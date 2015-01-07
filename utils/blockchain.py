#!/usr/bin/env python3

import urllib.request
import urllib.error
import socke
import json


def blockchain(addr):
    result = []
    url = "https://blockchain.info/address/{}?format=json&limit=50".format(addr)
    offset = 0
    while True:
        try:
            res = urllib.request.urlopen("{}&offset={}".format(url, offset),
                                         timeout=10).read()
        except (urllib.error.URLError, socket.timeout):
            print("Timeout {} offset{}".format(addr, offset))
            continue

        try:
            transaction = json.loads(res.decode())['txs']
        except TypeError as err:
            print("Corrupted {} offset{}".format(addr, offset))
            print(err)
            print(res)
            continue

        for tx in transaction:
            for out in tx['out']:
                if out['addr'] == addr:
                    result.append([int(tx['time']), int(out['value'])])
                    break

        print("Done {} offset{}".format(addr, offset))
        offset += 50

        if len(transaction) < 50:
            break

    return result


def main():
    delta = []
    for addr in ['1XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                 '1YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
                 '1ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ']:
        delta += blockchain(addr)

    delta = sorted(delta, key=lambda d: d[0])

    balance = []
    b = 0
    for d in delta:
        b += d[1]
        balance.append([d[0] * 1000, b / 100000000])

    print("-----------------")
    print(delta)
    print("-----------------")
    print(balance)


if __name__ == '__main__':
    main()
