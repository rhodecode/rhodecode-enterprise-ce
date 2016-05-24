# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# RhodeCode Enterprise Edition, including its added features, Support services,
# and proprietary license terms, please see https://rhodecode.com/licenses/

"""
Legacy support for old logging formatter names.

.. deprecated:: 3.2.0

   Got replaced by rhodecode.lib.logging_formatter. This module stays for a
   few versions to ease the migration of INI files.

"""

import warnings

from rhodecode.lib import logging_formatter


def _deprecated_formatter(name):
    BaseFormatter = getattr(logging_formatter, name)

    class LegacyFormatter(BaseFormatter):

        def __init__(self, *args, **kwargs):
            warnings.warn(
                "Use rhodecode.lib.logging_formatter.%s instead." % name,
                DeprecationWarning)
            BaseFormatter.__init__(self, *args, **kwargs)

    return LegacyFormatter


ColorFormatter = _deprecated_formatter('ColorFormatter')
ColorFormatterSql = _deprecated_formatter('ColorFormatterSql')
