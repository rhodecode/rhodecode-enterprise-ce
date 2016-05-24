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

import pytest

from rhodecode.api.utils import Optional, OAttr
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestApi(object):
    maxDiff = None

    def test_Optional_object(self):

        option1 = Optional(None)
        assert '<Optional:%s>' % (None,) == repr(option1)
        assert option1() is None

        assert 1 == Optional.extract(Optional(1))
        assert 'example' == Optional.extract('example')

    def test_Optional_OAttr(self):
        option1 = Optional(OAttr('apiuser'))
        assert 'apiuser' == Optional.extract(option1)

    def test_OAttr_object(self):
        oattr1 = OAttr('apiuser')
        assert '<OptionalAttr:apiuser>' == repr(oattr1)
        assert oattr1() == oattr1

    def test_api_wrong_key(self):
        id_, params = build_data('trololo', 'get_user')
        response = api_call(self.app, params)

        expected = 'Invalid API KEY'
        assert_error(id_, expected, given=response.body)

    def test_api_missing_non_optional_param(self):
        id_, params = build_data(self.apikey, 'get_repo')
        response = api_call(self.app, params)

        expected = 'Missing non optional `repoid` arg in JSON DATA'
        assert_error(id_, expected, given=response.body)

    def test_api_missing_non_optional_param_args_null(self):
        id_, params = build_data(self.apikey, 'get_repo')
        params = params.replace('"args": {}', '"args": null')
        response = api_call(self.app, params)

        expected = 'Missing non optional `repoid` arg in JSON DATA'
        assert_error(id_, expected, given=response.body)

    def test_api_missing_non_optional_param_args_bad(self):
        id_, params = build_data(self.apikey, 'get_repo')
        params = params.replace('"args": {}', '"args": 1')
        response = api_call(self.app, params)

        expected = 'Missing non optional `repoid` arg in JSON DATA'
        assert_error(id_, expected, given=response.body)

    def test_api_non_existing_method(self, request):
        id_, params = build_data(self.apikey, 'not_existing', args='xx')
        response = api_call(self.app, params)
        expected = 'No such method: not_existing'
        assert_error(id_, expected, given=response.body)

    def test_api_disabled_user(self, request):

        def set_active(active):
            from rhodecode.model.db import Session, User
            user = User.get_by_auth_token(self.apikey)
            user.active = active
            Session().add(user)
            Session().commit()

        request.addfinalizer(lambda: set_active(True))

        set_active(False)
        id_, params = build_data(self.apikey, 'test', args='xx')
        response = api_call(self.app, params)
        expected = 'Request from this user not allowed'
        assert_error(id_, expected, given=response.body)

    def test_api_args_is_null(self):
        __, params = build_data(self.apikey, 'get_users', )
        params = params.replace('"args": {}', '"args": null')
        response = api_call(self.app, params)
        assert response.status == '200 OK'

    def test_api_args_is_bad(self):
        __, params = build_data(self.apikey, 'get_users', )
        params = params.replace('"args": {}', '"args": 1')
        response = api_call(self.app, params)
        assert response.status == '200 OK'

    def test_api_args_different_args(self):
        import string
        expected = {
            'ascii_letters': string.ascii_letters,
            'ws': string.whitespace,
            'printables': string.printable
        }
        id_, params = build_data(self.apikey, 'test', args=expected)
        response = api_call(self.app, params)
        assert response.status == '200 OK'
        assert_ok(id_, expected, response.body)
