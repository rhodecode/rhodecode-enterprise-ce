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

import mock
import pytest

from rhodecode.model.gist import GistModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash)


@pytest.mark.usefixtures("testuser_api", "app")
class TestApiDeleteGist(object):
    def test_api_delete_gist(self, gist_util):
        gist_id = gist_util.create_gist().gist_access_id
        id_, params = build_data(self.apikey, 'delete_gist', gistid=gist_id)
        response = api_call(self.app, params)
        expected = {'gist': None, 'msg': 'deleted gist ID:%s' % (gist_id,)}
        assert_ok(id_, expected, given=response.body)

    def test_api_delete_gist_regular_user(self, gist_util):
        gist_id = gist_util.create_gist(
            owner=self.TEST_USER_LOGIN).gist_access_id
        id_, params = build_data(
            self.apikey_regular, 'delete_gist', gistid=gist_id)
        response = api_call(self.app, params)
        expected = {'gist': None, 'msg': 'deleted gist ID:%s' % (gist_id,)}
        assert_ok(id_, expected, given=response.body)

    def test_api_delete_gist_regular_user_no_permission(self, gist_util):
        gist_id = gist_util.create_gist().gist_access_id
        id_, params = build_data(
            self.apikey_regular, 'delete_gist', gistid=gist_id)
        response = api_call(self.app, params)
        expected = 'gist `%s` does not exist' % (gist_id,)
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(GistModel, 'delete', crash)
    def test_api_delete_gist_exception_occurred(self, gist_util):
        gist_id = gist_util.create_gist().gist_access_id
        id_, params = build_data(self.apikey, 'delete_gist', gistid=gist_id)
        response = api_call(self.app, params)
        expected = 'failed to delete gist ID:%s' % (gist_id,)
        assert_error(id_, expected, given=response.body)
