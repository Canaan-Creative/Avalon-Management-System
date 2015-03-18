#!/usr/bin/env python3
# -*- coding: utf-8; -*-
#
# Copyright (C) 2014-2015  DING Changchang
#
# This file is part of Avalon Management System (AMS).
#
# AMS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AMS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AMS. If not, see <http://www.gnu.org/licenses/>.

import datetime
from multiprocessing import Process

from ams.farm import Farm
from ams.log import log
from ams.pool import update_poolrate


def main():
    miners = []
    miners.append({'ip': '192.168.1.21', 'port': 4028, 'mods': [5, 5]})
    miners.append({'ip': '192.168.1.22', 'port': 4028, 'mods': [5, 5]})
    miners.append({'ip': '192.168.1.23', 'port': 4028, 'mods': [5, 5]})
    miners.append({'ip': '192.168.1.24', 'port': 4028, 'mods': [5, 5]})
    miners.append({'ip': '192.168.1.25', 'port': 4028, 'mods': [4, 4]})
    myFarm = Farm(miners, 'avalon4')

    db = {'host': '127.0.0.1',
          'database': 'ams_ng',
          'user': 'ams',
          'password': 'ams',
          'thread_num': 50}
    myFarm.db_init(db)

    pool_list = [
        {
            'name': 'kano',
            'user': '__USER_1__',
            'worker': '__WORKER_1__',
            'api_key': '__API_KEY_1__'
        },
        {
            'name': 'btcchina',
            'user': '__USER_2__',
            'worker': '__WORKER_2__',
            'api_key': '__API_KEY_2__'
        },
        {
            'name': 'ghash',
            'user': '__USER_3__',
            'worker': '__WORKER_3__',
            'api_key': '__API_KEY_3__',
            'api_secret_key': '__API_SECRET_KEY_3__'
        }
    ]

    now = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

    farm_process = Process(
        target=myFarm.run,
        args=(now, 100, 5)
    )
    pool_process = Process(
        target=update_poolrate,
        args=(pool_list, now, db, 3)
    )
    farm_process.start()
    pool_process.start()
    farm_process.join()
    pool_process.join()


if __name__ == '__main__':
    log()
    main()
