#!/usr/bin/env python2

import json
import re
import sys

from cgminer_api import cgminer_api

pattern = re.compile(r'.*MDH5m\[(?P<dh>[^\]]+)\].*MVol\[(?P<vol>[^]]+)\].*')

def debug(ip):
    global pattern
    js = cgminer_api(ip, 4028, ['estats'])
    for estat in sorted(js['STATS'], key=lambda k: k['STATS']):
        for mm in sorted(estat):
            if mm[:5] == 'MM ID' and re.match(pattern, estat[mm]) is not None:
                g = re.match(pattern, estat[mm]).groupdict()
                print '[{:>13}][{:>2}][{:>2}]\tMDH5m[{}]\tMVol[{}]'.format(
                    ip, estat['ID'][3:], mm[5:], g['dh'], g['vol'])


if __name__ == '__main__':
    ip = sys.argv[1]
    cgminer_api(ip, 4028, ['debug', 'D'])
    debug(ip)
    cgminer_api(ip, 4028, ['debug', 'D'])
