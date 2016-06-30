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
celery libs for RhodeCode
"""


import socket
import logging

import rhodecode

from os.path import join as jn
from pylons import config

from decorator import decorator

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.config import utils
from rhodecode.lib.utils2 import safe_str, md5_safe, aslist
from rhodecode.lib.pidlock import DaemonLock, LockHeld
from rhodecode.lib.vcs import connect_vcs
from rhodecode.model import meta

log = logging.getLogger(__name__)


class ResultWrapper(object):
    def __init__(self, task):
        self.task = task

    @LazyProperty
    def result(self):
        return self.task


def run_task(task, *args, **kwargs):
    if rhodecode.CELERY_ENABLED:
        celery_is_up = False
        try:
            t = task.apply_async(args=args, kwargs=kwargs)
            log.info('running task %s:%s', t.task_id, task)
            celery_is_up = True
            return t

        except socket.error as e:
            if isinstance(e, IOError) and e.errno == 111:
                log.error('Unable to connect to celeryd. Sync execution')
            else:
                log.exception("Exception while connecting to celeryd.")
        except KeyError as e:
            log.error('Unable to connect to celeryd. Sync execution')
        except Exception as e:
            log.exception(
                "Exception while trying to run task asynchronous. "
                "Fallback to sync execution.")

        # keep in mind there maybe a subtle race condition where something
        # depending on rhodecode.CELERY_ENABLED such as @dbsession decorator
        # will see CELERY_ENABLED as True before this has a chance to set False
        rhodecode.CELERY_ENABLED = celery_is_up
    else:
        log.debug('executing task %s in sync mode', task)
    return ResultWrapper(task(*args, **kwargs))


def __get_lockkey(func, *fargs, **fkwargs):
    params = list(fargs)
    params.extend(['%s-%s' % ar for ar in fkwargs.items()])

    func_name = str(func.__name__) if hasattr(func, '__name__') else str(func)
    _lock_key = func_name + '-' + '-'.join(map(safe_str, params))
    return 'task_%s.lock' % (md5_safe(_lock_key),)


def locked_task(func):
    def __wrapper(func, *fargs, **fkwargs):
        lockkey = __get_lockkey(func, *fargs, **fkwargs)
        lockkey_path = config['app_conf']['cache_dir']

        log.info('running task with lockkey %s' % lockkey)
        try:
            l = DaemonLock(file_=jn(lockkey_path, lockkey))
            ret = func(*fargs, **fkwargs)
            l.release()
            return ret
        except LockHeld:
            log.info('LockHeld')
            return 'Task with key %s already running' % lockkey

    return decorator(__wrapper, func)


def get_session():
    if rhodecode.CELERY_ENABLED:
        utils.initialize_database(config)
    sa = meta.Session()
    return sa


def dbsession(func):
    def __wrapper(func, *fargs, **fkwargs):
        try:
            ret = func(*fargs, **fkwargs)
            return ret
        finally:
            if rhodecode.CELERY_ENABLED and not rhodecode.CELERY_EAGER:
                meta.Session.remove()

    return decorator(__wrapper, func)


def vcsconnection(func):
    def __wrapper(func, *fargs, **fkwargs):
        if rhodecode.CELERY_ENABLED and not rhodecode.CELERY_EAGER:
            backends = config['vcs.backends'] = aslist(
                config.get('vcs.backends', 'hg,git'), sep=',')
            for alias in rhodecode.BACKENDS.keys():
                if alias not in backends:
                    del rhodecode.BACKENDS[alias]
            utils.configure_pyro4(config)
            utils.configure_vcs(config)
            connect_vcs(
                config['vcs.server'],
                utils.get_vcs_server_protocol(config))
        ret = func(*fargs, **fkwargs)
        return ret

    return decorator(__wrapper, func)
