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

import ams.luci


def luciThread(node_queue, msg_queue, commands, db):
    while True:
        try:
            node = node_queue.get(False)
        except:
            break

        result = db.run(
            'select',
            'controller_config',
            ['password'],
            "`ip` = %s and `port` = %s",
            [node['ip'], node['port']]
        )
        password = result[0][0] if result[0][0] is not None else ''

        success = False
        for i in range(3):
            try:
                luci = ams.luci.LuCI(node['ip'], 80, password)
                luci.auth()
                result = []
                for c in commands:
                    c.replace('`ip4`', node['ip'].split('.')[3])
                    result.append(luci.put('uci', 'exec', [c]))
                success = True
                break
            except:
                continue
        if success:
            node_queue.task_done()
            msg_queue.push({
                'node': node,
                'msg': result,
            })
        else:
            node_queue.task_done()
            msg_queue.push({
                'node': node,
                'msg': ['Error'],
            })


def sshThread(node_queue, msg_queue, commands, db):
    pass


def rtac(nodes, commands, method, db):

    node_queue = queue.Queue()
    msg_queue = queue.Queue()

    for node in nodes:
        node_queue.put(node)

    if method == 'ssh':
        target = sshThread
    elif method == 'luci':
        target = luciThread

    for i in range(10):
        t = threading.Thread(
            target=target,
            args=(node_queue, msg_queue, commands, db)
        )
        t.start()
    node_queue.join()

    return [msg for msg in msg_queue.queue]
