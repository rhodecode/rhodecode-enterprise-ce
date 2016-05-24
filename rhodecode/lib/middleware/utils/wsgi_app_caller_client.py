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
Utility to call a WSGI app wrapped in a WSGIAppCaller object.
"""

import logging

from Pyro4.errors import ConnectionClosedError


log = logging.getLogger(__name__)


def _get_clean_environ(environ):
    """Return a copy of the WSGI environment without wsgi.* keys.

    It also omits any non-string values.

    :param environ: WSGI environment to clean
    :type environ: dict

    :returns: WSGI environment to pass to WSGIAppCaller.handle.
    :rtype: dict
    """
    clean_environ = dict(
        (k, v) for k, v in environ.iteritems()
        if type(v) == str and type(k) == str and not k.startswith('wsgi.')
    )

    return clean_environ


# pylint: disable=too-few-public-methods
class RemoteAppCaller(object):
    """Create and calls a remote WSGI app using the given factory.

    It first cleans the environment, so as to reduce the data transferred.
    """

    def __init__(self, remote_wsgi, *args, **kwargs):
        """
        :param remote_wsgi: The remote wsgi object that creates a
          WSGIAppCaller. This object
          has to have a handle method, with the signature:
          handle(environ, start_response, *args, **kwargs)
        :param args: args to be passed to the app creation
        :param kwargs: kwargs to be passed to the app creation
        """
        self._remote_wsgi = remote_wsgi
        self._args = args
        self._kwargs = kwargs

    def __call__(self, environ, start_response):
        """
        :param environ: WSGI environment with which the app will be run
        :type environ: dict
        :param start_response: callable of WSGI protocol
        :type start_response: callable

        :returns: an iterable with the data returned by the app
        :rtype: iterable<str>
        """
        log.debug("Forwarding WSGI request via proxy %s", self._remote_wsgi)
        input_data = environ['wsgi.input'].read()
        clean_environ = _get_clean_environ(environ)

        try:
            data, status, headers = self._remote_wsgi.handle(
                clean_environ, input_data, *self._args, **self._kwargs)
        except ConnectionClosedError:
            log.debug('Remote Pyro Server ConnectionClosedError')
            self._remote_wsgi._pyroReconnect(tries=15)
            data, status, headers = self._remote_wsgi.handle(
                clean_environ, input_data, *self._args, **self._kwargs)

        log.debug("Got result from proxy, returning to WSGI container")
        start_response(status, headers)

        return data
