#!/usr/bin/env python

import sys
import gpcp

def main(args=sys.argv[1:]):
    if len(args) != 1:
        print "USAGE: %s file_name" % sys.argv[0]
        return

    fp = open(args[0])
    try:
        headers = gpcp.get_gpcp_headers(fp)
    finally:
        fp.close()

    for key, value in headers:
        print '%s = %s' % (key, value)

if __name__ == '__main__':
    main()
