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
# along with AMS.  If not, see <http://www.gnu.org/licenses/>.

import logging
import threading
import queue

import mysql.connector


class Farm():
    def __init__(self, miner_info, farm_type):
        self.miner_list = []
        self.log = logging.getLogger('AMS.Farm')

        if farm_type == 'avalon4':
            import ams.avalon4 as miner_type
            from ams.avalon4 import Avalon4 as miner_class
        #
        # Add drivers here
        # e.g.
        #
        # elif farm_type == 'avalon3':
        #    import ams.avalon3 as miner_type
        #    from ams.avalon3 import Avalon3 as miner_class
        #
        else:
            self.log.critical('Miner Type Undefined.')
            exit()

        self.miner_type = miner_type
        self.miner_class = miner_class

        for miner in miner_info:
            ip = miner['ip']
            port = miner['port']
            module_list = miner['mods']

            self.miner_list.append(self.miner_class(ip, port, module_list))

    def db_init(self, db):
        self.db = db
        conn = mysql.connector.connect(
            host=db['host'],
            user=db['user'],
            password=db['password'],
            database=db['database']
        )
        cursor = conn.cursor()

        self.miner_type.db_init(conn, cursor)
        cursor.close()
        conn.close()

    def run(self, run_time, thread_num, retry):
        conn = mysql.connector.connect(
            host=self.db['host'],
            user=self.db['user'],
            password=self.db['password'],
            database=self.db['database']
        )
        cursor = conn.cursor()
        self.miner_type.db_init(conn, cursor, temp=True)

        miner_queue = queue.Queue()
        for miner in self.miner_list:
            miner_queue.put(miner)
        for i in range(thread_num):
            miner_thread = MinerThread(run_time, miner_queue, retry, self.db)
            miner_thread.daemon = True
            miner_thread.start()
        miner_queue.join()

        self.miner_type.db_final(conn, cursor)
        cursor.close()
        conn.close()


class Map():
    pass


class MinerThread(threading.Thread):
    def __init__(self, run_time, miner_queue, retry, db):
        threading.Thread.__init__(self)
        self.run_time = run_time
        self.miner_queue = miner_queue
        self.db = db
        self.retry = retry

    def run(self):
        while True:
            try:
                miner = self.miner_queue.get(False)
            except queue.Empty:
                break
            miner.run(self.run_time, self.retry, self.db)
            self.miner_queue.task_done()
