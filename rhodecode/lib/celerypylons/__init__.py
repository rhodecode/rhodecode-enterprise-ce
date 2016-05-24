# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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
Automatically sets the environment variable `CELERY_LOADER` to
`celerypylons.loader:PylonsLoader`.  This ensures the loader is
specified when accessing the rest of this package, and allows celery
to be installed in a webapp just by importing celerypylons::

    import celerypylons

"""

import os
import warnings

CELERYPYLONS_LOADER = 'rhodecode.lib.celerypylons.loader.PylonsLoader'
if os.environ.get('CELERY_LOADER', CELERYPYLONS_LOADER) != CELERYPYLONS_LOADER:
    warnings.warn("'CELERY_LOADER' environment variable will be overridden by celery-pylons.")
os.environ['CELERY_LOADER'] = CELERYPYLONS_LOADER
