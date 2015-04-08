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

import json
import urllib.parse
import urllib.request
from urllib.error import URLError
import hashlib
import hmac
import time
import logging
import threading
import queue

import mysql.connector

import ams.sql as sql


class Pool():
    name = "pool"

    def __init__(self, user, worker, api_key, api_secret_key=None):
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.user = user
        self.worker = worker
        self.fullname = '{}.{}'.format(user, worker)
        self.log = logging.getLogger('AMS.Pool')

    def _collect(self):
        pass

    def run(self, retry):
        for r in range(retry):
            try:
                result = self._collect()
            except (URLError, TypeError, ValueError, KeyError) as e:
                if r == retry - 1:
                    self.log.error('[{}] Failed fetching. {}'.
                                   format(self.name, e))
                    return None
                else:
                    self.log.debug('[{}] Failed fetching. Retry {}. {}'.
                                   format(self.name, r, e))
                    continue
            break
        return result


class ghash(Pool):
    name = "ghash.io"

    def _collect(self):
        url = 'https://cex.io/api/ghash.io/workers'
        nonce = '{:.0f}'.format(time.time()*1000)
        signature = hmac.new(
            self.api_secret_key.encode(),
            msg='{}{}{}'.format(nonce, self.user, self.api_key).encode(),
            digestmod=hashlib.sha256
        ).hexdigest().upper()
        post_content = {
            'key': self.api_key,
            'signature': signature,
            'nonce': nonce
        }
        param = urllib.parse.urlencode(post_content).encode()
        request = urllib.request.Request(
            url,
            param,
            {'User-agent': 'bot-cex.io-{}'.format(self.user)}
        )
        data = json.loads(urllib.request.urlopen(request).read().decode())

        return float(data[self.fullname]['last1h'])


class ozcoin(Pool):
    name = "ozco.in"

    def _collect(self):
        url = 'http://ozco.in/api.php?api_key={}'.format(self.api_key)
        data = json.loads(urllib.request.urlopen(url).read().decode())

        return float(''.join(data['worker'][self.fullname]
                             ['current_speed'].split(',')))


class btcchina(Pool):
    name = "btcchina.com"

    def _collect(self):
        url = 'https://pool.btcchina.com/api?api_key={}'.format(self.api_key)
        data = json.loads(urllib.request.urlopen(url).read().decode())

        for worker in data['user']['workers']:
            if worker['worker_name'] == self.fullname:
                return float(worker['hashrate']) / 1000000.0


class kano(Pool):
    name = "kano.is"

    def _collect(self):
        url = ('http://kano.is/index.php?k=api&username={}&api={}'
               '&json=y&work=y').format(self.user, self.api_key)
        data = json.loads(urllib.request.urlopen(url).read().decode())

        for key in data:
            if data[key] == self.fullname:
                index = key.split(':')[1]
                return float(data['w_hashrate5m:{}'.format(index)]) / 1000000.0
        return None


def update_poolrate(pool_list, run_time, db, retry):
    pool_queue = queue.Queue()
    hashrate_queue = queue.Queue()

    for p in pool_list:
        if p['name'] in ['ghash', 'ozcoin', 'btcchina', 'kano']:
            pool_queue.put(p)

    for i in range(len(pool_list)):
        pool_thread = PoolThread(pool_queue, hashrate_queue, retry)
        pool_thread.daemon = True
        pool_thread.start()
    pool_queue.join()

    column = ['time']
    value = [run_time]
    while not hashrate_queue.empty():
        h = hashrate_queue.get(False)
        column.append(h['name'])
        value.append(h['hashrate'])

    conn = mysql.connector.connect(
        host=db['host'],
        user=db['user'],
        password=db['password'],
        database=db['database']
    )
    cursor = conn.cursor()

    pool_sql = sql.SQL(cursor)

    if not pool_sql.run('insert', 'hashrate', column, value):
        for i in range(len(column) - 1):
            pool_sql.run(
                'raw',
                'ALTER TABLE hashrate ADD `{}` DOUBLE'.format(column[i + 1])
            )
        conn.commit()
        pool_sql.run('insert', 'hashrate', column, value)

    conn.commit()
    cursor.close()
    conn.close()


class PoolThread(threading.Thread):
    def __init__(self, pool_queue, hashrate_queue, retry):
        threading.Thread.__init__(self)
        self.pool_queue = pool_queue
        self.hashrate_queue = hashrate_queue
        self.retry = retry

    def run(self):
        while True:
            try:
                p = self.pool_queue.get(False)
            except queue.Empty:
                break
            pool = eval(p['name'])(
                p['user'],
                p['worker'],
                p['api_key'],
                p['api_secret_key'] if 'api_secret_key' in p else None
            )
            hashrate = pool.run(self.retry)
            self.hashrate_queue.put({'name': p['name'], 'hashrate': hashrate})
            self.pool_queue.task_done()
