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
middleware to handle https correctly
"""


from rhodecode.lib.utils2 import str2bool


class HttpsFixup(object):

    def __init__(self, app, config):
        self.application = app
        self.config = config

    def __call__(self, environ, start_response):
        self.__fixup(environ)
        debug = str2bool(self.config.get('debug'))
        is_ssl = environ['wsgi.url_scheme'] == 'https'

        def custom_start_response(status, headers, exc_info=None):
            if is_ssl and str2bool(self.config.get('use_htsts')) and not debug:
                headers.append(('Strict-Transport-Security',
                                'max-age=8640000; includeSubDomains'))
            return start_response(status, headers, exc_info)

        return self.application(environ, custom_start_response)

    def __fixup(self, environ):
        """
        Function to fixup the environ as needed. In order to use this
        middleware you should set this header inside your
        proxy ie. nginx, apache etc.
        """
        # DETECT PROTOCOL !
        if 'HTTP_X_URL_SCHEME' in environ:
            proto = environ.get('HTTP_X_URL_SCHEME')
        elif 'HTTP_X_FORWARDED_SCHEME' in environ:
            proto = environ.get('HTTP_X_FORWARDED_SCHEME')
        elif 'HTTP_X_FORWARDED_PROTO' in environ:
            proto = environ.get('HTTP_X_FORWARDED_PROTO')
        else:
            proto = 'http'
        org_proto = proto

        # if we have force, just override
        if str2bool(self.config.get('force_https')):
            proto = 'https'

        environ['wsgi.url_scheme'] = proto
        environ['wsgi._org_proto'] = org_proto
