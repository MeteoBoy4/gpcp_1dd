#!/usr/bin/env python
"""
Converts a GPCP 1DD file to delimited format
"""

import argparse
import contextlib
import csv
import sys

from gpcp import onedd


def main(args=sys.argv[1:]):
    """
    Reads arguments, writes date, latitude, longitude, precipitation
    to output
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout, metavar='OUTPUT',
                        help="Output (default: stdout)")
    parser.add_argument('-d', '--delimiter', default='\t',
                        metavar='DELIM',
                        help='Output delimiter (default: Tab)')
    parser.add_argument('files', nargs='+', metavar="FILE",
                        help='1DD file to read')

    parsed_args = parser.parse_args(args)

    with contextlib.closing(parsed_args.output):
        writer = csv.writer(parsed_args.output,
                            delimiter=parsed_args.delimiter)

        # Headers
        headers = ('date', 'latitude', 'longitude', 'precipitation')
        writer.writerow(headers)

        for infile in parsed_args.files:
            with open(infile, 'rb') as fp:
                reader = onedd.reader(fp)
                writer.writerows(reader.data_iter())

if __name__ == '__main__':
    main()
