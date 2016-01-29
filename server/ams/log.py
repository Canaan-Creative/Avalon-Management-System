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

import logging
import logging.handlers


def log():
    ams_logger = logging.getLogger('AMS')
    ams_logger.setLevel(logging.DEBUG)

    handler = logging.handlers.SysLogHandler(address='/dev/log')
    formatter = logging.Formatter("[%(name)s][%(levelname)s]%(message)s")
    handler.setFormatter(formatter)

    ams_logger.addHandler(handler)
