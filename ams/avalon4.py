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

import re
import datetime

import ams.miner as miner


class Avalon4(miner.Miner):
    _pattern = re.compile(
        r'Ver\[(?P<Ver>[-0-9A-Fa-f+]+)\]\s'
        'DNA\[(?P<DNA>[0-9A-Fa-f]+)\]\s'
        'Elapsed\[(?P<Elapsed>[-0-9]+)\]\s'
        # 'MW\[(?P<MW>[-\s0-9]+)\]\s'
        '.*LW\[(?P<LW>[-0-9]+)\]\s'
        # 'MH\[(?P<MH>[-\s0-9]+)\]\s'
        '.*HW\[(?P<HW>[-0-9]+)\]\s'
        'DH\[(?P<DH>[-.0-9]+)%\]\s'
        'GHS5m\[(?P<GHS5m>[-.0-9]+)\]\s'
        'DH5m\[(?P<DH5m>[-.0-9]+)%\]\s'
        'Temp\[(?P<Temp>[0-9]+)\]\s'
        'Fan\[(?P<Fan>[0-9]+)\]\s'
        'Vol\[(?P<Vol>[.0-9]+)\]\s'
        'Freq\[(?P<Freq>[.0-9]+)\]\s'
        'PG\[(?P<PG>[0-9]+)\]\s'
        'Led\[(?P<Led>0|1)\]', re.X
    )

    name = 'Avalon4'

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def __str__(self):
        return super().__str__()

    def _collect(self, *args, **kwargs):
        return super()._collect(*args, **kwargs)

    def _generate_sql_summary(self, run_time):
        # 'summary' -> table 'miner'
        try:
            summary = self.raw['summary']['SUMMARY'][0]
        except TypeError:
            return

        summary['Last getwork'] = datetime.datetime.fromtimestamp(
            summary['Last getwork']
        )

        precise_time = datetime.datetime.fromtimestamp(
            self.raw['summary']['STATUS'][0]['When']
        )

        summary_sorted = sorted(summary)
        column = ['time', 'ip', 'port', 'precise_time']
        column.extend(
            k.strip('%').replace(' ', '_').lower() for k in summary_sorted
        )
        value = [run_time, self.ip, self.port, precise_time]
        value.extend(summary[k] for k in summary_sorted)
        self.sql_queue.put({
            'command': 'insert',
            'name': 'miner_temp',
            'column': column,
            'value': value
        })

    def _generate_sql_edevs(self, run_time):
        # 'edevs' -> table 'device'
        # 'estats' -> table 'module'
        try:
            edevs = self.raw['edevs']['DEVS']
            estats = self.raw['estats']['STATS']
        except TypeError:
            return

        precise_time = datetime.datetime.fromtimestamp(
            self.raw['edevs']['STATUS'][0]['When']
        )
        column = ['time', 'ip', 'port', 'precise_time', 'device_id']
        value = [run_time, self.ip, self.port, precise_time]
        i = 0
        for edev in edevs:
            edev_sorted = sorted(edev)
            new_column = [k.strip('%').replace(' ', '_').lower()
                          for k in edev_sorted]
            edev['Last Share Time'] = datetime.datetime.fromtimestamp(
                edev['Last Share Time']
            )
            edev['Last Valid Work'] = datetime.datetime.fromtimestamp(
                edev['Last Valid Work']
            )

            new_value = [edev['ID']]
            new_value.extend(edev[k] for k in edev_sorted)
            estat = estats[i]
            new_column.extend(
                k.replace(' ', '_').lower() for k in sorted(estat)
                if k[:3] == 'AUC' or k[:3] == 'USB' or k[:4] == 'Auto'
            )
            new_value.extend(
                estat[k] for k in sorted(estat) if k[:3] == 'AUC'
                or k[:3] == 'USB' or k[:4] == 'Auto'
            )
            self.sql_queue.put({
                'command': 'insert',
                'name': 'device_temp',
                'column': column + new_column,
                'value': value + new_value
            })
            i += 1

    def _generate_sql_estats(self, run_time):
        # 'estats' -> table 'module'
        try:
            estats = self.raw['estats']['STATS']
        except TypeError:
            return

        precise_time = datetime.datetime.fromtimestamp(
            self.raw['estats']['STATUS'][0]['When']
        )
        column = ['time', 'ip', 'port', 'precise_time',
                  'device_id', 'module_id']
        value = [run_time, self.ip, self.port, precise_time]
        for estat in estats:
            for key in estat:
                if key[:5] == 'MM ID':
                    self._generate_sql_estat(column, value, key, estat)

    def _generate_sql_estat(self, column, value, key, estat):
        device_id = int(estat['ID'][3:])
        module_id = int(key[5:])
        module = estat[key]
        module_info = re.match(self._pattern, module)
        if module_info is None:
            self.log.error('{}[{}][{}] Non-match module info.'.format(
                self, device_id, module_id
            ))
            self.log.debug('{}[{}][{}] {}'.format(
                self, device_id, module_id, module
            ))
            return

        module_info = module_info.groupdict()
        new_column = []
        new_value = [device_id, module_id]
        for k in module_info:
            if (k == 'DNA' or k == 'Ver' or
                    k == 'Led' or k == 'Elapsed'):
                new_column.append(k.lower())
                new_value.append(module_info[k])
            elif (k == 'DH' or k == 'Vol' or k == 'Freq' or
                  k == 'GHS5m' or k == 'DH5m'):
                new_column.append(k.lower())
                new_value.append(float(module_info[k]))
            elif k == 'MW' or k == 'MH':
                i = 0
                for m in module_info[k].split(' '):
                    new_column.append('{}{}'.format(k.lower(), i))
                    new_value.append(float(m))
                    i += 1
            else:
                new_column.append(k.lower())
                new_value.append(int(module_info[k]))

        self.sql_queue.put({
            'command': 'insert',
            'name': 'module_temp',
            'column': column + new_column,
            'value': value + new_value
        })

    def _generate_sql_pools(self, run_time):
        # 'pools' -> table 'pool'
        try:
            pools = self.raw['pools']['POOLS']
        except TypeError:
            return

        precise_time = datetime.datetime.fromtimestamp(
            self.raw['pools']['STATUS'][0]['When']
        )
        column = ['time', 'ip', 'port', 'precise_time', 'pool_id']
        value = [run_time, self.ip, self.port, precise_time]
        for pool in pools:
            pool_sorted = sorted(pool)
            pool['Last Share Time'] = datetime.datetime.fromtimestamp(
                pool['Last Share Time']
            )
            new_column = [k.strip('%').replace(' ', '_').lower()
                          for k in pool_sorted]
            new_value = [pool['POOL']]
            new_value.extend(pool[k] for k in pool_sorted)
            self.sql_queue.put({
                'command': 'insert',
                'name': 'pool_temp',
                'column': column + new_column,
                'value': value + new_value
            })

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)

    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)


COLUMN_EDEVS = [
    {'name': 'time',
     'type': 'TIMESTAMP DEFAULT 0'},
    {'name': 'ip',
     'type': 'VARCHAR(40)'},
    {'name': 'port',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'precise_time',
     'type': 'TIMESTAMP DEFAULT 0'},
    {'name': 'device_id',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'asc',
     'type': 'INT'},
    {'name': 'name',
     'type': 'CHAR(3)'},
    {'name': 'id',
     'type': 'INT'},
    {'name': 'enabled',
     'type': 'CHAR(1)'},
    {'name': 'status',
     'type': 'CHAR(1)'},
    {'name': 'temperature',
     'type': 'DOUBLE'},
    {'name': 'mhs_av',
     'type': 'DOUBLE'},
    {'name': 'mhs_5s',
     'type': 'DOUBLE'},
    {'name': 'mhs_1m',
     'type': 'DOUBLE'},
    {'name': 'mhs_5m',
     'type': 'DOUBLE'},
    {'name': 'mhs_15m',
     'type': 'DOUBLE'},
    {'name': 'accepted',
     'type': 'INT'},
    {'name': 'rejected',
     'type': 'INT'},
    {'name': 'hardware_errors',
     'type': 'INT'},
    {'name': 'utility',
     'type': 'DOUBLE'},
    {'name': 'last_share_pool',
     'type': 'INT'},
    {'name': 'last_share_time',
     'type': 'TIMESTAMP DEFAULT 0'},
    {'name': 'total_mh',
     'type': 'DOUBLE'},
    {'name': 'diff1_work',
     'type': 'BIGINT'},
    {'name': 'difficulty_accepted',
     'type': 'DOUBLE'},
    {'name': 'difficulty_rejected',
     'type': 'DOUBLE'},
    {'name': 'last_share_difficulty',
     'type': 'DOUBLE'},
    {'name': 'no_device',
     'type': 'BOOL'},
    {'name': 'last_valid_work',
     'type': 'TIMESTAMP DEFAULT 0'},
    {'name': 'device_hardware',
     'type': 'DOUBLE'},
    {'name': 'device_rejected',
     'type': 'DOUBLE'},
    {'name': 'device_elapsed',
     'type': 'BIGINT'},
    {'name': 'mm_count',
     'type': 'INT'},
    {'name': 'automatic_voltage',
     'type': 'BOOL'},
    {'name': 'auc_ver',
     'type': 'CHAR(12)'},
    {'name': 'auc_i2c_speed',
     'type': 'INT'},
    {'name': 'auc_i2c_xdelay',
     'type': 'INT'},
    {'name': 'auc_adc',
     'type': 'INT'},
    {'name': 'usb_pipe',
     'type': 'VARCHAR(32)'},
    {'name': 'usb_delay',
     'type': 'VARCHAR(32)'},
    {'name': 'usb_tmo',
     'type': 'VARCHAR(32)'}
]

COLUMN_ESTATS = [
    {'name': 'time',
     'type': 'TIMESTAMP DEFAULT 0'},
    {'name': 'ip',
     'type': 'VARCHAR(40)'},
    {'name': 'port',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'precise_time',
     'type': 'TIMESTAMP DEFAULT 0'},
    {'name': 'device_id',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'module_id',
     'type': 'TINYINT UNSIGNED'},
    {'name': 'ver',
     'type': 'CHAR(15)'},
    {'name': 'dna',
     'type': 'CHAR(16)'},
    {'name': 'elapsed',
     'type': 'BIGINT'},
    {'name': 'lw',
     'type': 'BIGINT'},
    {'name': 'hw',
     'type': 'BIGINT'},
    # {'name': 'mw0',
    #  'type': 'BIGINT'},
    # {'name': 'mw1',
    #  'type': 'BIGINT'},
    # {'name': 'mw2',
    #  'type': 'BIGINT'},
    # {'name': 'mw3',
    #  'type': 'BIGINT'},
    # {'name': 'mw4',
    #  'type': 'BIGINT'},
    # {'name': 'mw5',
    #  'type': 'BIGINT'},
    # {'name': 'mw6',
    #  'type': 'BIGINT'},
    # {'name': 'mw7',
    #  'type': 'BIGINT'},
    # {'name': 'mw8',
    #  'type': 'BIGINT'},
    # {'name': 'mw9',
    #  'type': 'BIGINT'},
    # {'name': 'mh0',
    #  'type': 'BIGINT'},
    # {'name': 'mh1',
    #  'type': 'BIGINT'},
    # {'name': 'mh2',
    #  'type': 'BIGINT'},
    # {'name': 'mh3',
    #  'type': 'BIGINT'},
    # {'name': 'mh4',
    #  'type': 'BIGINT'},
    # {'name': 'mh5',
    #  'type': 'BIGINT'},
    # {'name': 'mh6',
    #  'type': 'BIGINT'},
    # {'name': 'mh7',
    #  'type': 'BIGINT'},
    # {'name': 'mh8',
    #  'type': 'BIGINT'},
    # {'name': 'mh9',
    #  'type': 'BIGINT'},
    {'name': 'dh',
     'type': 'DOUBLE'},
    {'name': 'ghs5m',
     'type': 'DOUBLE'},
    {'name': 'dh5m',
     'type': 'DOUBLE'},
    {'name': 'temp',
     'type': 'INT'},
    {'name': 'fan',
     'type': 'INT'},
    {'name': 'vol',
     'type': 'DOUBLE'},
    {'name': 'freq',
     'type': 'DOUBLE'},
    {'name': 'pg',
     'type': 'SMALLINT'},
    {'name': 'led',
     'type': 'BOOL'},
]


def db_init(sql_queue):
    miner.db_init(sql_queue)

    for suffix in ['', '_temp']:
        sql_queue.put({
            'command': 'create',
            'name': 'device{}'.format(suffix),
            'column_def': COLUMN_EDEVS,
            'additional': 'PRIMARY KEY(`time`, `ip`, `port`, `device_id`)',
        })
        sql_queue.put({
            'command': 'create',
            'name': 'module{}'.format(suffix),
            'column_def': COLUMN_ESTATS,
            'additional': 'PRIMARY KEY(\
                `time`, `ip`, `port`, `device_id`, `module_id`\
            )',
        })


def db_final(sql_queue):
    sql_queue.put({
        'command': 'raw',
        'query': '''
UPDATE miner_temp AS a
  LEFT OUTER JOIN (
           SELECT time, ip, port, precise_time, elapsed, total_mh
             FROM miner
            WHERE time = (SELECT MAX(time) FROM miner)
       ) b
    ON a.ip = b.ip and a.port = b.port
   SET mhs = IF(
         a.precise_time > b.precise_time
             AND TIMESTAMPDIFF(SECOND, b.precise_time, a.precise_time)
                     >= a.elapsed - b.elapsed - 1
             AND TIMESTAMPDIFF(SECOND, b.precise_time, a.precise_time)
                     <= a.elapsed - b.elapsed + 1,
         (a.total_mh - b.total_mh) / (a.elapsed - b.elapsed),
         a.total_mh / a.elapsed
       )
        ''',
    })
    for name in ['miner', 'device', 'module', 'pool']:
        sql_queue.put({
            'command': 'raw',
            'query': 'REPLACE INTO {0} SELECT * FROM {0}_temp'.format(name),
        })
    sql_queue.put({
        'command': 'raw',
        'query': 'DROP TABLES miner_temp, device_temp, module_temp, pool_temp',
    })
