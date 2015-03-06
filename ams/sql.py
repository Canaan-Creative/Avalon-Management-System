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

import threading
import logging
import queue

import mysql.connector


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
        miner_sql = SQL(conn, cursor)

        while True:
            try:
                sql_raw = self.sql_queue.get(False)
            except queue.Empty:
                break

            if sql_raw['command'] == 'insert':
                miner_sql.run(
                    'insert',
                    sql_raw['name'],
                    sql_raw['column'],
                    sql_raw['value']
                )

            self.sql_queue.task_done()
        cursor.close()
        conn.close()


class SQL():
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.log = logging.getLogger('AMS.SQL')

    def _create(self, name, column_def, additional=None, suffix=None):
        self.query = 'CREATE TABLE IF NOT EXISTS `{}` ({}{}) {}'.format(
            name,
            ', '.join('`{name}` {type}'.format(**c) for c in column_def),
            ', {}'.format(additional) if additional else '',
            suffix if suffix else ''
        )
        self.value = None

    def _insert(self, name, column, value):
        self.query = 'INSERT INTO `{}` (`{}`) VALUES ({})'.format(
            name,
            '`, `'.join(column),
            ', '.join('%s' for i in range(len(value)))
        )
        self.value = value

    def _select(self, name, column, clause):
        self.query = 'SELECT `{}` FROM `{}` WHRER {}'.format(
            '`, `'.join(column),
            name,
            clause
        )
        self.value = None

    def run(self, command, *args, **kwargs):
        if command == 'create':
            self._create(*args, **kwargs)
        elif command == 'insert':
            self._insert(*args, **kwargs)
        elif command == 'select':
            self._select(*args, **kwargs)
        else:
            self.log.error('Unknown sql command: {}'.format(command))
            return False

        try:
            self.cursor.execute(self.query, self.value)
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            self.log.error(e.msg)
            self.log.debug(self.query)
            if self.value is not None:
                self.log.debug(self.value)
            return False
