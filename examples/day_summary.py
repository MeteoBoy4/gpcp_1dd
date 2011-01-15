#!/usr/bin/env python

import math
import sys

import onedd


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
    return math.sqrt(sum((i - x_mean)**2 for i in x) / (n - 1))

def main(args=sys.argv[1:]):
    if len(args) != 1:
        print 'USAGE: %s 1DD_FILE' % sys.argv[0]
        return

    with open(sys.argv[1]) as fp:
        reader = onedd.reader(fp)
        print '%10s %8s %8s' % ('date', 'mean', 'sd')

        for day in reader:
            day_mean = mean(day.readings)
            day_sd = sd(day.readings)
            print '%10s %8.2f %8.2f' % (day.date.strftime('%Y-%m-%d'),
                                        day_mean, day_sd)


if __name__ == '__main__':
    main()
