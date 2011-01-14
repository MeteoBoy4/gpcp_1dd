#!/usr/bin/env python
"""
Tools for processing GPCP One-Degree Daily Precipitation Data Set

See:
ftp://rsd.gsfc.nasa.gov/pub/1dd-v1.1/1DD_v1.1_doc.pdf
"""

import csv
import datetime
import itertools
import re
import struct

# See GPCP file specification
HEADER_SIZE = 1440
GPCP_HEADER_PATTERN = r'(\w+)=(.*?) ?(?=(\w+=|$))'
GPCP_HEADER_RE = re.compile(GPCP_HEADER_PATTERN)

REAL_SIZE = 4
"""4-byte REALs"""

DAY_COUNT = 360 * 180
"""Number of values in day"""
DAY_SIZE = DAY_COUNT * REAL_SIZE
"""Size of a day in bytes"""

def read_onedd_headers(fp):
    """
    Loads headers from top HEADER_SIZE bytes of
    1dd data file.

    Returns list of name, value pairs.
    """
    # Read from beginning of file
    fp.seek(0)
    header = fp.read(HEADER_SIZE)

    # There's often unneeded trailing space
    header = header.rstrip()
    
    matches = GPCP_HEADER_RE.findall(header)
    return [match[:2] for match in matches]

def read_day(fp):
    """
    Reads a single day of data from an input file
    """
    # Read 1 day worth of data into a string - 
    # DAY_COUNT repeat of big-endian floats
    day_structure = ">" + ('f' * DAY_COUNT)
    assert struct.calcsize(day_structure) == DAY_SIZE

    day_str = fp.read(DAY_SIZE)
    return struct.unpack(day_structure, day_str)

class OneDegreeDay(object):
    """
    One day of GPCP data
    """

    def __init__(self, reader, day, readings):
        """
        Initializer 
        """
        self.reader = reader
        self.day = day
        self.date = datetime.datetime(reader.year, reader.month, day)
        self.readings = readings

    def __iter__(self):
        """
        Yields ((latitude, longitude), precipitation) tuples.
        """
        return itertools.izip(self.reader.coordinate_iterator(), self.readings)

    @staticmethod
    def from_file(reader, day, fp):
        """Creates a new day of data from input file-like object."""
        readings = read_day(fp)
        return OneDegreeDay(reader, day, readings)

class OneDegreeReader(object):
    """
    GPCP 1DD Data File Reader

    Exposes header information from file.
    """

    def __init__(self, fp):
        """
        Initializes OneDegreeReader from file-like object.
        """
        self.headers = dict(read_onedd_headers(fp))
        self._fp = fp
        self._days = None

    def __getitem__(self, key):
        """
        Gets a single day's data by 0-based index.
        """
        if not (key >= 0 and key < self.days):
            raise IndexError("Index out of range: " + str(key))

        day = key + 1

        # Seek to day
        seek_pos = HEADER_SIZE + (DAY_SIZE * key)

        self._fp.seek(seek_pos)
        return OneDegreeDay.from_file(self, day, self._fp)

    def __iter__(self):
        """
        Iterate over days in data set
        """
        self._fp.seek(HEADER_SIZE)
        for i in xrange(self.days):
            day = i + 1
            yield OneDegreeDay.from_file(self, day, self._fp)

    @property
    def days(self):
        """
        Returns number of days in data file, per header field.
        """
        if self._days is None:
            self._days = int(self.headers['days'].split('-')[1])
        return self._days

    @property
    def year(self):
        """
        Year covered by 1DD file
        """
        return int(self.headers['year'])

    @property
    def month(self):
        """
        Month covered by 1DD file.
        """
        return int(self.headers['month'])

    @property
    def missing_value(self):
        """
        Header value - magic number indicating missing value.
        """
        return float(self.headers['missing_value'])

    def close(self):
        """
        Closes the underlying file object.
        """
        self._fp.close()

    def coordinate_iterator(self):
        """
        Returns an iterator yielding ordered (latitude, longitude)
        pairs for a day.
        """
        # TODO: create iterator based on header values 1st_box_center,
        #       2nd_box_center and last_box_center  
        # Meanwhile, all in used datasets have values:
        # 1st_box_center = (89.5N,0.5E)
        # 2nd_box_center = (89.5N,1.5E)
        # last_box_center = (89.5S,359.5E)
        def coordinate_iterator_generator():
            for lat in xrange(180):
                for lon in xrange(360):
                    yield (89.5-lat, 0.5+lon)
        return coordinate_iterator_generator()

    def to_tsv(self, outf, headers=True):
        """
        Writes the month's data in tab-delimited format to
        provided file-like object, with optional headers.
        """
        writer = csv.writer(outf, delimiter="\t", lineterminator='\n')

        if headers:
            writer.writerow(('date', 'latitude', 'longitude', 
                             'precip_mm'))

        for day in self:
            for (lat, lon), precip in day:
                writer.writerow((day.date.strftime('%Y-%m-%d'), lat, lon, 
                                 precip))

def reader(fp):
    """
    Convenience function - returns an initialized reader.
    """
    return OneDegreeReader(fp)
