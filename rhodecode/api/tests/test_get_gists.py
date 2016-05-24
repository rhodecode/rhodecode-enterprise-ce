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

from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestApiGetGist(object):
    def test_api_get_gists(self, gist_util):
        gist_util.create_gist()
        gist_util.create_gist()

        id_, params = build_data(self.apikey, 'get_gists')
        response = api_call(self.app, params)
        assert len(response.json['result']) == 2

    def test_api_get_gists_regular_user(self, gist_util):
        # by admin
        gist_util.create_gist()
        gist_util.create_gist()

        # by reg user
        gist_util.create_gist(owner=self.TEST_USER_LOGIN)
        gist_util.create_gist(owner=self.TEST_USER_LOGIN)
        gist_util.create_gist(owner=self.TEST_USER_LOGIN)

        id_, params = build_data(self.apikey_regular, 'get_gists')
        response = api_call(self.app, params)
        assert len(response.json['result']) == 3

    def test_api_get_gists_only_for_regular_user(self, gist_util):
        # by admin
        gist_util.create_gist()
        gist_util.create_gist()

        # by reg user
        gist_util.create_gist(owner=self.TEST_USER_LOGIN)
        gist_util.create_gist(owner=self.TEST_USER_LOGIN)
        gist_util.create_gist(owner=self.TEST_USER_LOGIN)

        id_, params = build_data(
            self.apikey, 'get_gists', userid=self.TEST_USER_LOGIN)
        response = api_call(self.app, params)
        assert len(response.json['result']) == 3

    def test_api_get_gists_regular_user_with_different_userid(self):
        id_, params = build_data(
            self.apikey_regular, 'get_gists',
            userid=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)
        expected = 'userid is not the same as your user'
        assert_error(id_, expected, given=response.body)
