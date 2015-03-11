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

from ams.farm import Farm
from ams.log import log
from ams.pool import update_poolrate


def main():
    miners = []
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

    now = datetime.datetime.now()
    update_poolrate(pool_list, now, db, retry=3)


if __name__ == '__main__':
    log()
    main()
