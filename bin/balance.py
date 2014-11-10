#!/usr/bin/env python2

from __future__ import print_function
import urllib2
import json
import sys


def balance(cfg):
    bl = []
    print("Fetching Balance Data:")
    address = list(filter(None, (x.strip() for x in
                                 cfg['Balance']['address'].splitlines())))
    note = list(filter(None, (x.strip() for x in
                              cfg['Balance']['note'].splitlines())))
    for i in xrange(len(address)):
        addr = address[i]
        print(addr, end="... ")
        sys.stdout.flush()
        url = ("http://blockchain.info/address/{}?"
               "format=json&limit=0").format(addr)

        try:
            res = urllib2.urlopen(url, timeout=10).read()
            bl.append(json.loads(res))
            bl[-1]['final_balance'] /= 1.0e8
        except:
            bl.append({'address': addr,
                       'final_balance': 'Connection Failed'})
        try:
            bl[-1]['note'] = note[i]
        except:
            bl[-1]['note'] = ''
        print("Done.")
    return bl
