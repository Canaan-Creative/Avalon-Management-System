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
# along with AMS.  If not, see <http://www.gnu.org/licenses/>.

import logging
import logging.handlers

from ams.log import log


def main():
    test_logger = logging.getLogger('AMS')
    test_logger.critical('Test')
    test_logger = logging.getLogger('AMS.Test')
    test_logger.critical('Test')


if __name__ == '__main__':
    log()
    main()
