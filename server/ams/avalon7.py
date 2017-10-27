# -*- coding: utf-8; -*-
#
# Copyright (C) 2016  DING Changchang (of Canaan Creative)
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


class Miner(miner.Miner):
    _pattern = re.compile(
        r'Ver\[(?P<Ver>[-0-9A-Fa-f+]+)\]\s'
        'DNA\[(?P<DNA>[0-9A-Fa-f]+)\]\s'
        'Elapsed\[(?P<Elapsed>[-0-9]+)\]\s'
        'MW\[(?P<MW>[-\s0-9]+)\]\s'
        'LW\[(?P<LW>[-0-9]+)\]\s'
        'MH\[(?P<MH>[-\s0-9]+)\]\s'
        'HW\[(?P<HW>[-0-9]+)\]\s'
        'DH\[(?P<DH>[-.0-9]+)%\]\s'
        'Temp\[(?P<Temp>[0-9]+)\]\s'
        'TMax\[(?P<TMax>[0-9]+)\]\s'
        'Fan\[(?P<Fan>[0-9]+)\]\s'
        'FanR\[(?P<FanR>[0-9]+)%\]\s'
        'Vi\[(?P<Vi>[-\s0-9]+)\]\s'
        'Vo\[(?P<Vo>[-\s0-9]+)\]\s'
        '('
        'PLL0\[(?P<PLL0>[-\s0-9]+)\]\s'
        'PLL1\[(?P<PLL1>[-\s0-9]+)\]\s'
        'PLL2\[(?P<PLL2>[-\s0-9]+)\]\s'
        'PLL3\[(?P<PLL3>[-\s0-9]+)\]\s'
        ')?'
        'GHSmm\[(?P<GHSmm>[-.0-9]+)\]\s'
        'WU\[(?P<WU>[-.0-9]+)\]\s'
        'Freq\[(?P<Freq>[.0-9]+)\]\s'
        'PG\[(?P<PG>[0-9]+)\]\s'
        'Led\[(?P<LED>0|1)\]\s'
        'MW0\[(?P<MW0>[0-9\s]+)\]\s'
        'MW1\[(?P<MW1>[0-9\s]+)\]\s'
        'MW2\[(?P<MW2>[0-9\s]+)\]\s'
        'MW3\[(?P<MW3>[0-9\s]+)\]\s'
        'TA\[(?P<TA>[0-9]+)\]\s'
        'ECHU\[(?P<ECHU>[0-9\s]+)\]\s'
        'ECMM\[(?P<ECMM>[0-9]+)\]\s'
        '(.*'
        'SF0\[(?P<SF0>[-\s0-9]+)\]\s'
        'SF1\[(?P<SF1>[-\s0-9]+)\]\s'
        'SF2\[(?P<SF2>[-\s0-9]+)\]\s'
        'SF3\[(?P<SF3>[-\s0-9]+)\]\s'
        'PMUV\[(?P<PMUV>[0-9A-Fa-f\s]+)\]\s'
        'ERATIO0\[(?P<ERATIO0>[-.%\s0-9]+)\]\s'
        'ERATIO1\[(?P<ERATIO1>[-.%\s0-9]+)\]\s'
        'ERATIO2\[(?P<ERATIO2>[-.%\s0-9]+)\]\s'
        'ERATIO3\[(?P<ERATIO3>[-.%\s0-9]+)\]\s'
        'C_0_00\[(?P<C_0_00>[\s0-9]+)\]\s'
        'C_1_00\[(?P<C_1_00>[\s0-9]+)\]\s'
        'C_2_00\[(?P<C_2_00>[\s0-9]+)\]\s'
        'C_[34]_00\[(?P<C_3_00>[\s0-9]+)\]\s'
        'C_0_01\[(?P<C_0_01>[\s0-9]+)\]\s'
        'C_1_01\[(?P<C_1_01>[\s0-9]+)\]\s'
        'C_2_01\[(?P<C_2_01>[\s0-9]+)\]\s'
        'C_3_01\[(?P<C_3_01>[\s0-9]+)\]\s'
        'C_0_02\[(?P<C_0_02>[\s0-9]+)\]\s'
        'C_1_02\[(?P<C_1_02>[\s0-9]+)\]\s'
        'C_2_02\[(?P<C_2_02>[\s0-9]+)\]\s'
        'C_3_02\[(?P<C_3_02>[\s0-9]+)\]\s'
        'C_0_03\[(?P<C_0_03>[\s0-9]+)\]\s'
        'C_1_03\[(?P<C_1_03>[\s0-9]+)\]\s'
        'C_2_03\[(?P<C_2_03>[\s0-9]+)\]\s'
        'C_3_03\[(?P<C_3_03>[\s0-9]+)\]\s'
        'C_0_04\[(?P<C_0_04>[\s0-9]+)\]\s'
        'C_1_04\[(?P<C_1_04>[\s0-9]+)\]\s'
        'C_2_04\[(?P<C_2_04>[\s0-9]+)\]\s'
        'C_3_04\[(?P<C_3_04>[\s0-9]+)\]\s'
        'GHSmm00\[(?P<GHSmm00>[-.\s0-9]+)\]\s'
        'GHSmm01\[(?P<GHSmm01>[-.\s0-9]+)\]\s'
        'GHSmm02\[(?P<GHSmm02>[-.\s0-9]+)\]\s'
        'GHSmm03\[(?P<GHSmm03>[-.\s0-9]+)\]\s'
        ')?'
        'FM\[(?P<FM>[0-9]+)\]\s'
        'CRC\[(?P<CRC>[0-9\s]+)\]\s.*'
        'PVT_T\[(?P<PVT_T>[-0-9\s/]+)\]', re.X
    )

    name = 'Avalon7'

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
        except (TypeError, KeyError):
            self.sql_queue.put({
                'command': 'insert',
                'name': 'miner_temp',
                'column': ['time', 'ip', 'port',
                           'precise_time', 'total_mh', 'dead'],
                'value': [run_time, self.ip, self.port, run_time, 0, 1],
            })
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
        try:
            self.sql_queue.put({
                'command': 'insert',
                'name': 'miner_temp',
                'column': column,
                'value': value
            })
        except:
            self.sql_queue.append({
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
        except (TypeError, KeyError):
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
                if k.replace(' ', '_').lower() in [
                    'mm_count',
                    'smart_speed',
                    'auc_ver',
                    'auc_i2c_speed',
                    'auc_i2c_xdelay',
                    'auc_sensor',
                    'auc_temperature',
                    'usb_pipe',
                    'usb_delay',
                    'usb_tmo'
                ]
            )
            new_value.extend(
                estat[k] for k in sorted(estat)
                if k.replace(' ', '_').lower() in [
                    'mm_count',
                    'smart_speed',
                    'auc_ver',
                    'auc_i2c_speed',
                    'auc_i2c_xdelay',
                    'auc_sensor',
                    'auc_temperature',
                    'usb_pipe',
                    'usb_delay',
                    'usb_tmo'
                ]
            )
            try:
                self.sql_queue.put({
                    'command': 'insert',
                    'name': 'device_temp',
                    'column': column + new_column,
                    'value': value + new_value
                })
            except:
                self.sql_queue.append({
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
        except (TypeError, KeyError):
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
            if not self.log:
                return
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
                    k == 'LED' or k == 'Elapsed'):
                new_column.append(k.lower())
                new_value.append(module_info[k])
            elif (k == 'DH' or k == 'Freq' or k == 'WU' or
                  k == 'GHSmm'):
                new_column.append(k.lower())
                new_value.append(float(module_info[k]))
            elif (k in ['PVT_T', 'MW', 'MH', 'Vi',
                        'Vo', 'ECHU', 'CRC', 'PMUV'] or
                  k[:-1] in ['PLL', 'SF', 'GHSmm0', 'MW', 'ERATIO'] or
                  k[:2] == 'C_') and module_info[k] is not None:
                for i, m in enumerate(module_info[k].split()):
                    new_column.append('{}_{}'.format(k.lower(), i))
                    if k[:-1] == 'ERATIO':
                        new_value.append(float(m[:-1]))
                    elif k[:-1] == 'GHSmm0':
                        new_value.append(float(m))
                    elif k == 'PVT_T' or k == 'PMUV':
                        new_value.append(m)
                    else:
                        new_value.append(int(m))
            elif module_info[k] is not None:
                new_column.append(k.lower())
                new_value.append(int(module_info[k]))

        try:
            self.sql_queue.put({
                'command': 'insert',
                'name': 'module_temp',
                'column': column + new_column,
                'value': value + new_value
            })
        except:
            self.sql_queue.append({
                'command': 'insert',
                'name': 'module_temp',
                'column': column + new_column,
                'value': value + new_value
            })

    def _generate_sql_pools(self, run_time):
        # 'pools' -> table 'pool'
        try:
            pools = self.raw['pools']['POOLS']
        except (TypeError, KeyError):
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
            try:
                self.sql_queue.put({
                    'command': 'insert',
                    'name': 'pool_temp',
                    'column': column + new_column,
                    'value': value + new_value
                })
            except:
                self.sql_queue.append({
                    'command': 'insert',
                    'name': 'pool_temp',
                    'column': column + new_column,
                    'value': value + new_value
                })

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)


COLUMN_EDEVS = [
    {'name': 'time',
     'type': 'TIMESTAMP DEFAULT "0000-00-00 00:00:00"'},
    {'name': 'ip',
     'type': 'VARCHAR(40)'},
    {'name': 'port',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'precise_time',
     'type': 'TIMESTAMP DEFAULT "0000-00-00 00:00:00"'},
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
     'type': 'TIMESTAMP DEFAULT "0000-00-00 00:00:00"'},
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
     'type': 'TIMESTAMP DEFAULT "0000-00-00 00:00:00"'},
    {'name': 'device_hardware',
     'type': 'DOUBLE'},
    {'name': 'device_rejected',
     'type': 'DOUBLE'},
    {'name': 'device_elapsed',
     'type': 'BIGINT'},
    {'name': 'mm_count',
     'type': 'INT'},
    {'name': 'smart_speed',
     'type': 'BOOL'},
    {'name': 'automatic_voltage',
     'type': 'BOOL'},
    {'name': 'auc_ver',
     'type': 'CHAR(12)'},
    {'name': 'auc_i2c_speed',
     'type': 'INT'},
    {'name': 'auc_i2c_xdelay',
     'type': 'INT'},
    {'name': 'auc_sensor',
     'type': 'INT'},
    {'name': 'auc_temperature',
     'type': 'DOUBLE'},
    {'name': 'usb_pipe',
     'type': 'VARCHAR(32)'},
    {'name': 'usb_delay',
     'type': 'VARCHAR(32)'},
    {'name': 'usb_tmo',
     'type': 'VARCHAR(32)'}
]

COLUMN_ESTATS = [
    {'name': 'time',
     'type': 'TIMESTAMP DEFAULT "0000-00-00 00:00:00"'},
    {'name': 'ip',
     'type': 'VARCHAR(40)'},
    {'name': 'port',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'precise_time',
     'type': 'TIMESTAMP DEFAULT "0000-00-00 00:00:00"'},
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
    {'name': 'dh',
     'type': 'DOUBLE'},
    {'name': 'temp',
     'type': 'INT'},
    {'name': 'tmax',
     'type': 'INT'},
    {'name': 'fan',
     'type': 'INT'},
    {'name': 'fanr',
     'type': 'INT'},
    {'name': 'ghsmm',
     'type': 'DOUBLE'},
    {'name': 'wu',
     'type': 'DOUBLE'},
    {'name': 'freq',
     'type': 'DOUBLE'},
    {'name': 'pg',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'led',
     'type': 'BOOL'},
    {'name': 'ta',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'ecmm',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'fm',
     'type': 'SMALLINT UNSIGNED'},
    {'name': 'pmuv_0',
     'type': 'CHAR(4)'},
    {'name': 'pmuv_1',
     'type': 'CHAR(4)'},
]

for i in range(4):
    COLUMN_ESTATS.append({
        'name': 'pvt_t_{}'.format(i),
        'type': 'VARCHAR(18)',
    })

    for name in ['mw', 'mh', 'vi', 'vo', 'echu', 'crc']:
        COLUMN_ESTATS.append({
            'name': '{}_{}'.format(name, i),
            'type': 'INT',
        })
    for j in range(6):
        for name in ['pll', 'sf']:
            COLUMN_ESTATS.append({
                'name': '{}{}_{}'.format(name, i, j),
                'type': 'INT',
            })
    for j in range(22):
        COLUMN_ESTATS.append({
            'name': 'mw{}_{}'.format(i, j),
            'type': 'INT',
        })
        for name in ['ghsmm0', 'eratio']:
            COLUMN_ESTATS.append({
                'name': '{}{}_{}'.format(name, i, j),
                'type': 'DOUBLE',
            })
        for k in range(5):
            COLUMN_ESTATS.append({
                'name': 'c_{}_0{}_{}'.format(i, k, j),
                'type': 'INT',
            })


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


def db_final(sql_queue, run_time):
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
    sql_queue.put({
        'command': 'raw',
        'query': '''
UPDATE miner_temp AS a
  LEFT OUTER JOIN (
           SELECT time, ip, port, precise_time, elapsed, found_blocks
             FROM miner
            WHERE time = (SELECT MAX(time) FROM miner)
       ) b
    ON a.ip = b.ip and a.port = b.port
   SET new_blocks = IF(
         a.precise_time > b.precise_time
             AND TIMESTAMPDIFF(SECOND, b.precise_time, a.precise_time)
                     >= a.elapsed - b.elapsed - 1
             AND TIMESTAMPDIFF(SECOND, b.precise_time, a.precise_time)
                     <= a.elapsed - b.elapsed + 1,
        a.found_blocks, a.found_blocks - b.found_blocks)''',
    })

    sql_queue.put({
        'command': 'raw',
        'query': '''\
            REPLACE INTO hashrate (time, local)
            SELECT time, sum(mhs) FROM miner_temp''',
    })

    sql_queue.put({
        'command': 'raw',
        'query': '''\
            REPLACE INTO blocks (time, ip, port, blocks)
            SELECT time, ip, port, new_blocks FROM miner_temp
            WHERE new_blocks > 0''',
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
