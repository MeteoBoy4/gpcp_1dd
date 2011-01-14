#!/usr/bin/env python
"""
Simple utility to read GPCP 1DD file, outputting measurements
for provided coordinates.
"""

import argparse
import contextlib
import csv
import glob
import sys

import onedd

def main(args=sys.argv[1:]):
    """
    Parses arguments, reads file(s), prints results to output
    """
    parser = argparse.ArgumentParser(description="""GPCP 1DD Extraction utility -
filters the file(s) specified by the provided coordinates.""")
    parser.add_argument('latitude', type=float)
    parser.add_argument('longitude', type=float)
    parser.add_argument('file', nargs="+")
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help="Output file (default: stdout)")

    args = parser.parse_args()

    writer = csv.writer(args.output)
    writer.writerow(('year', 'month', 'day', 'lat', 'lon', 'value'))
    with contextlib.closing(args.output):
        for path in args.file:
            fp = open(path)
            with contextlib.closing(fp):
                data_file = onedd.reader(fp)
                data = (i for i in data_file.data_iter()
                        if i[1] == args.latitude and i[2] == args.longitude)
                writer.writerows(data)

if __name__ == '__main__':
    main()

