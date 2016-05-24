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

from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, expected_permissions)


@pytest.mark.usefixtures("testuser_api", "app")
class TestApiGetRepoGroup(object):
    def test_api_get_repo_group(self, user_util):
        repo_group = user_util.create_repo_group()
        repo_group_name = repo_group.group_name

        id_, params = build_data(
            self.apikey, 'get_repo_group', repogroupid=repo_group_name)
        response = api_call(self.app, params)

        repo_group = RepoGroupModel()._get_repo_group(repo_group_name)
        ret = repo_group.get_api_data()

        permissions = expected_permissions(repo_group)

        ret['members'] = permissions
        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_get_repo_group_not_existing(self):
        id_, params = build_data(
            self.apikey, 'get_repo_group', repogroupid='no-such-repo-group')
        response = api_call(self.app, params)

        ret = 'repository group `%s` does not exist' % 'no-such-repo-group'
        expected = ret
        assert_error(id_, expected, given=response.body)
