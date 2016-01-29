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
import logging
import urllib.request


class LuCI():
    def __init__(self, ip, port=80, password='', log=True):
        self.ip = ip
        self.port = port or 80
        self.password = password or ''
        self.token = None
        if log:
            self.log = logging.getLogger('AMS.LuCI')
        else:
            self.log = False

    def __str__(self):
        ip = '({})'.format(self.ip) if ':' in self.ip else self.ip
        return '[{}:{}]'.format(ip, self.port)

    def auth(self, timeout=3):
        response = self.put('auth', 'login', ['root', self.password])
        self.token = response['result']

    def put(self, lib, method, params=None, timeout=60):
        url = 'http://{}:{}/cgi-bin/luci/rpc/{}{}'.format(
            self.ip, self.port, lib,
            '?auth={}'.format(self.token) if self.token is not None else ''
        )
        if params is None:
            data = json.dumps({"method": method})
        else:
            data = json.dumps({"method": method, "params": params})

        request = urllib.request.Request(url=url, data=data.encode())
        with urllib.request.urlopen(request, timeout=timeout) as f:
            response = f.read().decode()

        try:
            obj = json.loads(response)
            return obj
        except Exception as e:
            if not self.log:
                return False
            self.log.error('{} Error decoding json: {}'.format(self, e))
            self.log.debug('{} Error decoding json: {}'.format(self, response))
            return False
