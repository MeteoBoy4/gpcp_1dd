#!/usr/bin/env python
"""
Header reader for GPCC 1DD data files.
"""

import sys

from gpcp import onedd


def main(args=sys.argv[1:]):
    """
    Parses argument, reads headers.
    """
    if len(args) != 1:
        print "USAGE: %s file_name" % sys.argv[0]
        return

    with open(args[0], 'rb') as fp:
        headers = onedd.read_onedd_headers(fp)

    for key, value in headers:
        print '%s = %s' % (key, value)

if __name__ == '__main__':
    main()
