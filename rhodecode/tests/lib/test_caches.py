# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
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

import time

import pytest

from rhodecode.lib import caches
from rhodecode.lib.memory_lru_debug import MemoryLRUNamespaceManagerBase


class TestCacheManager(object):

    @pytest.mark.parametrize('repo_name', [
        ('',),
        (u'',),
        (u'ac',),
        ('ac', ),
        (u'ęćc',),
        ('ąac',),
    ])
    def test_cache_manager_init(self, repo_name):
        cache_manager_instance = caches.get_cache_manager(
            repo_name, 'my_cache')
        assert cache_manager_instance

    def test_cache_manager_init_undefined_namespace(self):
        cache_manager_instance = caches.get_cache_manager(
            'repo_cache_long_undefined', 'my_cache')
        assert cache_manager_instance

        def_config = caches.DEFAULT_CACHE_MANAGER_CONFIG.copy()
        def_config.pop('type')
        assert cache_manager_instance.nsargs == def_config

        assert isinstance(
            cache_manager_instance.namespace, MemoryLRUNamespaceManagerBase)

    @pytest.mark.parametrize('example_input', [
        ('',),
        (u'/ac',),
        (u'/ac', 1, 2, object()),
        (u'/ęćc', 1, 2, object()),
        ('/ąac',),
        (u'/ac', ),
    ])
    def test_cache_manager_create_key(self, example_input):
        key = caches.compute_key_from_params(*example_input)
        assert key

    def test_store_and_invalidate_value_from_manager(self):
        cache_manger_instance = caches.get_cache_manager(
            'repo_cache_long', 'my_cache_store')

        def compute():
            return time.time()

        added_keys = []
        for i in xrange(3):
            _cache_key = caches.compute_key_from_params('foo_bar', 'p%s' % i)
            added_keys.append(_cache_key)
            for x in xrange(10):
                cache_manger_instance.get(_cache_key, createfunc=compute)

        for key in added_keys:
            assert cache_manger_instance[key]

        caches.clear_cache_manager(cache_manger_instance)

        for key in added_keys:
            assert key not in cache_manger_instance
        assert len(cache_manger_instance.namespace.keys()) == 0

    def test_store_and_get_value_from_manager(self):
            cache_manger_instance = caches.get_cache_manager(
                'repo_cache_long', 'my_cache_store')

            _cache_key = caches.compute_key_from_params('foo_bar', 'multicall')

            def compute():
                return time.time()

            result = set()
            for x in xrange(10):
                ret = cache_manger_instance.get(_cache_key, createfunc=compute)
                result.add(ret)

            # once computed we have only one value after executing it 10x
            assert len(result) == 1
