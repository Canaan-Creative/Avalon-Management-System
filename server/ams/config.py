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


import os.path
import logging

import yaml


def config(yaml_file=None):
    if yaml_file is None:
        for f in ['/etc/ams.yaml', '/etc/ams/ams.yaml',
                  '~/ams.yaml', './ams.yaml']:
            if os.path.isfile(f):
                yaml_file = f
                logger = logging.getLogger('AMS.YAML')
                logger.info('Loading configuration file: {}'.format(yaml_file))
                break
    try:
        config = yaml.safe_load(file(yaml_file, 'r'))
    except:
        logger = logging.getLogger('AMS.YAML')
        logger.critical('Cannot load configuration file: {}'.format(yaml_file))
        return None
    return config
