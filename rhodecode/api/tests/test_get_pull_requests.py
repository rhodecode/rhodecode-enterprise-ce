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

from rhodecode.model.meta import Session
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetPullRequest(object):
    @pytest.mark.backends("git", "hg")
    def test_api_get_pull_requests(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request_2 = PullRequestModel().create(
            created_by=pull_request.author,
            source_repo=pull_request.source_repo,
            source_ref=pull_request.source_ref,
            target_repo=pull_request.target_repo,
            target_ref=pull_request.target_ref,
            revisions=pull_request.revisions,
            reviewers=(),
            title=pull_request.title,
            description=pull_request.description,
        )
        Session().commit()
        id_, params = build_data(
            self.apikey, 'get_pull_requests',
            repoid=pull_request.target_repo.repo_name)
        response = api_call(self.app, params)
        assert response.status == '200 OK'
        assert len(response.json['result']) == 2

        PullRequestModel().close_pull_request(
            pull_request_2, pull_request_2.author)
        Session().commit()

        id_, params = build_data(
            self.apikey, 'get_pull_requests',
            repoid=pull_request.target_repo.repo_name,
            status='new')
        response = api_call(self.app, params)
        assert response.status == '200 OK'
        assert len(response.json['result']) == 1

        id_, params = build_data(
            self.apikey, 'get_pull_requests',
            repoid=pull_request.target_repo.repo_name,
            status='closed')
        response = api_call(self.app, params)
        assert response.status == '200 OK'
        assert len(response.json['result']) == 1

    @pytest.mark.backends("git", "hg")
    def test_api_get_pull_requests_repo_error(self):
        id_, params = build_data(self.apikey, 'get_pull_requests', repoid=666)
        response = api_call(self.app, params)

        expected = 'repository `666` does not exist'
        assert_error(id_, expected, given=response.body)
