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

import json
import datetime
import importlib
import decimal
import os

from flask import Flask, g, request

from ams.sql import DataBase
from ams.miner import COLUMN_SUMMARY, COLUMN_POOLS


app = Flask(__name__)
cfgfile = os.path.join(os.environ.get('VIRTUAL_ENV') or '/', 'etc/ams.conf')


def readCfg(filename):
    import configparser
    config = configparser.ConfigParser()
    config.read(filename)
    return config


cfg = readCfg(cfgfile)
db = cfg['DataBase']
farm_type = cfg['Farm']['type']
miner_type = importlib.import_module('ams.{}'.format(farm_type))
COLUMNS = {
    'summary': COLUMN_SUMMARY,
    'pool': COLUMN_POOLS,
    'device': miner_type.COLUMN_EDEVS,
    'module': miner_type.COLUMN_ESTATS,
}


def ams_dumps(data):
    def json_serial(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime.datetime):
            return int(obj.timestamp())
    return json.dumps(data, default=json_serial)


def ams_sort(data):
    def sort_order(x):
        order = []
        if 'ip' in x:
            order.extend([int(i) for i in x['ip'].split('.')])
        if 'port' in x:
            order.append(int(x['port']))
        if 'device_id' in x:
            order.append(int(x['device_id']))
        if 'module_id' in x:
            order.append(int(x['module_id']))
        if 'pool_id' in x:
            order.append(x['pool_id'])
        return order
    return sorted(data, key=sort_order)


@app.before_request
def before_request():
    g.database = DataBase(db)
    g.database.connect()


# miner.password need permission protection
@app.route('/nodes', methods=['GET'])
def get_nodes():
    result = g.database.run(
        'select',
        'controller_config',
        ['ip', 'port', 'mods', 'password'])
    nodes = []
    for r in result:
        nodes.append({'ip': r[0], 'port': r[1], 'mods': r[2], 'password': r[3]})
    return ams_dumps({'result': nodes})


# Need permission protection
@app.route('/update_nodes', methods=['POST'])
def update_nodes():
    nodes = request.json['nodes']
    g.database.run('raw', 'DROP TABLES IF EXISTS controller_config')
    g.database.run('create', 'controller_config', [
        {"name": "ip", "type": "VARCHAR(40)"},
        {"name": "port", "type": "SMALLINT UNSIGNED"},
        {"name": "mods", "type": "SMALLINT UNSIGNED"},
        {"name": "password", "type": "VARCHAR(32)"}
    ])
    for node in nodes:
        safe_node = {
           'ip': node['ip'],
           'port': node['port'],
           'password': node['password'],
           'mods': node['mods']
        }
        g.database.run(
            'insert', 'controller_config',
            list(safe_node.keys()), list(safe_node.values())
        )
    g.database.commit()
    return ams_dumps({'success': True})


@app.route('/shortlog', methods=['GET'])
def get_shortlog():
    result = g.database.run(
        'raw',
        '''\
SELECT a.time, a.mhs, a.node, b.module
  FROM (
        SELECT time, SUM(mhs) AS mhs, COUNT(ip) AS node
          FROM miner
         WHERE time = (SELECT MAX(time) FROM miner) AND dead IS FALSE
        )
    AS a
  JOIN (
        SELECT time, COUNT(dna) AS module
          FROM module
         WHERE time = (SELECT MAX(time) FROM miner)
        )
    AS b''')
    return ams_dumps({'result': {
        'time': result[0][0],
        'hashrate': result[0][1],
        'node_num': result[0][2],
        'module_num': result[0][3],
    }})


@app.route('/lasttime', methods=['GET'])
def get_last_time():
    result = g.database.run('raw', 'SELECT MAX(time) FROM miner')
    return ams_dumps({'result': result[0][0]})


@app.route('/config/<ip>/<port>', methods=['GET'])
def get_config(ip, port):
    import ams.luci
    clause = "`ip` = %s"
    nodes = g.database.run(
        'select', 'controller_config', ['password'], clause, [ip])
    if not nodes:
        return '{"result": "wrong node"}'
    password = nodes[0][0] if nodes[0][0] is not None else ''
    luci = ams.luci.LuCI(ip, 80, password)
    luci.auth()
    result = luci.put('uci', 'get_all', ['cgminer.default'])
    return ams_dumps(result)


@app.route('/info/<ip>/<port>', methods=['GET'])
def get_info(ip, port):
    import ams.luci
    clause = "`ip` = %s"
    nodes = g.database.run(
        'select', 'controller_config', ['password'], clause, [ip])
    if not nodes:
        return '{"result": "wrong node"}'
    password = nodes[0][0] if nodes[0][0] is not None else ''
    luci = ams.luci.LuCI(ip, 80, password)
    luci.auth()
    result = luci.put('uci', 'exec', ['ubus call network.device status'])
    result = json.loads(result['result'])
    mac = result['eth0']['macaddr']
    return ams_dumps({'mac': mac})


@app.route('/summary/<time>', methods=['GET'])
def get_summary(time):
    if time == 'latest':
        result = g.database.run('raw', 'SELECT MAX(time) from hashrate')
        time = result[0][0].timestamp()
    time = datetime.datetime.fromtimestamp(int(time))

    result = g.database.run(
        'raw',
        """\
SELECT miner.ip, miner.port, miner.mhs,
       module.number, module.temp, module.temp0, module.temp1
  FROM miner
  LEFT JOIN (
        SELECT COUNT(dna) AS number,
               AVG(temp) AS temp,
               AVG(temp0) AS temp0,
               AVG(temp1) AS temp1,
               ip, port
          FROM module
         WHERE time = '{:%Y-%m-%d %H:%M:%S}'
         GROUP BY ip, port
       )
    AS module
    ON miner.ip = module.ip AND miner.port = module.port
 WHERE miner.time = '{:%Y-%m-%d %H:%M:%S}'""".format(time, time)
    )
    summary = [{
        'ip': r[0],
        'port': r[1],
        'mhs': r[2],
        'module': r[3],
        'temp': r[4],
        'temp0': r[5],
        'temp1': r[6],
    } for r in result]

    return ams_dumps({'result': ams_sort(summary)})


@app.route('/farmmap/<time>', methods=['GET'])
def get_farmmap(time):
    if time == 'latest':
        result = g.database.run('raw', 'SELECT MAX(time) from hashrate')
        time = result[0][0].timestamp()
    time = datetime.datetime.fromtimestamp(int(time))
    result = g.database.run(
        'select', 'miner', ['ip', 'port', 'mhs', 'dead'],
        "time = '{:%Y-%m-%d %H:%M:%S}'".format(time)
    )
    farmmap = {}
    for r in result:
        farmmap['{}:{}'.format(r[0], r[1])] = {
            'ip': r[0],
            'port': r[1],
            'mhs': r[2],
            'dead': r[3],
            'avg_tempI': None,
            'avg_tempB': None,
            'max_tempI': None,
            'max_tempB': None,
            'mod_num': 0,
            'modules': [],
        }
    result = g.database.run(
        'select', 'module',
        ['ip', 'port', 'device_id', 'module_id',
         'dna', 'temp', 'temp0', 'temp1', 'ghsmm', 'ec'],
        "time = '{:%Y-%m-%d %H:%M:%S}'".format(time)
    )
    for r in result:
        (ip, port, did, mid, dna, temp, temp0, temp1, ghsmm, ec) = r
        node = farmmap['{}:{}'.format(ip, port)]
        if len(node['modules']) == 0:
            node['avg_tempI'] = temp
            node['avg_tempB'] = (temp0 + temp1) / 2
            node['max_tempI'] = temp
            node['max_tempB'] = max(temp0, temp1)
        else:
            node['avg_tempI'] += temp
            node['avg_tempB'] += (temp0 + temp1) / 2
            node['max_tempI'] = max(temp, node['max_tempI'])
            node['max_tempB'] = max(temp0, temp1, node['max_tempB'])
        node['mod_num'] += 1
        node['modules'].append({
            'id': '{}:{}'.format(did, mid),
            'dna': dna,
            'temp': temp,
            'temp0': temp0,
            'temp1': temp1,
            'ghsmm': ghsmm,
            'ec': ec,
        })

    nodes = []
    for node in farmmap.values():
        if node['mod_num'] != 0:
            node['avg_tempI'] /= node['mod_num']
            node['avg_tempB'] /= node['mod_num']
        nodes.append(node)

    return ams_dumps({'result': ams_sort(nodes)})


@app.route('/aliverate', methods=['POST'])
def get_aliverate():
    req = request.json
    start = '{:%Y-%m-%d %H:%M:%S}'.format(
        datetime.datetime.fromtimestamp(req['start']))
    end = '{:%Y-%m-%d %H:%M:%S}'.format(
        datetime.datetime.fromtimestamp(req['end']))
    clause = "WHERE time > '{}' AND time < '{}'".format(start, end)
    aliverate = [{'values': [], 'key': 'nodes'},
                 {'values': [], 'key': 'modules'}]

    result = g.database.run(
        'raw',
        '''\
SELECT pool.time, miner.number
  FROM hashrate AS pool
  LEFT JOIN (
        SELECT time, count(ip) AS number
          FROM miner ''' + clause + '''\
           AND dead IS FALSE
         GROUP BY time
       )
    AS miner
    ON miner.time = pool.time ''' + clause.replace('time', 'pool.time'))
    for r in result:
        aliverate[0]['values'].append({
            'x': r[0],
            'y': r[-1] if r[-1] is not None else 0,
            'serie': 'node',
        })

    result = g.database.run(
        'raw',
        '''\
SELECT pool.time, module.number
  FROM hashrate AS pool
  LEFT JOIN (
        SELECT time, count(dna) AS number
          FROM module ''' + clause + '''\
         GROUP BY time
       )
    AS module
    ON module.time = pool.time ''' + clause.replace('time', 'pool.time'))
    for r in result:
        aliverate[1]['values'].append({
            'x': r[0],
            'y': r[-1] if r[-1] is not None else 0,
            'serie': 'module',
        })
    return ams_dumps({'result': aliverate})


@app.route('/hashrate', methods=['POST'])
# format:
# {
#  scope: str 'farm' | 'node' | 'module'
#  ip:    str *node scope only*
#  port:  int *node scope only*
#  start: int timestamp
#  end:   int timestamp
# }
def get_hashrate():
    req = request.json
    start = '{:%Y-%m-%d %H:%M:%S}'.format(
        datetime.datetime.fromtimestamp(req['start']))
    end = '{:%Y-%m-%d %H:%M:%S}'.format(
        datetime.datetime.fromtimestamp(req['end']))
    clause = "time > '{}' AND time < '{}'".format(start, end)
    if req['scope'] == 'farm':
        hashrate = []
        result = g.database.run('raw', 'DESCRIBE hashrate')
        for r in result[1:]:
            hashrate.append({'values': [], 'key': r[0]})
        result = g.database.run('select', 'hashrate', None, clause)
        for r in result:
            for i in range(1, len(r)):
                hashrate[i - 1]['values'].append({
                    'x': r[0],
                    'y': r[i] * 1000000 if r[i] is not None else 0,
                })

        return ams_dumps({'result': hashrate})
    elif req['scope'] == 'node':
        hashrate = [{'values': [], 'key': 'node'}]
        result = g.database.run(
            'raw',
            "SELECT a.time, a.mhs FROM miner AS a RIGHT JOIN "
            "(SELECT time FROM hashrate) AS b ON a.time = b.time "
            "WHERE {} AND a.ip = %s AND a.port = %s".format(
                clause.replace('time', 'b.time')
            ),
            [req['ip'], req['port']]
        )
        for r in result:
            hashrate[0]['values'].append({
                'x': r[0],
                'y': r[1] * 1000000 if r[1] is not None else 0,
            })
        return ams_dumps({'result': hashrate})
    elif req['scope'] == 'module':
        # TODO
        pass
    else:
        # TODO: error
        pass


@app.route('/issue/<time>', methods=['GET'])
def get_issue(time):
    if time == 'latest':
        result = g.database.run('raw', 'SELECT MAX(time) from hashrate')
        time = result[0][0].timestamp()

    result = g.database.run(
        'select', 'module',
        ['ip', 'port', 'device_id', 'module_id', 'dna', 'ec'],
        "time = '{:%Y-%m-%d %H:%M:%S}' AND (ec & 65054) != 0 "
        "ORDER BY ip, port, device_id, module_id".format(
            datetime.datetime.fromtimestamp(int(time)),
        )
    )
    ec_issue = [{
        'ip': r[0],
        'port': r[1],
        'device_id': r[2],
        'module_id': r[3],
        'dna': r[4],
        'ec': r[5]
    } for r in result]

    result = g.database.run(
        'select', 'miner',
        ['ip', 'port'],
        "time = '{:%Y-%m-%d %H:%M:%S}' AND dead is TRUE "
        "ORDER BY ip, port".format(
            datetime.datetime.fromtimestamp(int(time)),
        )
    )
    node_issue = [{'ip': r[0], 'port': r[1]} for r in result]

    result = g.database.run(
        'raw',
        """\
SELECT a.ip, a.port, a.device_id, a.module_id, a.dna
  FROM (
        SELECT ip, port, device_id, module_id, dna
          FROM module
         WHERE time = '{:%Y-%m-%d %H:%M:%S}'
       )
    AS a
  JOIN (
        SELECT ip, port, dna, ec
          FROM module
         WHERE ec & 2 = 2
         GROUP BY dna
       )
    AS b
    ON a.ip = b.ip AND a.port = b.port AND a.dna = b.dna""".format(
            datetime.datetime.fromtimestamp(int(time)),
        )
    )
    hot_issue = [{
        'ip': r[0],
        'port': r[1],
        'device_id': r[2],
        'module_id': r[3],
        'dna': r[4],
    } for r in result]

    return ams_dumps({
        'result': {
            'ec': ams_sort(ec_issue),
            'node': ams_sort(node_issue),
            'hot': ams_sort(hot_issue)
        }})


@app.route('/status/<table>/<time>/<ip>/<port>', methods=['GET'])
def get_status(table, time, ip, port):

    if time == 'latest':
        node = miner_type.Miner(ip, port, 0, log=False)
        status = node.get(table)
    else:
        status = []
        result = g.database.run(
            'select',
            # TODO: some naming problem...
            # summary node(s) miner
            table if table != 'summary' else 'miner',
            None,
            "time = '{:%Y-%m-%d %H:%M:%S}' "
            "AND ip = %s AND port = %s".format(
                datetime.datetime.fromtimestamp(int(time)),
            ),
            [ip, port]
        )
        for r in result:
            s = {}
            i = 0
            for column in COLUMNS[table]:
                s[column['name']] = r[i]
                i += 1
            status.append(s)

    return ams_dumps({'result': ams_sort(status)})


@app.route('/led', methods=['POST'])
def set_led():
    import queue
    import threading

    def s(modules):
        while True:
            try:
                m = modules.get(False)
            except queue.Empty:
                break
            node = miner_type.Miner(m['ip'], m['port'], 0, log=False)
            node.put(
                'ascset',
                '{},led,{}-{}'.format(
                    m['device_id'], m['module_id'], m['led']
                )
            )
            modules.task_done()

    modules = queue.Queue()
    posted = request.json['modules']
    for m in posted:
        modules.put(m)
    for i in range(0, min(50, len(posted))):
        t = threading.Thread(
            target=s,
            args=(modules,)
        )
        t.start()
    modules.join()
    return '{"result": "success"}'


@app.teardown_request
def teardown_request(exception):
    database = getattr(g, 'database', None)
    if database is not None:
        database.disconnect()


if __name__ == '__main__':
    app.run()
