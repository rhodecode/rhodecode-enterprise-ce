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

import wsgiref.simple_server

import pytest
import webtest

from rhodecode.lib.middleware import csrf


def test_origin_checker_no_origin():
    app = csrf.OriginChecker(
        wsgiref.simple_server.demo_app, 'https://safe.org')
    app = webtest.TestApp(app)

    app.post('/foo')


def test_origin_checker_null_origin():
    app = csrf.OriginChecker(
        wsgiref.simple_server.demo_app, 'https://safe.org')
    app = webtest.TestApp(app)

    app.post('/foo', headers={'Origin': 'null'})


@pytest.mark.parametrize('origin', [
    'http://safe.org',
    'http://safe.org:80',
    'http://safe.org http://redirect',
])
def test_origin_checker_valid_origin(origin):
    app = csrf.OriginChecker(
        wsgiref.simple_server.demo_app, 'http://safe.org')
    app = webtest.TestApp(app)

    app.post('/foo', headers={'Origin': origin})


@pytest.mark.parametrize('origin', [
    'https://safe.org',
    'https://safe.org:443',
    'https://safe.org https://redirect',
])
def test_origin_checker_valid_origin_https(origin):
    app = csrf.OriginChecker(
        wsgiref.simple_server.demo_app, 'https://safe.org')
    app = webtest.TestApp(app)

    app.post('/foo', headers={'Origin': origin})


@pytest.mark.parametrize('origin', [
    'http://www.evil.org',
    'https://www.evil.org',
    'foo',
])
def test_origin_checker_invalid_origin(origin):
    app = csrf.OriginChecker(
        wsgiref.simple_server.demo_app, 'https://safe.org')
    app = webtest.TestApp(app)

    app.post('/foo', headers={'Origin': origin}, status=403)


def test_origin_checker_invalid_origin_skipped_url():
    app = csrf.OriginChecker(
        wsgiref.simple_server.demo_app, 'https://safe.org', skip_urls=['/foo'])
    app = webtest.TestApp(app)

    app.post('/foo', headers={'Origin': 'http://www.evil.org'})
