#!/usr/bin/env python3
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

import sys
from ams.log import log


def readCfg(filename):
    import configparser
    config = configparser.ConfigParser()
    config.read(filename)
    return config


def validIP(ip):
    if ip[0] == '[' and ip[-1] == ']':
        part = ip[1:-1].split(':')
        if len(part) > 8:
            return False
        for p in part:
            if p == '':
                continue
            if int(p, 16) > 0xffff:
                return False
    else:
        part = ip.split('.')
        if len(part) != 4:
            return False
        for p in part:
            if int(p) > 255:
                return False
    return True


def ipDecode(s):
    if ':' in s and s[0] != '[':
        ip, port = s.split(':')
        port = int(port)
        if port < 0 or port > 65535 or not validIP(ip):
            return False
    elif s[1] == '[' and s[-1] != ']':
        tmp = s.split(']')
        ip = '{}]'.format(tmp[0])
        port = int(tmp[1][1:])
        if port < 0 or port > 65535 or not validIP(ip):
            return False
    else:
        ip = s
        port = None
        if not validIP(ip):
            return False
    return (ip, port)


def update(argv):
    import datetime
    from multiprocessing import Process

    from ams.farm import Farm
    from ams.pool import update_poolrate
    from ams.sql import sql_handler, DataBase, SQLQueue

    db = readCfg('ams.cfg')['DataBase']

    database = DataBase(db)
    database.connect()
    minerList = database.run('select', 'ctrl_config', ['ip', 'port', 'mods'])
    if not minerList:
        print("No miner found.\n Run subcommand 'ctrl' to add.")
        exit()

    miners = [
        {
            'ip': m[0],
            'port': m[1],
            'mods': [int(mod) for mod in m[2].split(',')]
        }
        for m in minerList
    ]
    myFarm = Farm(miners, 'avalon4')

    poolList = database.run(
        'select', 'pools',
        ['name', 'user', 'worker', 'api_key', 'api_secret_key']
    )
    if not poolList:
        pools = []
    else:
        pools = [
            {
                'name': p[0],
                'user': p[1],
                'worker': p[2],
                'api_key': p[3],
                'api_secret_key': p[4]
            } for p in poolList
        ]
    database.disconnect()

    now = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    sql_queue = SQLQueue()

    farm_process = Process(
        target=myFarm.run,
        args=(now, sql_queue, 5, 100)
    )
    pool_process = Process(
        target=update_poolrate,
        args=(pools, now, db, 3)
    )
    db_process = Process(
        target=sql_handler,
        args=(sql_queue, db, int(db['thread_num']))
    )
    db_process.start()
    pool_process.start()
    farm_process.start()
    pool_process.join()
    farm_process.join()
    db_process.join()


def fetch(argv):
    # using jq to reformat the output is recommended
    from ams.miner import Miner
    import json

    result = ipDecode(argv[0])
    if not result:
        exit()
    ip = result[0]
    port = result[1] or 4028
    miner = Miner(ip, port, None, False)
    command = argv[1]
    if len(argv) == 2:
        parameter = None
    else:
        parameter = argv[2]
    print(json.dumps(miner.put(command, parameter)))


def cfg(argv):
    from ams.sql import DataBase

    if argv[0] != "all":
        result = ipDecode(argv[0])
        if not result:
            exit()
        ip, port = result
        if port is None:
            clause = "`ip` = '{}'".format(ip)
        else:
            clause = "`ip` = '{}' and port = '{}'".format(ip, port)

        db = readCfg('ams.cfg')['DataBase']

        database = DataBase(db)
        database.connect()
        minerList = database.run('select', 'ctrl_config', ['password'], clause)
        database.disconnect()
        if not minerList:
            exit()
        password = minerList[0][0]

    else:
        pass


def ctrl(argv):
    import tempfile
    import subprocess
    import re
    from ams.sql import DataBase

    db = readCfg('ams.cfg')['DataBase']

    database = DataBase(db)
    database.connect()
    minerList = database.run(
        'select', 'ctrl_config',
        ['ip', 'port', 'mods', 'password']
    )

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.ams') as temp:
        temp.write('#ip\tport\tmods\tpassword')
        if minerList:
            temp.write('\n')
            temp.write(
                '\n'.join('\t'.join(str(i) for i in m) for m in minerList)
            )
        temp.write('\n')
        temp.flush()
        subprocess.call(['vim', temp.name])
        temp.seek(0)
        cfg = temp.readlines()
    pattern = re.compile(
        r'\s*(?P<ip>[0-9a-fA-F.:\[\]]+)\s+'
        '(?P<port>[0-9]+)\s+'
        '(?P<mods>([0-9]+,)*[0-9]+)\s+'
        '(?P<password>[^\s]+)\s*', re.X
    )

    result = []
    for c in cfg:
        if len(c.lstrip()) == 0 or c.lstrip()[0] == '#':
            continue
        match = re.match(pattern, c)
        if match is None:
            result = None
            break
        ip = match.group('ip')
        port = int(match.group('port'))
        mods = match.group('mods')
        passwd = match.group('password')
        if not validIP(ip) or port > 65535:
            result = None
            break
        result.append({
            "ip": ip, "port": port,
            "mods": mods, "password": passwd
        })

    if result is None:
        print('Invalid configuration.')
        database.disconnect()
        exit()

    database.run('raw', 'DROP TABLES IF EXISTS ctrl_config')
    database.run('create', 'ctrl_config', [
        {"name": "ip", "type": "VARCHAR(40)"},
        {"name": "port", "type": "SMALLINT UNSIGNED"},
        {"name": "mods", "type": "VARCHAR(32)"},
        {"name": "password", "type": "VARCHAR(32)"}
    ])
    for r in result:
        database.run('insert', 'ctrl_config', list(r.keys()), list(r.values()))
    database.commit()
    database.disconnect()


def pool(argv):
    import tempfile
    import subprocess
    import re
    from ams.sql import DataBase

    db = readCfg('ams.cfg')['DataBase']

    database = DataBase(db)
    database.connect()
    poolList = database.run(
        'select', 'pool_config',
        ['pool', 'address', 'user', 'key', 'seckey']
    )

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.ams') as temp:
        temp.write('#pool\taddress\tuser\tkey\tseckey')
        if poolList:
            temp.write('\n')
            temp.write(
                '\n'.join('\t'.join(i for i in m) for m in poolList)
            )
        temp.write('\n')
        temp.flush()
        subprocess.call(['vim', temp.name])
        temp.seek(0)
        cfg = temp.readlines()

    pattern = re.compile(
        r'\s*(?P<pool>btcchina|kano|ghash)\s+'
        '(?P<address>[^\s]+)\s+'
        '(?P<user>[^\s]+)\s+'
        '(?P<key>[^\s]+)'
        '(\s+(?P<seckey>[^\s]+))?\s*', re.X
    )

    result = []
    for c in cfg:
        if len(c.lstrip()) == 0 or c.lstrip()[0] == '#':
            continue
        match = re.match(pattern, c)
        if match is None:
            result = None
            break
        pool = match.group('pool')
        address = match.group('address')
        user = match.group('user')
        key = match.group('key')
        seckey = match.group('seckey') or ''
        result.append({
            "pool": pool, "address": address, "user": user,
            "key": key, "seckey": seckey
        })

    if result is None:
        print('Invalid configuration.')
        database.disconnect()
        exit()

    database.run('raw', 'DROP TABLES pool_config')
    database.run('create', 'pool_config', [
        {"name": "pool", "type": "VARCHAR(16)"},
        {"name": "address", "type": "VARCHAR(64)"},
        {"name": "user", "type": "VARCHAR(64)"},
        {"name": "key", "type": "VARCHAR(64)"},
        {"name": "seckey", "type": "VARCHAR(64)"}
    ])
    for r in result:
        database.run('insert', 'pool_config', list(r.keys()), list(r.values()))
    database.commit()
    database.disconnect()


def alert(argv):
    pass


if __name__ == '__main__':
    doc = '''\
THIS IS THE DOC.'''

    if (len(sys.argv) < 2):
        print(doc)
        exit()

    log()
    if (sys.argv[1] == 'ctrl'):
        ctrl(sys.argv[2:])
    elif (sys.argv[1] == 'pool'):
        pool(sys.argv[2:])
    elif (sys.argv[1] == 'fetch'):
        fetch(sys.argv[2:])
    elif (sys.argv[1] == 'update'):
        update(sys.argv[2:])

    elif (sys.argv[1] == 'cfg'):
        cfg(sys.argv[2:])
    elif (sys.argv[1] == 'alert'):
        alert(sys.argv[2:])
    else:
        print(doc)
