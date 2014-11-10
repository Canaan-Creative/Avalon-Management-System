#!/usr/bin/env python2

from __future__ import print_function
import datetime
import argparse

from collect import collect
from analyze import analyze
from configurate import configurate
from poolrate import poolrate
from plot import hashrate
from plot import heatmap
from report import sendMail
from balance import balance

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="AMS.")
    parser.add_argument('-m', '--email', dest="time", nargs='?',
                        help="send email [with the fetching time]",
                        const='now')
    args = parser.parse_args()
    cfg = configurate('../etc/ams.conf')
    if (not args.time) or args.time == 'now':
        now = datetime.datetime.now()
        now_s = '{:%Y_%m_%d_%H_%M}'.format(now)
        dataQueue = collect(now, cfg)
        analyze(dataQueue, now_s, cfg)
        poolrate(now_s, cfg)
    else:
        now_s = args.time
        now = datetime.datetime.strptime(now_s, '%Y_%m_%d_%H_%M')
    if args.time is not None:
        cfg['Email']['hsimg'] = hashrate(now, cfg)
        cfg['Email']['tmimg'] = heatmap(now, cfg)
        cfg['Email']['balance'] = balance(cfg)
        sendMail(now, cfg)
