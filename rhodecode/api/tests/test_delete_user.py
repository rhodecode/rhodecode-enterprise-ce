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

from rhodecode.model.user import UserModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, crash)


@pytest.mark.usefixtures("testuser_api", "app")
class TestDeleteUser(object):
    def test_api_delete_user(self, user_util):
        usr = user_util.create_user(auto_cleanup=False)

        username = usr.username
        usr_id = usr.user_id

        id_, params = build_data(self.apikey, 'delete_user', userid=username)
        response = api_call(self.app, params)

        ret = {'msg': 'deleted user ID:%s %s' % (usr_id, username),
               'user': None}
        expected = ret
        assert_ok(id_, expected, given=response.body)

    @mock.patch.object(UserModel, 'delete', crash)
    def test_api_delete_user_when_exception_happened(self, user_util):
        usr = user_util.create_user()
        username = usr.username

        id_, params = build_data(
            self.apikey, 'delete_user', userid=username, )
        response = api_call(self.app, params)
        ret = 'failed to delete user ID:%s %s' % (usr.user_id,
                                                  usr.username)
        expected = ret
        assert_error(id_, expected, given=response.body)
