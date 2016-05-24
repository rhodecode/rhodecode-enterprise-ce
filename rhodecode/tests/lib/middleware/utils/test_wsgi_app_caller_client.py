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

import webtest

from rhodecode.lib.middleware.utils import wsgi_app_caller_client

# pylint: disable=protected-access,too-many-public-methods


BASE_ENVIRON = {
    'REQUEST_METHOD': 'GET',
    'SERVER_NAME': 'localhost',
    'SERVER_PORT': '80',
    'SCRIPT_NAME': '',
    'PATH_INFO': '/',
    'QUERY_STRING': '',
    'foo.bool_var': True,
    'foo.str_var': 'True',
    'wsgi.foo': True,
    # Some non string values. The validator expects to get an iterable as
    # value.
    (42,): '42',
    (True,): 'False',
}


def assert_all_values_are_str(environ):
    """Checks that all values of a dict are str."""
    for key, value in environ.iteritems():
        assert isinstance(value, str), (
            "Value for key %s: has type %s but 'str' was expected. Value: %s" %
            (key, type(value), repr(value)))


def assert_all_keys_are_str(environ):
    """Checks that all keys of a dict are str."""
    for key, value in environ.iteritems():
        assert isinstance(value, str), (
            "Key %s: has type %s but 'str' was expected. " %
            (repr(key), type(key)))


def assert_no_prefix_in_keys(environ, prefix):
    """Checks that no key of the dict starts with the prefix."""
    for key in environ:
        assert not key.startswith(prefix), 'Key %s should not be present' % key


def test_get_environ():
    clean_environ = wsgi_app_caller_client._get_clean_environ(BASE_ENVIRON)

    assert len(clean_environ) == 7
    assert_no_prefix_in_keys(clean_environ, 'wsgi.')
    assert_all_keys_are_str(clean_environ)
    assert_all_values_are_str(clean_environ)


def test_remote_app_caller():

    class RemoteAppCallerMock(object):

        def handle(self, environ, input_data, arg1, arg2,
                   arg3=None, arg4=None, arg5=None):
            assert ((arg1, arg2, arg3, arg4, arg5) ==
                    ('a1', 'a2', 'a3', 'a4', None))
            # Note: RemoteAppCaller is expected to return a tuple like the
            # following one
            return (['content'], '200 OK', [('Content-Type', 'text/plain')])

    wrapper_app = wsgi_app_caller_client.RemoteAppCaller(
        RemoteAppCallerMock(), 'a1', 'a2', arg3='a3', arg4='a4')

    test_app = webtest.TestApp(wrapper_app)

    response = test_app.get('/path')

    assert response.status == '200 OK'
    assert response.headers.items() == [
        ('Content-Type', 'text/plain'), ('Content-Length', '7')]
    assert response.body == 'content'
