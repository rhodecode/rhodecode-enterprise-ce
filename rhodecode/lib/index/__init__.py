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
Index schema for RhodeCode
"""

import importlib
import logging

log = logging.getLogger(__name__)

# leave defaults for backward compat
default_searcher = 'rhodecode.lib.index.whoosh'
default_location = '%(here)s/data/index'


class BaseSearch(object):
    def __init__(self):
        pass

    def cleanup(self):
        pass

    def search(self, query, document_type, search_user, repo_name=None):
        raise Exception('NotImplemented')


def searcher_from_config(config, prefix='search.'):
    _config = {}
    for key in config.keys():
        if key.startswith(prefix):
            _config[key[len(prefix):]] = config[key]

    if 'location' not in _config:
        _config['location'] = default_location
    imported = importlib.import_module(_config.get('module', default_searcher))
    searcher = imported.Search(config=_config)
    return searcher
