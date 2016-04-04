#!/usr/bin/env python
"""
Tools for processing GPCP One-Degree Daily Precipitation data files

See:
ftp://rsd.gsfc.nasa.gov/pub/1dd-v1.1/1DD_v1.1_doc.pdf
"""

import collections
import csv
import datetime
import itertools
import re
import struct

import numpy as np
import numpy.ma as ma

from netCDF4 import Dataset
import netCDF4

# See GPCP 1DD file specification for more details
HEADER_SIZE = 1440
GPCP_HEADER_PATTERN = r'(\w+)=(.*?) ?(?=(\w+=|$))'
GPCP_HEADER_RE = re.compile(GPCP_HEADER_PATTERN)

# Data file contains 4-byte Reals
REAL_SIZE = 4

# Number of values in a day 360 degrees of longitude x 180 degrees of latitude.
MEASUREMENTS_PER_DAY = 360 * 180

# Size of a day in bytes
DAY_SIZE = MEASUREMENTS_PER_DAY * REAL_SIZE


def read_onedd_headers(fp):
    """
    Loads headers from top HEADER_SIZE bytes of
    1dd data file.

    Returns list of (name, value) pairs.
    """
    # Read from beginning of file
    fp.seek(0)
    header = fp.read(HEADER_SIZE)

    # There's often unneeded trailing space
    header = header.rstrip()

    matches = GPCP_HEADER_RE.findall(header)
    headers = [match[:2] for match in matches]
    if not headers:
        raise IOError("No headers found. Is this a 1DD file?")

    return headers


def read_day(fp):
    """
    Reads a single day of data from an input file.

    Returns a two-dimensional numpy array. Missing values (magic number defined in header)
    are left intact.
    """
    # Read 1 day worth of data into a string -
    # MEASUREMENTS_PER_DAY repeat of big-endian floats
    day_structure = ">" + ('f' * MEASUREMENTS_PER_DAY)
    assert struct.calcsize(day_structure) == DAY_SIZE

    day_str = fp.read(DAY_SIZE)
    _tuple=struct.unpack(day_structure, day_str)
    day_arr=np.array(_tuple)
    return day_arr.reshape(180,360)


class OneDegreeReader(object):
    """
    GPCP 1DD Data File Reader

    Exposes header information from file, provides
    iteration over each day of data in file, as well as
    all precipitation measurements.
    """

    def __init__(self, fp):
        """
        Initializes OneDegreeReader from file-like object.
        """
        self.headers = dict(read_onedd_headers(fp))
        self._fp = fp
        self._days = None

        # Verify we have a valid file
        self._check_headers()

    def reading(self):
        """Read from the file's current position, return a numpy masked array using the fill_value in header."""

        _readings=read_day(self._fp)
	masked=ma.masked_values(_readings,self.missing_value)
	return masked

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
        return self.reading() 

    def __iter__(self):
        """
        Iterate over days in data set.

        Resets file position, yields single day global data.
        """

        self._fp.seek(HEADER_SIZE)
        for i in xrange(self.days):
            day = i + 1
            yield self.reading()

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

    def to_netcdf(self,name):
	"""
	Create the netCDF file corresponding to the whold month's data.

	Attributes and vaiables are handled.
	
	The name of the output file should be given as string.
	"""
        _cdf=NetcdfCreator(self,name)
	_cdf.commander()

    def _check_headers(self):
        """
        Checks the headers of the current object to verify file type.
        """
        for header in ('year', 'month', 'days'):
            if not header in self.headers:
                raise KeyError(("Expected header %s not present. " % header) +
                               "Is this a 1DD file?")

class NetcdfCreator(object):
    """
    GPCP netCDF file creator.

    Create the netcdf file coorsponding to the whole month's data.
    """

    def __init__(self,reader,name):
	"""Initialize the creator."""
	self.reader=reader
	self._name=name

    def creator(self):
	"""Create the file."""
        self._thefile=Dataset(self._name+".nc","w",format="NETCDF3_CLASSIC")

    def dimension_creator(self):
	"""Create the dimensions."""
	self.time=self._thefile.createDimension("time",self.reader.days)
	self.lat =self._thefile.createDimension("lat",180)
	self.lon =self._thefile.createDimension("lon",360)

    def variable_creator(self):
	"""Create variables."""
	self.times=self._thefile.createVariable("time","f8",("time",))
	self.latitudes=self._thefile.createVariable("lat","f4",("lat",))
	self.longitudes=self._thefile.createVariable("lon","f4",("lon",))
	self.precip=self._thefile.createVariable("PREC","f4",("time","lat","lon"),fill_value=self.reader.missing_value)

    def attributes_creator(self):
	"""Create the variable attributes."""
	self.latitudes.units="degrees_north"
	self.latitudes.long_name="latitude"
	self.longitudes.units="degrees_east"
	self.longitudes.long_name="longitude"
	self.precip.units="mm/day"
	self.precip.missingvalue=self.reader.missing_value
	self.times.units="hours since 1990-01-01 00:00:00.0"
	self.times.calendar="gregorian"
	self.times.long_name="time"

    def history_creator(self):
	"""Create the global attribute: history."""
	time_stamp=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
	self._thefile.history=time_stamp

    def coordinate_writer(self):
	"""Fill in the coordinate variable."""
        lats=np.arange(89.5,-90.5,-1.)
	lons=np.arange(0.5,360.5,1.)
	self.latitudes[:]=lats
	self.longitudes[:]=lons

    def time_coordinate(self):
	"""Fill in the right time coordinate."""
	dates=[datetime.datetime(self.reader.year,self.reader.month,1)+n*datetime.timedelta(hours=24) for n in range(
		self.reader.days)]
	self.times[:]=netCDF4.date2num(dates,units=self.times.units,calendar=self.times.calendar)

    def variable_writer(self):
	"""Fill in the preciptation data."""
	self.precip[:,:,:]=np.array(list(self.reader)).reshape(self.reader.days,180,360)

    def close(self):
	"""Close the file."""
        self._thefile.close()

    def commander(self):
	"""Do the whole series of things to create the complete netCDF file."""
	self.creator()
	self.dimension_creator()
	self.variable_creator()
	self.attributes_creator()
	self.history_creator()
	self.coordinate_writer()
	self.time_coordinate()
	self.variable_writer()
	self.close()

def reader(fp):
    """
    Convenience function - returns an initialized reader.
    """
    return OneDegreeReader(fp)
