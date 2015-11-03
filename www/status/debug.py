#!/usr/bin/env python2

import re
import sys

from cgminer_api import cgminer_api

pattern = re.compile(r'.*DNA\[(?P<dna>[^\]]+)\].*GHSmm\[(?P<ghs>[^]]+)\].*Freq\[(?P<freq>[^\]]+)\].*PLL\[(?P<pll>[^\]]+)\].*')


def debug(ip):
    global pattern
    js = cgminer_api(ip, 4028, ['estats'])
    for estat in sorted(js['STATS'], key=lambda k: k['STATS']):
        for mm in sorted(estat):
            if mm[:5] == 'MM ID' and re.match(pattern, estat[mm]) is not None:
                g = re.match(pattern, estat[mm]).groupdict()
                print '[{:>13}][{:>2}][{:>2}]\tDNA[{}]\tGHsmm[{}]]\tFreq[{}]\tPLL[{}]'.format(
                    ip, estat['ID'][3:], mm[5:], g['dna'], g['ghs'], g['freq'], g['pll'])


if __name__ == '__main__':
    ip = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 4028
    cgminer_api(ip, port, ['debug', 'D'])
    debug(ip)
    cgminer_api(ip, port, ['debug', 'D'])
