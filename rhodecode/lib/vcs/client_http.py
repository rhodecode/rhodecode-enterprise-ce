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

"""
Client for the VCSServer implemented based on HTTP.


Status
------

This client implementation shall eventually replace the Pyro4 based
implementation.
"""

import copy
import logging
import threading
import urllib2
import urlparse
import uuid

import msgpack
import requests

from . import exceptions, CurlSession


log = logging.getLogger(__name__)


# TODO: mikhail: Keep it in sync with vcsserver's
# HTTPApplication.ALLOWED_EXCEPTIONS
EXCEPTIONS_MAP = {
    'KeyError': KeyError,
    'URLError': urllib2.URLError,
}


class RepoMaker(object):

    def __init__(self, server_and_port, backend_endpoint, session):
        self.url = urlparse.urljoin(
            'http://%s' % server_and_port, backend_endpoint)
        self._session = session

    def __call__(self, path, config, with_wire=None):
        log.debug('RepoMaker call on %s', path)
        return RemoteRepo(
            path, config, self.url, self._session, with_wire=with_wire)

    def __getattr__(self, name):
        def f(*args, **kwargs):
            return self._call(name, *args, **kwargs)
        return f

    @exceptions.map_vcs_exceptions
    def _call(self, name, *args, **kwargs):
        payload = {
            'id': str(uuid.uuid4()),
            'method': name,
            'params': {'args': args, 'kwargs': kwargs}
        }
        return _remote_call(self.url, payload, EXCEPTIONS_MAP, self._session)


class RemoteRepo(object):

    def __init__(self, path, config, url, session, with_wire=None):
        self.url = url
        self._session = session
        self._wire = {
            "path": path,
            "config": config,
            "context": str(uuid.uuid4()),
        }
        if with_wire:
            self._wire.update(with_wire)

        # johbo: Trading complexity for performance. Avoiding the call to
        # log.debug brings a few percent gain even if is is not active.
        if log.isEnabledFor(logging.DEBUG):
            self._call = self._call_with_logging

    def __getattr__(self, name):
        def f(*args, **kwargs):
            return self._call(name, *args, **kwargs)
        return f

    @exceptions.map_vcs_exceptions
    def _call(self, name, *args, **kwargs):
        # TODO: oliver: This is currently necessary pre-call since the
        # config object is being changed for hooking scenarios
        wire = copy.deepcopy(self._wire)
        wire["config"] = wire["config"].serialize()
        payload = {
            'id': str(uuid.uuid4()),
            'method': name,
            'params': {'wire': wire, 'args': args, 'kwargs': kwargs}
        }
        return _remote_call(self.url, payload, EXCEPTIONS_MAP, self._session)

    def _call_with_logging(self, name, *args, **kwargs):
        log.debug('Calling %s@%s', self.url, name)
        return RemoteRepo._call(self, name, *args, **kwargs)

    def __getitem__(self, key):
        return self.revision(key)


class RemoteObject(object):

    def __init__(self, url, session):
        self._url = url
        self._session = session

        # johbo: Trading complexity for performance. Avoiding the call to
        # log.debug brings a few percent gain even if is is not active.
        if log.isEnabledFor(logging.DEBUG):
            self._call = self._call_with_logging

    def __getattr__(self, name):
        def f(*args, **kwargs):
            return self._call(name, *args, **kwargs)
        return f

    @exceptions.map_vcs_exceptions
    def _call(self, name, *args, **kwargs):
        payload = {
            'id': str(uuid.uuid4()),
            'method': name,
            'params': {'args': args, 'kwargs': kwargs}
        }
        return _remote_call(self._url, payload, EXCEPTIONS_MAP, self._session)

    def _call_with_logging(self, name, *args, **kwargs):
        log.debug('Calling %s@%s', self._url, name)
        return RemoteObject._call(self, name, *args, **kwargs)


def _remote_call(url, payload, exceptions_map, session):
    response = session.post(url, data=msgpack.packb(payload))
    response = msgpack.unpackb(response.content)
    error = response.get('error')
    if error:
        type_ = error.get('type', 'Exception')
        exc = exceptions_map.get(type_, Exception)
        exc = exc(error.get('message'))
        try:
            exc._vcs_kind = error['_vcs_kind']
        except KeyError:
            pass
        raise exc
    return response.get('result')


class VcsHttpProxy(object):

    CHUNK_SIZE = 16384

    def __init__(self, server_and_port, backend_endpoint):
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.base_url = urlparse.urljoin(
            'http://%s' % server_and_port, backend_endpoint)
        self.session = requests.Session()
        self.session.mount('http://', adapter)

    def handle(self, environment, input_data, *args, **kwargs):
        data = {
            'environment': environment,
            'input_data': input_data,
            'args': args,
            'kwargs': kwargs
        }
        result = self.session.post(
            self.base_url, msgpack.packb(data), stream=True)
        return self._get_result(result)

    def _deserialize_and_raise(self, error):
        exception = Exception(error['message'])
        try:
            exception._vcs_kind = error['_vcs_kind']
        except KeyError:
            pass
        raise exception

    def _iterate(self, result):
        unpacker = msgpack.Unpacker()
        for line in result.iter_content(chunk_size=self.CHUNK_SIZE):
            unpacker.feed(line)
            for chunk in unpacker:
                yield chunk

    def _get_result(self, result):
        iterator = self._iterate(result)
        error = iterator.next()
        if error:
            self._deserialize_and_raise(error)

        status = iterator.next()
        headers = iterator.next()

        return iterator, status, headers


class ThreadlocalSessionFactory(object):
    """
    Creates one CurlSession per thread on demand.
    """

    def __init__(self):
        self._thread_local = threading.local()

    def __call__(self):
        if not hasattr(self._thread_local, 'curl_session'):
            self._thread_local.curl_session = CurlSession()
        return self._thread_local.curl_session
