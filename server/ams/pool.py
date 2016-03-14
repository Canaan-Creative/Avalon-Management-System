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

from ams.sql import DataBase


class Pool():
    name = "pool"

    def __init__(self, user, worker, key, seckey=None):
        self.key = key
        self.seckey = seckey
        self.user = user
        if worker[0] == '[' and worker[-1] == ']':
            self.worker = [x.strip() for x in worker[1:-1].split(',')]
            self.fullname = ['{}.{}'.format(user, w) for w in self.worker]
        else:
            self.worker = worker
            self.fullname = ['{}.{}'.format(user, worker)]
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
            self.seckey.encode(),
            msg='{}{}{}'.format(nonce, self.user, self.key).encode(),
            digestmod=hashlib.sha256
        ).hexdigest().upper()
        post_content = {
            'key': self.key,
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

        mhs = 0
        for name in self.fullname:
            mhs += float(data[name]['last1h'])
        return mhs


class ozcoin(Pool):
    name = "ozco.in"

    def _collect(self):
        url = 'http://ozco.in/api.php?api_key={}'.format(self.key)
        data = json.loads(urllib.request.urlopen(url).read().decode())

        mhs = 0
        for name in self.fullname:
            mhs += float(''.join(data['worker'][name]
                                 ['current_speed'].split(',')))
        return mhs


class btcchina(Pool):
    name = "btcchina.com"

    def _collect(self):
        url = 'https://pool.btcchina.com/api?api_key={}'.format(self.key)
        data = json.loads(urllib.request.urlopen(url).read().decode())

        mhs = 0
        for worker in data['user']['workers']:
            if worker['worker_name'] in self.fullname:
                mhs += float(worker['hashrate'])
        return mhs / 1000000.0


class cksolo(Pool):
    name = "solo.ckpool.org"

    def _collect(self):
        url = 'http://solo.ckpool.org/users/{}'.format(self.key)
        data = json.loads(urllib.request.urlopen(url).read().decode())
        mhs = data['hashrate1hr']
        if mhs[-1] == 'P':
            mhs = float(mhs[:-1]) * 1000000000
        elif mhs[-1] == 'T':
            mhs = float(mhs[:-1]) * 1000000
        elif mhs[-1] == 'G':
            mhs = float(mhs[:-1]) * 1000
        else:
            mhs = float(mhs[:-1])
        return mhs


class kano(Pool):
    name = "kano.is"

    def _collect(self):
        url = ('http://kano.is/index.php?k=api&username={}&api={}'
               '&json=y&work=y').format(self.user, self.key)
        data = json.loads(urllib.request.urlopen(url).read().decode())

        mhs = 0
        for index in data:
            if data[index] in self.fullname:
                index = index.split(':')[1]
                mhs += float(data['w_hashrate5m:{}'.format(index)])
        return mhs / 1000000.0


# using bitcoin address as user on kano.is
class kano_a(Pool):
    name = "kano.is"

    def _collect(self):
        url = ('http://kano.is/address.php?a={}').format(self.user)
        result = urllib.request.urlopen(url).read().decode()
        data = json.loads('{' + result.split('{')[1].split('}')[0] + '}')
        hs = data['hashrate5m']
        if hs[-1] == 'P':
            hs = float(hs[:-1]) * 1000000000
        elif hs[-1] == 'T':
            hs = float(hs[:-1]) * 1000000
        elif hs[-1] == 'G':
            hs = float(hs[:-1]) * 1000
        else:
            hs = float(hs)
        return hs


def update_poolrate(pool_list, run_time, db, retry):
    pool_queue = queue.Queue()
    hashrate_queue = queue.Queue()

    for p in pool_list:
        if p['name'] in [
                'ghash', 'ozcoin', 'btcchina',
                'kano', 'kano_a' 'cksolo']:
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

    database = DataBase(db)
    database.connect()

    if not database.run('insert', 'hashrate', column, value):
        for i in range(len(column) - 1):
            database.run(
                'raw',
                'ALTER TABLE hashrate ADD `{}` DOUBLE'.format(column[i + 1])
            )
        database.commit()
        database.run('insert', 'hashrate', column, value)

    database.commit()
    database.disconnect()


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
                p['key'],
                p['seckey'] if 'seckey' in p else None
            )
            hashrate = pool.run(self.retry)
            self.hashrate_queue.put({'name': p['name'], 'hashrate': hashrate})
            self.pool_queue.task_done()
