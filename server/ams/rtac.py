#!/usr/bin/env python3
# -*- coding: utf-8; -*-
#
# Copyright (C) 2015-2016  DING Changchang (of Canaan Creative)
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


import threading
import queue
import copy

import ams.luci
from ams.sql import DataBase


def luciThread(node_queue, result_queue, commands, db):
    database = DataBase(db)
    database.connect()
    while True:
        try:
            node = node_queue.get(False)
        except:
            break

        result = database.run(
            'select',
            'controller_security',
            ['password', 'new_password'],
            "`ip` = %s",
            [node['ip']]
        )
        if not result or not result[0]:
            password = ''
            new_password = ''
        else:
            password = result[0][0] if result[0][0] is not None else ''
            new_password = (result[0][1] if result[0][1] is not None
                            else password)

        error = False
        for i in range(3):
            try:
                luci = ams.luci.LuCI(node['ip'], 80, password)
                if not luci.auth():
                    result = ['Login failed.']
                    error = True
                    continue
                result = []
                for c in commands:
                    if c['params'] is not None:
                        for i, param in enumerate(c['params']):
                            c['params'][i] = param.replace(
                                '`ip4`', node['ip'].split('.')[3]
                            )
                            c['params'][i] = param.replace(
                                '`password`', password
                            )
                            c['params'][i] = param.replace(
                                '`new_password`', new_password
                            )
                    result.append(luci.put(
                        c['lib'], c['method'], c['params'], i + 3
                    ))
                break
            except:
                error = True
                result = ['Error']
                continue
        result_queue.put({
            'node': node,
            'result': result,
            'error': error,
        })
        node_queue.task_done()
    database.disconnect()


def sshThread(node_queue, result_queue, commands, db):
    pass


def rtac(nodes, commands, method, db, result_queue):

    node_queue = queue.Queue()

    for node in nodes:
        node_queue.put(node)

    if method == 'ssh':
        target = sshThread
    elif method == 'luci':
        target = luciThread

    for i in range(min(len(nodes), 50)):
        t = threading.Thread(
            target=target,
            args=(node_queue, result_queue, copy.deepcopy(commands), db)
        )
        t.start()
    node_queue.join()

    result_queue.put("END")
