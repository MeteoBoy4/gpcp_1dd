#!/usr/bin/env python

import argparse
import contextlib
import csv
import glob
import sys

import gpcp

def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('latitude', type=float)
    parser.add_argument('longitude', type=float)
    parser.add_argument('file', nargs="+")
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    if args.output is None:
        output = sys.stdout
    else: 
        output = open(args.output, 'w')

    writer = csv.writer(output)
    writer.writerow(('year', 'month', 'day', 'lat', 'lon', 'value'))
    
    for path in args.file:
        fp = open(path)
        with contextlib.closing(fp):
            data_file = gpcp.GPCPDataFile(fp)
            data_file.load_data()
            day_data = data_file.day_data
            for day in day_data:
                data = ((data_file.year, data_file.month,
                         day.day, lat, lon, value) 
                        for (lat, lon), value in day
                        if lat == args.latitude and lon == args.longitude)
                writer.writerows(data)
    output.close()

if __name__ == '__main__':
    main()

