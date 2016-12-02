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

    columns = []

    for i in range(4):
        for j in range(18, 22):
            columns.append({
                'name': 'mw{}_{}'.format(i, j),
                'type': 'INT',
            })
            for name in ['ghsmm0', 'eratio']:
                columns.append({
                    'name': '{}{}_{}'.format(name, i, j),
                    'type': 'DOUBLE',
                })
            for k in range(5):
                columns.append({
                    'name': 'c_{}_0{}_{}'.format(i, k, j),
                    'type': 'INT',
                })

    for c in columns:
        database.run(
            'raw',
            'ALTER TABLE `module` ADD COLUMN `{name}` {type}'.format(**c))

    database.commit()
    database.disconnect()
