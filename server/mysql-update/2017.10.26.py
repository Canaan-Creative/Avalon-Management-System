#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import os

from ams.sql import DataBase


cfgfile = os.path.join(os.environ.get('VIRTUAL_ENV') or '/', 'etc/ams.conf')


def readCfg(filename):
    import configparser
    config = configparser.ConfigParser(interpolation=None)
    config.read(filename, encoding="utf8")
    return config


if __name__ == '__main__':
    cfg = readCfg(cfgfile)
    db = cfg['DataBase']
    database = DataBase(db)
    database.connect()

    database.run(
        command='create',
        name='blocks',
        column_def=[
            {'name': 'time', 'type': 'TIMESTAMP DEFAULT "0000-00-00 00:00:00"'},
            {'name': 'ip', 'type': 'VARCHAR(40)'},
            {'name': 'port', 'type': 'SMALLINT UNSIGNED'},
            {'name': 'blocks', 'type': 'INT UNSIGNED'}
        ],
        additional='PRIMARY KEY (`time`, `ip`, `port`)',
    )
    minerList = database.run('select', 'controller_config', ['ip', 'port'])

    nb_records = []
    for m in minerList:
        print(m[0])
        records = database.run('raw', '''\
            SELECT `time`, `precise_time`, `elapsed`, `found_blocks`
            FROM `miner` WHERE `ip` = %s and `port` = %s ORDER BY `time`
            ''', [m[0], m[1]])
        [t0, pt0, e0, b0] = records[0]
        if b0 is not None and b0 != 0:
            nb_records.append([t0, m[0], m[1], b0])
        for r in records[1:]:
            [t, pt, e, b] = r
            if e is None:
                continue
            if e0 is not None and t > t0:
                s = (pt - pt0).total_seconds()
                if (s >= e - e0 - 1) and (s <= e - e0 + 1):
                    nb = b - b0
                else:
                    nb = b
            else:
                nb = b
            if nb != 0:
                nb_records.append([t, m[0], m[1], nb])
            [t0, pt0, e0, b0] = [t, pt, e, b]

    for r in nb_records:
        database.run('insert', 'blocks',
                     ['time', 'ip', 'port', 'blocks'], r)

    database.run(
        'raw',
        'ALTER TABLE `miner` ADD COLUMN `new_blocks` INT UNSIGNED')

    database.commit()
    database.disconnect()
