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

from rhodecode.model.db import UserLog
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestClosePullRequest(object):
    @pytest.mark.backends("git", "hg")
    def test_api_close_pull_request(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        author = pull_request.user_id
        repo = pull_request.target_repo.repo_id
        id_, params = build_data(
            self.apikey, 'close_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id)
        response = api_call(self.app, params)
        expected = {
            'pull_request_id': pull_request_id,
            'closed': True,
        }
        assert_ok(id_, expected, response.body)
        action = 'user_closed_pull_request:%d' % pull_request_id
        journal = UserLog.query()\
            .filter(UserLog.user_id == author)\
            .filter(UserLog.repository_id == repo)\
            .filter(UserLog.action == action)\
            .all()
        assert len(journal) == 1

    @pytest.mark.backends("git", "hg")
    def test_api_close_pull_request_already_closed_error(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        pull_request_repo = pull_request.target_repo.repo_name
        PullRequestModel().close_pull_request(
            pull_request, pull_request.author)
        id_, params = build_data(
            self.apikey, 'close_pull_request',
            repoid=pull_request_repo, pullrequestid=pull_request_id)
        response = api_call(self.app, params)

        expected = 'pull request `%s` is already closed' % pull_request_id
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_close_pull_request_repo_error(self):
        id_, params = build_data(
            self.apikey, 'close_pull_request',
            repoid=666, pullrequestid=1)
        response = api_call(self.app, params)

        expected = 'repository `666` does not exist'
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_close_pull_request_non_admin_with_userid_error(self,
                                                                pr_util):
        pull_request = pr_util.create_pull_request()
        id_, params = build_data(
            self.apikey_regular, 'close_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id,
            userid=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        expected = 'userid is not the same as your user'
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_close_pull_request_no_perms_to_close(
            self, user_util, pr_util):
        user = user_util.create_user()
        pull_request = pr_util.create_pull_request()

        id_, params = build_data(
            user.api_key, 'close_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id,)
        response = api_call(self.app, params)

        expected = ('pull request `%s` close failed, '
                    'no permission to close.') % pull_request.pull_request_id

        response_json = response.json['error']
        assert response_json == expected
