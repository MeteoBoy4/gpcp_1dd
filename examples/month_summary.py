#!/usr/bin/env python
"""
Summarizes a month's data into a single record per coordinate, with
mean precipitation, maxiumum, minimum, total, and sum.
"""

import argparse
import contextlib
import csv
import itertools
import math
import sys

from gpcp import onedd


def mean(x):
    """
    Returns the mean of an iterable.

    Example:
    >>> mean((1, 2, 3))
    2.0
    """
    return float(sum(x)) / len(x)


def sd(x):
    """
    Returns the standard deviation of an iterable
    """
    n = len(x)
    x_mean = mean(x)
    return math.sqrt(sum((i - x_mean) ** 2 for i in x) / (n - 1))


def summarize_coordinate(days, coordinate_index):
    """
    Summarizes the coordinate at index coordinate_index of each day in reader,
    returning a tuple with (mean, )
    """
    readings = []
    for day in days:
        readings.append(day.readings[coordinate_index])

    r_mean = mean(readings)
    r_min = min(readings)
    r_max = max(readings)
    r_sd = sd(readings)
    r_total = sum(readings)
    r_nreadings = len([i for i in readings if i is not None])

    return (r_nreadings, r_total, r_mean, r_sd, r_min, r_max)


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout, help="Output (default: stdout)")
    parser.add_argument('-d', '--delimiter', default='\t', metavar='DELIMITER',
                        help='Delimiter (default: Tab)')
    parser.add_argument('files', metavar='1DD_FILE', nargs='+')

    parsed_args = parser.parse_args(args)

    with contextlib.closing(parsed_args.output):
        writer = csv.writer(parsed_args.output,
                            delimiter=parsed_args.delimiter)
        writer.writerow(('year', 'month', 'latitude', 'longitude',
                         'reading_count', 'total', 'mean', 'sd',
                         'minimum', 'maximum'))
        for outfile in parsed_args.files:
            with open(outfile) as fp:
                reader = onedd.reader(fp)

                indices = xrange(onedd.MEASUREMENTS_PER_DAY)
                coordinates = reader.coordinate_iter()
                days = list(reader)

                for (i, (lat, lon)) in itertools.izip(indices, coordinates):
                    summary = summarize_coordinate(days, i)
                    row = [reader.year, reader.month, lat, lon]
                    row.extend(summary)

                    writer.writerow(row)

if __name__ == '__main__':
    main()
