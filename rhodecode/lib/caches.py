# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016  RhodeCode GmbH
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


import beaker
import logging

from beaker.cache import _cache_decorate, cache_regions, region_invalidate

from rhodecode.lib.utils import safe_str, md5
from rhodecode.model.db import Session, CacheKey, IntegrityError

log = logging.getLogger(__name__)

FILE_TREE = 'cache_file_tree'
FILE_TREE_META = 'cache_file_tree_metadata'
FILE_SEARCH_TREE_META = 'cache_file_search_metadata'
SUMMARY_STATS = 'cache_summary_stats'

# This list of caches gets purged when invalidation happens
USED_REPO_CACHES = (FILE_TREE, FILE_TREE_META, FILE_TREE_META)

DEFAULT_CACHE_MANAGER_CONFIG = {
    'type': 'memorylru_base',
    'max_items': 10240,
    'key_length': 256,
    'enabled': True
}


def configure_cache_region(
        region_name, region_kw, default_cache_kw, default_expire=60):
    default_type = default_cache_kw.get('type', 'memory')
    default_lock_dir = default_cache_kw.get('lock_dir')
    default_data_dir = default_cache_kw.get('data_dir')

    region_kw['lock_dir'] = region_kw.get('lock_dir', default_lock_dir)
    region_kw['data_dir'] = region_kw.get('data_dir', default_data_dir)
    region_kw['type'] = region_kw.get('type', default_type)
    region_kw['expire'] = int(region_kw.get('expire', default_expire))

    beaker.cache.cache_regions[region_name] = region_kw


def get_cache_manager(region_name, cache_name, custom_ttl=None):
    """
    Creates a Beaker cache manager. Such instance can be used like that::

    _namespace = caches.get_repo_namespace_key(caches.XXX, repo_name)
    cache_manager = caches.get_cache_manager('repo_cache_long', _namespace)
    _cache_key = caches.compute_key_from_params(repo_name, commit.raw_id)
    def heavy_compute():
        ...
    result = cache_manager.get(_cache_key, createfunc=heavy_compute)

    :param region_name: region from ini file
    :param cache_name: custom cache name, usually prefix+repo_name. eg
        file_switcher_repo1
    :param custom_ttl: override .ini file timeout on this cache
    :return: instance of cache manager
    """

    cache_config = cache_regions.get(region_name, DEFAULT_CACHE_MANAGER_CONFIG)
    if custom_ttl:
        log.debug('Updating region %s with custom ttl: %s',
                  region_name, custom_ttl)
        cache_config.update({'expire': custom_ttl})

    return beaker.cache.Cache._get_cache(cache_name, cache_config)


def clear_cache_manager(cache_manager):
    log.debug('Clearing all values for cache manager %s', cache_manager)
    cache_manager.clear()


def clear_repo_caches(repo_name):
    # invalidate cache manager for this repo
    for prefix in USED_REPO_CACHES:
        namespace = get_repo_namespace_key(prefix, repo_name)
        cache_manager = get_cache_manager('repo_cache_long', namespace)
        clear_cache_manager(cache_manager)


def compute_key_from_params(*args):
    """
    Helper to compute key from given params to be used in cache manager
    """
    return md5("_".join(map(safe_str, args)))


def get_repo_namespace_key(prefix, repo_name):
    return '{0}_{1}'.format(prefix, compute_key_from_params(repo_name))


def conditional_cache(region, prefix, condition, func):
    """
    Conditional caching function use like::
        def _c(arg):
            # heavy computation function
            return data

        # depending on the condition the compute is wrapped in cache or not
        compute = conditional_cache('short_term', 'cache_desc',
                                    condition=True, func=func)
        return compute(arg)

    :param region: name of cache region
    :param prefix: cache region prefix
    :param condition: condition for cache to be triggered, and
        return data cached
    :param func: wrapped heavy function to compute

    """
    wrapped = func
    if condition:
        log.debug('conditional_cache: True, wrapping call of '
                  'func: %s into %s region cache', region, func)
        cached_region = _cache_decorate((prefix,), None, None, region)
        wrapped = cached_region(func)
    return wrapped


class ActiveRegionCache(object):
    def __init__(self, context):
        self.context = context

    def invalidate(self, *args, **kwargs):
        return False

    def compute(self):
        log.debug('Context cache: getting obj %s from cache', self.context)
        return self.context.compute_func(self.context.cache_key)


class FreshRegionCache(ActiveRegionCache):
    def invalidate(self):
        log.debug('Context cache: invalidating cache for %s', self.context)
        region_invalidate(
            self.context.compute_func, None, self.context.cache_key)
        return True


class InvalidationContext(object):
    def __repr__(self):
        return '<InvalidationContext:{}[{}]>'.format(
            self.repo_name, self.cache_type)

    def __init__(self, compute_func, repo_name, cache_type,
                 raise_exception=False):
        self.compute_func = compute_func
        self.repo_name = repo_name
        self.cache_type = cache_type
        self.cache_key = compute_key_from_params(
            repo_name, cache_type)
        self.raise_exception = raise_exception

    def get_cache_obj(self):
        cache_key = CacheKey.get_cache_key(
            self.repo_name, self.cache_type)
        cache_obj = CacheKey.get_active_cache(cache_key)
        if not cache_obj:
            cache_obj = CacheKey(cache_key, self.repo_name)
        return cache_obj

    def __enter__(self):
        """
        Test if current object is valid, and return CacheRegion function
        that does invalidation and calculation
        """

        self.cache_obj = self.get_cache_obj()
        if self.cache_obj.cache_active:
            # means our cache obj is existing and marked as it's
            # cache is not outdated, we return BaseInvalidator
            self.skip_cache_active_change = True
            return ActiveRegionCache(self)

        # the key is either not existing or set to False, we return
        # the real invalidator which re-computes value. We additionally set
        # the flag to actually update the Database objects
        self.skip_cache_active_change = False
        return FreshRegionCache(self)

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.skip_cache_active_change:
            return

        try:
            self.cache_obj.cache_active = True
            Session().add(self.cache_obj)
            Session().commit()
        except IntegrityError:
            # if we catch integrity error, it means we inserted this object
            # assumption is that's really an edge race-condition case and
            # it's safe is to skip it
            Session().rollback()
        except Exception:
            log.exception('Failed to commit on cache key update')
            Session().rollback()
            if self.raise_exception:
                raise
