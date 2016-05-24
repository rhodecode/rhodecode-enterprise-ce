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

import gzip
import shutil
import logging
import tempfile
import urlparse

import rhodecode
from rhodecode.lib.middleware.appenlight import wrap_in_appenlight_if_enabled
from rhodecode.lib.middleware.simplegit import SimpleGit, GIT_PROTO_PAT
from rhodecode.lib.middleware.simplehg import SimpleHg
from rhodecode.lib.middleware.simplesvn import SimpleSvn


log = logging.getLogger(__name__)


def is_git(environ):
    """
    Returns True if requests should be handled by GIT wsgi middleware
    """
    is_git_path = GIT_PROTO_PAT.match(environ['PATH_INFO'])
    log.debug(
        'request path: `%s` detected as GIT PROTOCOL %s', environ['PATH_INFO'],
        is_git_path is not None)

    return is_git_path


def is_hg(environ):
    """
    Returns True if requests target is mercurial server - header
    ``HTTP_ACCEPT`` of such request would start with ``application/mercurial``.
    """
    is_hg_path = False

    http_accept = environ.get('HTTP_ACCEPT')

    if http_accept and http_accept.startswith('application/mercurial'):
        query = urlparse.parse_qs(environ['QUERY_STRING'])
        if 'cmd' in query:
            is_hg_path = True

    log.debug(
        'request path: `%s` detected as HG PROTOCOL %s', environ['PATH_INFO'],
        is_hg_path)

    return is_hg_path


def is_svn(environ):
    """
    Returns True if requests target is Subversion server
    """
    http_dav = environ.get('HTTP_DAV', '')
    is_svn_path = 'subversion' in http_dav
    log.debug(
        'request path: `%s` detected as SVN PROTOCOL %s', environ['PATH_INFO'],
        is_svn_path)

    return is_svn_path


class GunzipMiddleware(object):
    """
    WSGI middleware that unzips gzip-encoded requests before
    passing on to the underlying application.
    """

    def __init__(self, application):
        self.app = application

    def __call__(self, environ, start_response):
        accepts_encoding_header = environ.get('HTTP_CONTENT_ENCODING', b'')

        if b'gzip' in accepts_encoding_header:
            log.debug('gzip detected, now running gunzip wrapper')
            wsgi_input = environ['wsgi.input']

            if not hasattr(environ['wsgi.input'], 'seek'):
                # The gzip implementation in the standard library of Python 2.x
                # requires the '.seek()' and '.tell()' methods to be available
                # on the input stream.  Read the data into a temporary file to
                # work around this limitation.

                wsgi_input = tempfile.SpooledTemporaryFile(64 * 1024 * 1024)
                shutil.copyfileobj(environ['wsgi.input'], wsgi_input)
                wsgi_input.seek(0)

            environ['wsgi.input'] = gzip.GzipFile(fileobj=wsgi_input, mode='r')
            # since we "Ungzipped" the content we say now it's no longer gzip
            # content encoding
            del environ['HTTP_CONTENT_ENCODING']

            # content length has changes ? or i'm not sure
            if 'CONTENT_LENGTH' in environ:
                del environ['CONTENT_LENGTH']
        else:
            log.debug('content not gzipped, gzipMiddleware passing '
                      'request further')
        return self.app(environ, start_response)


class VCSMiddleware(object):

    def __init__(self, app, config, appenlight_client):
        self.application = app
        self.config = config
        self.appenlight_client = appenlight_client

    def _get_handler_app(self, environ):
        app = None
        if is_hg(environ):
            app = SimpleHg(self.application, self.config)

        if is_git(environ):
            app = SimpleGit(self.application, self.config)

        proxy_svn = rhodecode.CONFIG.get(
            'rhodecode_proxy_subversion_http_requests', False)
        if proxy_svn and is_svn(environ):
            app = SimpleSvn(self.application, self.config)

        if app:
            app = GunzipMiddleware(app)
            app, _ = wrap_in_appenlight_if_enabled(
                app, self.config, self.appenlight_client)

        return app

    def __call__(self, environ, start_response):
        # check if we handle one of interesting protocols ?
        vcs_handler = self._get_handler_app(environ)
        if vcs_handler:
            return vcs_handler(environ, start_response)

        return self.application(environ, start_response)
