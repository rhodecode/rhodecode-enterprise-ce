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

import logging
import textwrap

import routes.middleware
import urlobject
import webob
import webob.exc

import rhodecode.lib.auth


log = logging.getLogger(__name__)


class CSRFDetector(object):
    """
    Middleware for preventing CSRF.


    It checks that all requests are either GET or POST.
    For POST requests, it logs the requests that do not have a CSRF token.
    Eventually it will raise an error.

    It special cases some endpoints as they do not really require a token.

    Note: this middleware is only intended for testing.
    """

    _PUT_DELETE_MESSAGE = textwrap.dedent('''
        Do not call in tests app.delete or app.put, use instead
        app.post(..., params={'_method': 'delete'}.

        The reason is twofold. The first is because that's how the browser is
        calling rhodecode and the second is because it allow us to detect
        potential CSRF.''').strip()

    _PATHS_WITHOUT_TOKEN = frozenset((
        # The password is the token.
        '/_admin/login',
        # Captcha may be enabled.
        '/_admin/password_reset',
        # Captcha may be enabled.
        '/_admin/password_reset_confirmation',
        # Captcha may be enabled.
        '/_admin/register',
        # No change in state with this controller.
        '/error/document',
    ))

    def __init__(self, app):
        self._app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'].upper() not in ('GET', 'POST'):
            raise Exception(self._PUT_DELETE_MESSAGE)

        if (environ['REQUEST_METHOD'] == 'POST' and
                environ['PATH_INFO'] not in self._PATHS_WITHOUT_TOKEN and
                routes.middleware.is_form_post(environ)):
            body = environ['wsgi.input']
            if body.seekable():
                pos = body.tell()
                content = body.read()
                body.seek(pos)
            elif hasattr(body, 'peek'):
                content = body.peek()
            else:
                raise Exception("Cannot check if the request has a CSRF token")
            if rhodecode.lib.auth.csrf_token_key not in content:
                raise Exception(
                    '%s to %s does not have a csrf_token %r' %
                    (environ['REQUEST_METHOD'], environ['PATH_INFO'], content))

        return self._app(environ, start_response)


def _get_scheme_host_port(url):
    url = urlobject.URLObject(url)
    if '://' not in url:
        return None, url, None

    scheme = url.scheme or 'http'
    port = url.port
    if not port:
        if scheme == 'http':
            port = 80
        elif scheme == 'https':
            port = 443
    host = url.netloc.without_port()

    return scheme, host, port


def _equivalent_urls(url1, url2):
    """Check if both urls are equivalent."""
    return _get_scheme_host_port(url1) == _get_scheme_host_port(url2)


class OriginChecker(object):
    """
    Check whether the request has a valid Origin header.

    See https://wiki.mozilla.org/Security/Origin for details.
    """

    def __init__(self, app, expected_origin, skip_urls=None):
        """
        :param expected_origin: the value we expect to see for the Origin
                                header.
        :param skip_urls: list of urls for which we do not need to check the
                          Origin header.
        """
        self._app = app
        self._expected_origin = expected_origin
        self._skip_urls = frozenset(skip_urls or [])

    def __call__(self, environ, start_response):
        origin_header = environ.get('HTTP_ORIGIN', '')
        origin = origin_header.split(' ', 1)[0]
        if origin == 'null':
            origin = None

        if (environ['PATH_INFO'] not in self._skip_urls and origin and
                not _equivalent_urls(origin, self._expected_origin)):
            log.warn(
                'Invalid Origin header detected: got %s, expected %s',
                origin_header, self._expected_origin)
            return webob.exc.HTTPForbidden('Origin header mismatch')(
                environ, start_response)
        else:
            return self._app(environ, start_response)
