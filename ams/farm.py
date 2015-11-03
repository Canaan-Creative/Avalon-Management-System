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

import logging
import threading
import queue


class Farm():
    def __init__(self, miner_info, farm_type):
        self.miner_list = []
        self.log = logging.getLogger('AMS.Farm')

        if farm_type == 'avalon4':
            import ams.avalon4 as miner_type
            from ams.avalon4 import Avalon4 as miner_class

        elif farm_type == 'avalon6':
            import ams.avalon6 as miner_type
            from ams.avalon6 import Avalon6 as miner_class
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
            module_num = miner['mods']

            self.miner_list.append(self.miner_class(ip, port, module_num))

    def db_init(self, sql_queue):
        self.miner_type.db_init(sql_queue)

    def run(self, run_time, sql_queue, retry, thread_num):
        self.miner_type.db_init(sql_queue.pre)
        sql_queue.pre.put("END")

        miner_queue = queue.Queue()
        for miner in self.miner_list:
            miner_queue.put(miner)
        for i in range(thread_num):
            miner_thread = MinerThread(
                run_time, sql_queue.main, retry, miner_queue
            )
            miner_thread.daemon = True
            miner_thread.start()
        miner_queue.join()
        sql_queue.main.put("END")

        self.miner_type.db_final(sql_queue.post)
        sql_queue.post.put("END")


class MinerThread(threading.Thread):
    def __init__(self, run_time, sql_queue, retry, miner_queue):
        threading.Thread.__init__(self)
        self.run_time = run_time
        self.miner_queue = miner_queue
        self.retry = retry
        self.sql_queue = sql_queue

    def run(self):
        while True:
            try:
                miner = self.miner_queue.get(False)
            except queue.Empty:
                break
            miner.run(self.run_time, self.sql_queue, self.retry)
            self.miner_queue.task_done()
