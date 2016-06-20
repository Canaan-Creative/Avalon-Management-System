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
import base64
import os

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

        database.start_transaction()
        result = database.run(
            'select',
            'controller_security',
            ['password'],
            "`ip` = %s FOR UPDATE",
            [node['ip']]
        )
        if not result or not result[0]:
            password = ''
        else:
            password = result[0][0] if result[0][0] is not None else ''

        error = False
        auth = True
        for i in range(3):
            j = 0
            try:
                luci = ams.luci.LuCI(node['ip'], 80, password)
                if not luci.auth():
                    luci = ams.luci.LuCI(node['ip'], 80, '')
                if not luci.auth():
                    auth = False
                    error = True
                    break
                auth = True
                database.commit()
                result = []
                for c in commands[j:]:
                    if c['params'] is not None:
                        for i, param in enumerate(c['params']):
                            c['params'][i] = param.replace(
                                '`ip4`', node['ip'].split('.')[3]
                            )
                    if c['method'] == 'user.setpasswd':
                        new_password = base64.b64encode(os.urandom(9)).decode()
                        c['params'] = [new_password]
                        database.start_transaction()
                        result = database.run(
                            'select',
                            'controller_security',
                            ['password'],
                            "`ip` = %s FOR UPDATE",
                            [node['ip']]
                        )

                    r = luci.put(c['lib'], c['method'], c['params'], i + 10)

                    if c['method'] == 'user.setpasswd':
                        if r['error'] is None:
                            database.run(
                                'raw',
                                '''\
UPDATE controller_security
   SET password = %s
 WHERE ip = %s''',
                                [node['ip'], new_password])
                        database.commit()

                    result.append(r)

                    j += 1
                error = False
                break
            except:
                error = True
                continue

        if not auth:
            result.append({'result': 'Authentication Failed'})
        elif error:
            result.append({'result': 'Connection Failed'})
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
