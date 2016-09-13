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
import time
import importlib
import decimal
import os
import hashlib
import configparser
import multiprocessing
import copy

from flask import Flask, g, request
from jose import jwt
import redis

import ams.luci
import ams.rtac
from ams.log import log
from ams.sql import DataBase
from ams.miner import COLUMN_SUMMARY, COLUMN_POOLS


app = Flask(__name__)
cfgfile = os.path.join(os.environ.get('VIRTUAL_ENV') or '/', 'etc/ams.conf')


def readCfg(filename):
    config = configparser.ConfigParser(interpolation=None)
    config.read(filename, encoding="utf8")
    return config


cfg = readCfg(cfgfile)
jwt_password = cfg['JWT']['password']
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


def ams_auth(token):
    try:
        claims = jwt.decode(token, jwt_password, ['HS256'])
        return claims
    except:
        return False


@app.before_request
def before_request():
    log()
    g.database = DataBase(db)
    g.database.connect()


@app.route('/order', methods=['POST', 'GET'])
def order_handler():
    server = redis.StrictRedis()
    if request.method == 'POST':
        order = request.json.get('order')
        g.database.run(
            'raw',
            '''\
INSERT INTO order
       (order_id, doc_id, quantity, batch)
VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
       order_id = %s''',
            [order['order_id'], order['doc_id'],
             order['quantity'], order['batch'],
             order['order_id']]
        )
        server.set('order', ams_dumps(order))
        return ams_dumps({'success': True, 'order_id': order['order_id']})

    else:
        order = server.get('order')
        if order is None:
            order = {
                'order_id': '',
                'doc_id': '',
                'quantity': '',
                'batch': '',
                'serial': 0,
                'product_header': '',
                'components': [],
            }
            order = ams_dumps(order)
        return ams_dumps({
            'success': True,
            'result': json.loads(order),
        })


@app.route('/product', methods=['POST'])
def product_handler():
    product = request.json.get('product')
    g.database.run(
        'insert', 'products',
        ['product_id', 'order_id', 'time'],
        [product['product_id'], product['order_id'],
         '{:%Y-%m-%d %H:%M:%S}'.format(
             datetime.datetime.fromtimestamp(product['time'])
         )]
    )
    for component in product['components']:
        g.database.run(
            'insert', 'components',
            ['component_id', 'product_id', 'time'],
            [component['component_id'], product['product_id'],
             '{:%Y-%m-%d %H:%M:%S}'.format(
                 datetime.datetime.fromtimestamp(component['time'])
             )]
        )
    g.database.commit()
    return ams_dumps({'success': True})


@app.route('/rules', methods=['POST', 'GET'])
def rule_handler():
    if request.method == 'POST':
        rules = request.json.get('rules')
        now = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        for code_rule in rules['code']:
            g.database.run(
                'insert', 'code_rule',
                ['header', 'name', 'model', 'time'],
                [code_rule['header'], code_rule['name'],
                 code_rule['model'], now]
            )
        for depend_rule in rules['depend']:
            g.database.run(
                'insert', 'depend_rule',
                ['component_header', 'product_header', 'time'],
                [depend_rule['component_header'],
                 depend_rule['product_header'],
                 now]
            )
        g.database.commit()
        return ams_dumps({'success': True})
    else:
        rules = {'code': [], 'depend': []}
        result = g.database.run(
            'select', 'code_rule',
            ['header', 'name', 'model'],
            'time = (SELECT MAX(time) from code_rule)'
        )
        for r in result:
            rules['code'].append({
                'header': r[0], 'name': r[1], 'model': r[2]
            })
        result = g.database.run(
            'select', 'depend_rule',
            ['component_header', 'product_header'],
            'time = (SELECT MAX(time) from code_rule)'
        )
        for r in result:
            rules['depend'].append({
                'component_header': r[0], 'product_header': r[1]
            })

        return ams_dumps({'result': rules})


@app.route('/nodes', methods=['GET'])
def get_nodes():
    result = g.database.run(
        'select',
        'controller_config',
        ['ip', 'port', 'mods'])
    nodes = []
    if result:
        for r in result:
            nodes.append({'ip': r[0], 'port': r[1], 'mods': r[2]})
    return ams_dumps({'result': nodes})


@app.route('/update_nodes', methods=['POST'])
def update_nodes():
    token = request.json.get('token')
    if not ams_auth(token):
        return ams_dumps({'auth': False})
    nodes = request.json.get('nodes')
    g.database.run('raw', 'DROP TABLES IF EXISTS controller_config')
    g.database.run('create', 'controller_config', [
        {"name": "ip", "type": "VARCHAR(40)"},
        {"name": "port", "type": "SMALLINT UNSIGNED"},
        {"name": "mods", "type": "SMALLINT UNSIGNED"},
    ])
    for node in nodes:
        safe_node = {
           'ip': node['ip'],
           'port': node['port'],
           'mods': node['mods'],
        }
        g.database.run(
            'insert', 'controller_config',
            list(safe_node.keys()), list(safe_node.values())
        )
    g.database.commit()
    return ams_dumps({'success': True})


# TODO: change to /shortlog/<time>
@app.route('/shortlog', methods=['GET'])
def get_shortlog():
    result = g.database.run(
        'raw',
        '''\
SELECT a.time, a.mhs, a.node, b.module, b.ghs
  FROM (
        SELECT time, SUM(mhs) AS mhs, COUNT(ip) AS node
          FROM miner
         WHERE time = (SELECT MAX(time) FROM miner) AND dead IS FALSE
        )
    AS a
  JOIN (
        SELECT time, COUNT(dna) AS module, SUM(ghsmm) AS ghs
          FROM module
         WHERE time = (SELECT MAX(time) FROM miner)
        )
    AS b''')
    return ams_dumps({'result': {
        'time': result[0][0],
        'hashrate_cgminer': result[0][1] if result[0][1] else 0,
        'node_num': result[0][2],
        'module_num': result[0][3],
        'hashrate': float(result[0][4]) * 1000 if result[0][4] else 0,
    }})


@app.route('/pool_summary/<time>', methods=['GET'])
def get_pool_summary(time):
    if time == 'latest':
        result = g.database.run('raw', 'SELECT MAX(time) from hashrate')
        time = result[0][0].timestamp()
    time = datetime.datetime.fromtimestamp(int(time))

    result = g.database.run(
        'raw',
        '''\
SELECT url, SUBSTRING_INDEX(`user`, '.', 1) AS username, sum(ghs) AS ghs,
       COUNT(ip) AS ip_num, SUM(module_num) AS module_num
  FROM (
        SELECT a.ip, a.port, url, user, b.ghs ,b.module_num
          FROM pool AS a
          JOIN (
                SELECT ip, port, SUM(ghsmm) AS ghs, COUNT(dna) AS module_num
                  FROM module
                 WHERE time = '{0:%Y-%m-%d %H:%M:%S}'
                 GROUP BY ip, port)
            AS b
            ON a.port = b.port AND a.ip = b.ip
         WHERE a.time = '{0:%Y-%m-%d %H:%M:%S}' AND a.pool_id = 0
         ORDER BY a.ip)
    AS c
 GROUP BY username'''.format(time))

    summary = []
    for r in result:
        summary.append({
            'url': r[0],
            'username': r[1],
            'ghs': r[2],
            'node_num': r[3],
            'module_num': r[4],
        })
    return ams_dumps({'result': summary})


@app.route('/lasttime', methods=['GET'])
def get_last_time():
    result = g.database.run('raw', 'SELECT MAX(time) FROM miner')
    return ams_dumps({'result': result[0][0]})


@app.route('/config/<ip>/<port>', methods=['GET'])
def get_config(ip, port):
    try:
        nodes = g.database.run(
            'select',
            'controller_security',
            ['old_password', 'password'],
            "`ip` = %s",
            [ip]
        )
        password = nodes[0][1] if nodes[0][1] is not None else ''
        old_password = (nodes[0][0] if nodes[0][0] is not None else password)
    except:
        password = ''
        old_password = ''

    luci = ams.luci.LuCI(ip, 80, password)
    if not luci.auth():
        luci = ams.luci.LuCI(ip, 80, old_password)
    if not luci.auth():
        luci = ams.luci.LuCI(ip, 80, '')
    if not luci.auth():
        return '{"result": "auth false"}'

    result = luci.put('uci', 'get_all', ['cgminer.default'])
    return ams_dumps(result)


@app.route('/info/<ip>/<port>', methods=['GET'])
def get_info(ip, port):
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
       module.number, module.temp, module.tmax
  FROM miner
  LEFT JOIN (
        SELECT COUNT(dna) AS number,
               AVG(temp) AS temp,
               MAX(tmax) AS tmax,
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
        'tmax': r[5],
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
            'temp': None,
            'tmax': None,
            'mod_num': 0,
            'modules': [],
        }
    result = g.database.run(
        'select', 'module',
        ['ip', 'port', 'device_id', 'module_id',
         'dna', 'temp', 'tmax', 'ghsmm',
         'echu_0', 'echu_1', 'echu_2', 'echu_3', 'ecmm'],
        "time = '{:%Y-%m-%d %H:%M:%S}'".format(time)
    )
    for r in result:
        (ip, port, did, mid, dna, temp, tmax, ghsmm,
         echu_0, echu_1, echu_2, echu_3, ecmm) = r
        node = farmmap['{}:{}'.format(ip, port)]
        if len(node['modules']) == 0:
            node['temp'] = temp
            node['tmax'] = tmax
        else:
            node['temp'] += temp
            node['tmax'] = max(tmax, node['tmax'])
        node['mod_num'] += 1
        node['modules'].append({
            'id': '{}:{}'.format(did, mid),
            'dna': dna,
            'temp': temp,
            'tmax': tmax,
            'ghsmm': ghsmm,
            'echu': [echu_0, echu_1, echu_2, echu_3],
            'ecmm': ecmm,
        })

    nodes = []
    for node in farmmap.values():
        if node['mod_num'] != 0:
            node['temp'] /= node['mod_num']
        nodes.append(node)

    return ams_dumps({'result': ams_sort(nodes)})


@app.route('/aliverate', methods=['POST'])
def get_aliverate():
    start = '{:%Y-%m-%d %H:%M:%S}'.format(
        datetime.datetime.fromtimestamp(request.json.get('start')))
    end = '{:%Y-%m-%d %H:%M:%S}'.format(
        datetime.datetime.fromtimestamp(request.json.get('end')))
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
        ['ip', 'port', 'device_id', 'module_id', 'dna',
         'echu_0', 'echu_1', 'echu_2', 'echu_3', 'ecmm'],
        "time = '{:%Y-%m-%d %H:%M:%S}' AND (ecmm != 0 OR "
        "echu_0 != 0 OR echu_1 != 0 OR echu_2 != 0 OR echu_3 != 0) "
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
        'echu_0': r[5],
        'echu_1': r[6],
        'echu_2': r[7],
        'echu_3': r[8],
        'ec_mm': r[9]
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

    '''
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
    '''

    return ams_dumps({
        'result': {
            'ec': ams_sort(ec_issue),
            'node': ams_sort(node_issue),
            # 'hot': ams_sort(hot_issue)
        }})


@app.route('/status/<table>/<time>/<ip>/<port>', methods=['GET'])
def get_status(table, time, ip, port):

    if time == 'latest':
        if table == 'debug':
            node = miner_type.Miner(ip, port, 0, log=False)
            node.put('debug', 'D')
            raw = node.put('estats')
            node.put('debug', 'D')
            status = []
            for i, device in enumerate(raw['STATS']):
                status.append([])
                j = 1
                while 'MM ID{}'.format(j) in device:
                    status[i].append(device['MM ID{}'.format(j)])
                    j += 1
        else:
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


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    result = g.database.run(
        'select',
        'user',
        ['password'],
        'username = %s',
        [username]
    )
    if len(result) == 0 or hash_password != result[0][0]:
        return '{"auth": false}'
    claims = {
        'exp': int(time.time()) + 3600,
        'name': username,
    }
    token = jwt.encode(claims, jwt_password, algorithm='HS256')
    return ams_dumps({"auth": True, "token": token})


@app.route('/rtac', methods=['POST'])
def rtac():
    nodes = request.json.get('nodes')
    commands = request.json.get('commands')
    session_id = request.json.get('session_id')

    token = request.json.get('token')
    claims = ams_auth(token)
    if not claims:
        return '{"auth": false}'
    name = claims['name']

    key = "{}:{}".format(name, session_id)

    result_queue = multiprocessing.Queue()

    rtac_process = multiprocessing.Process(
        target=ams.rtac.rtac,
        args=(copy.deepcopy(nodes),
              copy.deepcopy(commands),
              'luci', db, result_queue)
    )
    rtac_process.daemon = False
    rtac_process.start()

    def storeResults(queue, key):
        server = redis.StrictRedis()
        while True:
            result = queue.get()
            if result == 'END':
                break
            server.rpush(key, json.dumps(result))

    result_process = multiprocessing.Process(
        target=storeResults,
        args=(result_queue, key)
    )
    result_process.daemon = False
    result_process.start()

    return ams_dumps({"session": session_id})


@app.route('/rtaclog', methods=['POST'])
def rtaclog():
    session_id = request.json.get('session_id')

    token = request.json.get('token')
    claims = ams_auth(token)
    if not claims:
        return '{"auth": false}'
    name = claims['name']

    key = "{}:{}".format(name, session_id)

    server = redis.StrictRedis()
    result = server.blpop(key, 3)
    if result is None:
        return '{"result": "timeout"}'
    else:
        return result[1]


@app.teardown_request
def teardown_request(exception):
    database = getattr(g, 'database', None)
    if database is not None:
        database.disconnect()


if __name__ == '__main__':
    app.run()
