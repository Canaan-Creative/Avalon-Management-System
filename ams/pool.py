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

import json
import urllib.parse
import urllib.request
from urllib.error import URLError
import hashlib
import hmac
import time
import logging


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
                    self.log.error('{} Failed fetching. {}'.
                                   format(self.name, e))
                    return None
                else:
                    self.log.debug('{} Failed fetching. Retry {}. {}'.
                                   format(self.name, r, e))
                    continue
            break
        return result


class ghash(Pool):

    name = "ghash.io"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, retry):
        super().run(retry)

    def _collect(self):
        url = 'https://cex.io/api/ghash.io/workers'
        nonce = '{:.0f}'.format(time.time()*1000)
        signature = hmac.new(self.api_secret_key,
                             msg=nonce + self.user + self.api_key,
                             digestmod=hashlib.sha256).hexdigest().upper()
        post_content = {'key': self.api_key,
                        'signature': signature,
                        'nonce': nonce}
        param = urllib.parse.urlencode(post_content)
        request = urllib.request.Request(
            url, param, {'User-agent': 'bot-cex.io-{}'.format(self.username)})
        js = urllib.request.urlopen(request).read()
        data = json.loads(js)

        return float(data[self.fullname]['last1h'])


class ozcoin(Pool):

    name = "ozco.in"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, retry):
        super().run(retry)

    def _collect(self):
        url = 'http://ozco.in/api.php?api_key={}'.format(self.api_key)
        js = urllib.request.urlopen(url).read()
        data = json.loads(js)

        return float(''.join(data['worker'][self.fullname]
                             ['current_speed'].split(',')))


class btcchina(Pool):

    name = "btcchina.com"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, retry):
        super().run(retry)

    def _collect(self):
        url = 'https://pool.btcchina.com/api?api_key={}'.format(self.api_key)
        js = urllib.request.urlopen(url).read()
        data = json.loads(js)

        for worker in data['user']['workers']:
            if worker['worker_name'] == self.fullname:
                return float(worker['hashrate']) / 1000000.0


class ckpool(Pool):

    name = "ckpool.org"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, retry):
        super().run(retry)

    def _collect(self):
        url = 'http://solo.ckpool.org/ahusers/{}'.format(self.api_key)
        js = urllib.request.urlopen(url).read()
        data = json.loads(js)

        result = data['hashrate1hr']
        if result[-1] == 'P':
            result = float(result[:-1]) * 1000000000
        elif result[-1] == 'T':
            result = float(result[:-1]) * 1000000
        elif result[-1] == 'G':
            result = float(result[:-1]) * 1000
        else:
            result = float(result[:-1])
        return result


class kano(Pool):

    name = "kano.is"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, retry):
        super().run(retry)

    def _collect(self):
        url = ('http://kano.is/index.php?k=api&username={}&api={}'
               '&json=y&work=y').format(self.user, self.api_key)
        js = urllib.request.urlopen(url).read()
        data = json.loads(js)

        for key, value in data.iteritems():
            if value == self.fullname:
                index = key.split(':')[1]
                break
        return float(data['w_hashrate5m:{}'.format(index)]) / 1000000.0


def update_poolrate(pool_list, retry):
    hashrate = []
    for p in pool_list:
        if p['name'] in ['ghash', 'ozcoin', 'btcchina', 'ckpool', 'kano']:
            pool_class = eval(p['name'])
            pool = pool_class(p['user'], p['worker'], p['api_key'],
                              p['api_secret_key'] if 'api_secret_key' in p
                              else None)
            hashrate.append(pool.run(retry))
    return hashrate
