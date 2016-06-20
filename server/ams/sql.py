# -*- coding: utf-8; -*-
#
# Copyright (C) 2014-2016  DING Changchang (of Canaan Creative)
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
import logging
import time
from multiprocessing import Queue

import mysql.connector


class SQLThread(threading.Thread):
    def __init__(self, sql_queue, db):
        threading.Thread.__init__(self)
        self.sql_queue = sql_queue
        self.db = DataBase(db)
        self.log = logging.getLogger('AMS.SQLThread')

    def run(self):
        retry = 0
        while retry < 3:
            try:
                self.db.connect()
                break
            except mysql.connector.Error as e:
                self.log.error(str(e))
                time.sleep(2)
                retry += 1

        if retry == 3:
            return

        while True:
            sql_raw = self.sql_queue.get()
            if sql_raw == "END":
                self.sql_queue.put("END")
                break
            self.db.run(**sql_raw)
            self.db.commit()

        self.db.disconnect()


class DataBase():
    def __init__(self, db):
        self.host = db['host']
        self.database = db['database']
        self.user = db['user']
        self.password = db['password']
        self.conn = None
        self.log = logging.getLogger('AMS.DataBase')

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()

    def start_transaction(self):
        self.conn.start_transaction()

    def commit(self):
        self.conn.commit()

    def disconnect(self):
        self.cursor.close()
        self.conn.close()

    def _create(self, name, column_def, additional=None, suffix=None):
        self.query = 'CREATE TABLE IF NOT EXISTS `{}` ({}{}){}'.format(
            name,
            ', '.join('`{name}` {type}'.format(**c) for c in column_def),
            ', {}'.format(additional) if additional else '',
            ' {}'.format(suffix) if suffix else ''
        )
        self.value = None

    def _insert(self, name, column, value):
        self.query = 'INSERT INTO `{}` (`{}`) VALUES ({})'.format(
            name,
            '`, `'.join(column),
            ', '.join('%s' for i in range(len(value)))
        )
        self.value = value

    def _select(self, name, column=None, clause=None, value=None):
        self.query = 'SELECT {} FROM `{}`{}'.format(
            '`{}`'.format('`, `'.join(column)) if column else '*',
            name,
            ' WHERE {}'.format(clause) if clause else ''
        )
        self.value = value

    def _raw(self, query, value=None):
        self.query = query
        self.value = value

    def run(self, command, *args, **kwargs):
        if command == 'create':
            self._create(*args, **kwargs)
        elif command == 'insert':
            self._insert(*args, **kwargs)
        elif command == 'select':
            self._select(*args, **kwargs)
        elif command == 'raw':
            self._raw(*args, **kwargs)
        else:
            self.log.error('Unknown sql command: {}'.format(command))
            return False

        try:
            self.cursor.execute(self.query, self.value)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as e:
            if 'No result set to fetch from.' in str(e):
                return True
            self.log.error(str(e))
            self.log.debug(self.query)
            if self.value is not None:
                self.log.debug(self.value)
            return False


class SQLQueue():
    def __init__(self):
        self.pre = Queue()
        self.post = Queue()
        self.main = Queue()


def sql_handler(sql_queue, db, thread_num):

    t = SQLThread(sql_queue.pre, db)
    t.start()
    t.join()

    threads = []
    for i in range(thread_num):
        t = SQLThread(sql_queue.main, db)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    t = SQLThread(sql_queue.post, db)
    t.start()
    t.join()
