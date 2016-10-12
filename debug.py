#!/usr/bin/env python2

import re
import sys
import json

from cgminer_api import cgminer_api

def debug(ip):
    js = cgminer_api(ip, 4028, ['estats'])
    print json.dumps(js)

if __name__ == '__main__':
    ip = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 4028
    cgminer_api(ip, port, ['debug', 'D'])
    debug(ip)
    cgminer_api(ip, port, ['debug', 'D'])
