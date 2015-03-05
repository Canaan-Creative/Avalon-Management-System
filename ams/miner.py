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

import socket
import queue
import threading
import json
import logging

import mysql.connector


class Miner():

    name = 'Miner'

    def __init__(self, ip, port, module_list):
        self.ip = ip
        self.port = port
        self.module_list = module_list
        self.log = logging.getLogger('AMS.Miner')

    def __str__(self):
        ip = '[{}]'.format(self.ip) if ':' in self.ip else self.ip
        return '{}|{}:{}'.format(self.name, ip, self.port)

    def _collect(self, retry):
        # TODO: add ping test
        for command in ['summary', 'edevs', 'estats', 'pools']:
            for timeout in range(1, retry + 1):
                try:
                    response = self.put(command, timeout=timeout)
                    break
                except socket.error:
                    response = None
                    if timeout == retry:
                        self.log.error('{} Failed fetching {}.'
                                       .format(self, command))
                    else:
                        self.log.debug('{} Failed fetching {}. Retry {}'
                                       .format(self, command, timeout))
            self.raw[command] = response
        return True

    def _generate_sql_summary(self, run_time):
        pass

    def _generate_sql_edevs(self, run_time):
        pass

    def _generate_sql_estats(self, run_time):
        pass

    def _generate_sql_pools(self, run_time):
        pass

    def run(self, run_time, retry, db):
        self.raw = {}
        self.sql_queue = queue.Queue()
        self._collect(retry)
        self._generate_sql_summary(run_time)
        self._generate_sql_edevs(run_time)
        self._generate_sql_estats(run_time)
        self._generate_sql_pools(run_time)
        host = db['host']
        database = db['database']
        user = db['user']
        password = db['password']
        thread_num = db['thread_num']
        for i in range(thread_num):
            store_thread = SQLThread(
                self.sql_queue,
                host,
                database,
                user,
                password
            )
            store_thread.daemon = True
            store_thread.start()
        self.sql_queue.join()

    def put(self, command, parameter=None, timeout=3):
        if parameter is None:
            request = '{{"command": "{}"}}'.format(command)
        else:
            request = '{{"command": "{}", "parameter": "{}"}}'.format(
                command, parameter)

        for res in socket.getaddrinfo(
                self.ip,
                self.port,
                socket.AF_UNSPEC,
                socket.SOCK_STREAM):

            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error:
                self.log.debug('{} Error in fetching {}: socket init.'
                               .format(self, command))
                s = None
                continue
            s.settimeout(timeout)
            try:
                s.connect(sa)
            except socket.error:
                self.log.debug('{} Error in fetching {}: socket connect.'
                               .format(self, command))
                s.close()
                s = None
                continue
            break
        if s is None:
            raise socket.error
        s.sendall(request.encode())
        response = s.recv(4096)
        while True:
            recv = s.recv(4096)
            if not recv:
                break
            else:
                response += recv
        return json.loads(response.decode().replace('\x00', ''))


class SQLThread(threading.Thread):
    def __init__(self, sql_queue, host, database, user, password):
        threading.Thread.__init__(self)
        self.sql_queue = sql_queue
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.log = logging.getLogger('AMS.SQLThread')

    def run(self):
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = conn.cursor()
        while True:
            try:
                sql = self.sql_queue.get(False)
            except queue.Empty:
                break
            insert_table(conn, cursor, sql['name'], sql['column'], sql['value'])
            self.sql_queue.task_done()
        cursor.close()
        conn.close()


def create_table(conn, cursor, name, column, additional=None, suffix=None):
    query = 'CREATE TABLE IF NOT EXISTS `{}` ({}{}) {}'.format(
        name,
        ', '.join('`{name}` {type}'.format(**c) for c in column),
        ', {}'.format(additional) if additional else '',
        suffix if suffix else ''
    )
    try:
        cursor.execute(query)
    except mysql.connector.Error as e:
        log = logging.getLogger('AMS.SQL')
        log.error(e.msg)
        log.debug(query)

        cursor.close()
        conn.close()
        exit()
    conn.commit()


def insert_table(conn, cursor, name, column, value):
    query = 'INSERT INTO `{}` (`{}`) VALUES ({})'.format(
        name,
        '`, `'.join(column),
        ', '.join('%s' for i in range(len(value)))
    )
    try:
        cursor.execute(query, value)
    except mysql.connector.Error as e:
        log = logging.getLogger('AMS.SQL')
        log.error(e.msg)
        log.debug(query)
        log.debug(value)
        return
    conn.commit()


def db_init(conn, cursor):
    data_summary = [
        {'name': 'time',
            'type': 'TIMESTAMP'},
        {'name': 'ip',
            'type': 'VARCHAR(40)'},
        {'name': 'port',
            'type': 'SMALLINT UNSIGNED'},
        {'name': 'precise_time',
            'type': 'TIMESTAMP'},
        {'name': 'elapsed',
            'type': 'BIGINT'},
        {'name': 'mhs_av',
            'type': 'DOUBLE'},
        {'name': 'mhs_5s',
            'type': 'DOUBLE'},
        {'name': 'mhs_1m',
            'type': 'DOUBLE'},
        {'name': 'mhs_5m',
            'type': 'DOUBLE'},
        {'name': 'mhs_15m',
            'type': 'DOUBLE'},
        {'name': 'found_blocks',
            'type': 'INT UNSIGNED'},
        {'name': 'getworks',
            'type': 'BIGINT'},
        {'name': 'accepted',
            'type': 'BIGINT'},
        {'name': 'rejected',
            'type': 'BIGINT'},
        {'name': 'hardware_errors',
            'type': 'INT'},
        {'name': 'utility',
            'type': 'DOUBLE'},
        {'name': 'discarded',
            'type': 'BIGINT'},
        {'name': 'stale',
            'type': 'BIGINT'},
        {'name': 'get_failures',
            'type': 'INT UNSIGNED'},
        {'name': 'local_work',
            'type': 'INT UNSIGNED'},
        {'name': 'remote_failures',
            'type': 'INT UNSIGNED'},
        {'name': 'network_blocks',
            'type': 'INT UNSIGNED'},
        {'name': 'total_mh',
            'type': 'DOUBLE'},
        {'name': 'work_utility',
            'type': 'DOUBLE'},
        {'name': 'difficulty_accepted',
            'type': 'DOUBLE'},
        {'name': 'difficulty_rejected',
            'type': 'DOUBLE'},
        {'name': 'difficulty_stale',
            'type': 'DOUBLE'},
        {'name': 'best_share',
            'type': 'BIGINT UNSIGNED'},
        {'name': 'device_hardware',
            'type': 'DOUBLE'},
        {'name': 'device_rejected',
            'type': 'DOUBLE'},
        {'name': 'pool_rejected',
            'type': 'DOUBLE'},
        {'name': 'pool_stale',
            'type': 'DOUBLE'},
        {'name': 'last_getwork',
            'type': 'TIMESTAMP'}
    ]
    data_pools = [
        {'name': 'time',
            'type': 'TIMESTAMP'},
        {'name': 'ip',
            'type': 'VARCHAR(40)'},
        {'name': 'port',
            'type': 'SMALLINT UNSIGNED'},
        {'name': 'precise_time',
            'type': 'TIMESTAMP'},
        {'name': 'pool_id',
            'type': 'TINYINT UNSIGNED'},
        {'name': 'pool',
            'type': 'INT'},
        {'name': 'url',
            'type': 'VARCHAR(64)'},
        {'name': 'status',
            'type': 'CHAR(1)'},
        {'name': 'priority',
            'type': 'INT'},
        {'name': 'quota',
            'type': 'INT'},
        {'name': 'long_poll',
            'type': 'CHAR(1)'},
        {'name': 'getworks',
            'type': 'INT UNSIGNED'},
        {'name': 'accepted',
            'type': 'BIGINT'},
        {'name': 'rejected',
            'type': 'BIGINT'},
        {'name': 'works',
            'type': 'INT'},
        {'name': 'discarded',
            'type': 'INT UNSIGNED'},
        {'name': 'stale',
            'type': 'INT UNSIGNED'},
        {'name': 'get_failures',
            'type': 'INT UNSIGNED'},
        {'name': 'remote_failures',
            'type': 'INT UNSIGNED'},
        {'name': 'user',
            'type': 'VARCHAR(32)'},
        {'name': 'last_share_time',
            'type': 'TIMESTAMP'},
        {'name': 'diff1_shares',
            'type': 'BIGINT'},
        {'name': 'proxy_type',
            'type': 'VARCHAR(32)'},
        {'name': 'proxy',
            'type': 'VARCHAR(64)'},
        {'name': 'difficulty_accepted',
            'type': 'DOUBLE'},
        {'name': 'difficulty_rejected',
            'type': 'DOUBLE'},
        {'name': 'difficulty_stale',
            'type': 'DOUBLE'},
        {'name': 'last_share_difficulty',
            'type': 'DOUBLE'},
        {'name': 'has_stratum',
            'type': 'BOOL'},
        {'name': 'stratum_active',
            'type': 'BOOL'},
        {'name': 'stratum_url',
            'type': 'BIGINT'},
        {'name': 'has_gbt',
            'type': 'BOOL'},
        {'name': 'best_share',
            'type': 'BIGINT UNSIGNED'},
        {'name': 'pool_rejected',
            'type': 'DOUBLE'},
        {'name': 'pool_stale',
            'type': 'DOUBLE'}
    ]

    create_table(
        conn, cursor, 'miner', data_summary,
        'PRIMARY KEY(`time`, `ip`, `port`)'
    )
    create_table(
        conn, cursor, 'pool', data_pools,
        'PRIMARY KEY(`time`, `ip`, `port`, `pool_id`)'
    )
