#!/usr/bin/env python3

import json
import datetime
import sys
import importlib

from flask import Flask, g, request

from ams.sql import DataBase
from ams.miner import COLUMN_SUMMARY, COLUMN_POOLS


app = Flask(__name__)
sys.path.append('__AMS_LIB_PATH__')
cfgfile = '__AMS_CFG_PATH__'


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


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        return int(obj.timestamp())


@app.before_request
def before_request():
    g.database = DataBase(db)
    g.database.connect()


@app.route('/nodes', methods=['GET'])
def get_nodes():
    result = g.database.run('select', 'controller_config', ['ip', 'port'])
    nodes = []
    for r in result:
        nodes.append({'ip': r[0], 'port': r[1]})
    return json.dumps({'result': nodes})


@app.route('/lasttime', methods=['GET'])
def get_last_time():
    result = g.database.run('raw', 'SELECT MAX(time) FROM miner')
    return json.dumps({'result': result[0][0]}, default=json_serial)


@app.route('/config/<ip>/<port>', methods=['GET'])
def get_config(ip, port):
    import ams.luci
    clause = "`ip` = '{}'".format(ip)
    nodes = g.database.run('select', 'controller_config', ['password'], clause)
    if not nodes:
        return '{"result": "wrong node"}'
    password = nodes[0][0] if nodes[0][0] is not None else ''
    luci = ams.luci.LuCI(ip, 80, password)
    luci.auth()
    result = luci.put('uci', 'get_all', ['cgminer.default'])
    return json.dumps(result)


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
    clause = "WHERE time > '{}' AND time < '{}'".format(start, end)
    if req['scope'] == 'farm':
        hashrate = [{'values': [], 'key': 'local'}]
        result = g.database.run('raw', 'DESCRIBE hashrate')
        for r in result[1:]:
            hashrate.append({'values': [], 'key': r[0]})
        result = g.database.run(
            'raw',
            '''\
SELECT pool.*, local.mhs
  FROM hashrate AS pool
  LEFT JOIN (
        SELECT time, sum(mhs) AS mhs
          FROM miner GROUP BY time
       )
    AS local
    ON local.time = pool.time ''' + clause.replace('time', 'pool.time')
        )
        for r in result:
            hashrate[0]['values'].append({
                'x': r[0],
                'y': r[-1] * 1000000 if r[-1] is not None else 0,
            })
            for i in range(1, len(r) - 1):
                hashrate[i]['values'].append({
                    'x': r[0],
                    'y': r[i] * 1000000 if r[i] is not None else 0,
                })

        return json.dumps({'result': hashrate}, default=json_serial)
    elif req['scope'] == 'node':
        hashrate = [{'values': [], 'key': 'node'}]
        result = g.database.run(
            'raw',
            "SELECT a.time, a.mhs FROM miner AS a RIGHT JOIN "
            "(SELECT time FROM hashrate) AS b ON a.time = b.time "
            "{} AND a.ip = '{}' AND a.port = '{}'".format(
                clause.replace('time', 'b.time'), req['ip'], req['port']
            ))
        for r in result:
            hashrate[0]['values'].append({
                'x': r[0],
                'y': r[1] * 1000000 if r[1] is not None else 0,
            })
        return json.dumps({'result': hashrate}, default=json_serial)
    elif req['scope'] == 'module':
        # TODO
        pass
    else:
        # TODO: error
        pass


@app.route('/warning/<name>/<time>', methods=['GET'])
def get_warning(name, time):
    if time == 'latest':
        result = g.database.run('raw', 'SELECT MAX(time) from hashrate')
        time = result[0][0].timestamp()

    if name == 'ec':
        result = g.database.run(
            'select', 'module',
            ['ip', 'port', 'device_id', 'module_id', 'dna', 'ec'],
            "time = '{:%Y-%m-%d %H:%M:%S}' AND (ec & 65054) != 0 "
            "ORDER BY ip, port, device_id, module_id".format(
                datetime.datetime.fromtimestamp(int(time)),
            )
        )
        warning = [{
            'ip': r[0],
            'port': r[1],
            'device_id': r[2],
            'module_id': r[3],
            'dna': r[4],
            'ec': r[5]
        } for r in result]

    return json.dumps({'result': warning}, default=json_serial)


@app.route('/status/<table>/<time>/<ip>/<port>', methods=['GET'])
def get_status(table, time, ip, port):
    # TODO: prevent injection by checking args validation

    status = []
    if time == 'latest':
        node = miner_type.Miner(ip, port, 0, log=False)
        result = node.get(table)
        for r in result['value']:
            s = {}
            i = 0
            for column in result['column']:
                s[column] = r[i]
                i += 1
            status.append(s)
    else:
        result = g.database.run(
            'select',
            # TODO: some naming problem...
            # summary node(s) miner
            table if table != 'summary' else 'miner',
            None,
            "time = '{:%Y-%m-%d %H:%M:%S}' "
            "AND ip = '{}' AND port = {}".format(
                datetime.datetime.fromtimestamp(int(time)),
                ip, port
            )
        )
        for r in result:
            s = {}
            i = 0
            for column in COLUMNS[table]:
                s[column['name']] = r[i]
                i += 1
            status.append(s)

    def sort_order(x):
        order = []
        if 'device_id' in x:
            order.append(x['device_id'])
        if 'module_id' in x:
            order.append(x['module_id'])
        if 'pool_id' in x:
            order.append(x['pool_id'])
        return order

    return json.dumps(
        {'result': sorted(status, key=sort_order)},
        default=json_serial
    )


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
