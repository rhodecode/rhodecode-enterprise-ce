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

from rhodecode.model.db import ChangesetStatus
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestCommentCommit(object):
    def test_api_comment_commit_on_empty_repo(self, backend):
        repo = backend.create_repo()
        id_, params = build_data(
            self.apikey, 'comment_commit', repoid=repo.repo_name,
            commit_id='tip', message='message', status_change=None)
        response = api_call(self.app, params)
        expected = 'failed to set comment on repository `%s`' % repo.repo_name
        assert_error(id_, expected, given=response.body)

    @pytest.mark.parametrize("status_change, message, commit_id", [
        (None, 'Hallo', 'tip'),
        (ChangesetStatus.STATUS_APPROVED, 'Approved', 'tip'),
        (ChangesetStatus.STATUS_REJECTED, 'Rejected', 'tip'),
    ])
    def test_api_comment_commit(
            self, backend, status_change, message, commit_id,
            no_notifications):
        id_, params = build_data(
            self.apikey, 'comment_commit', repoid=backend.repo_name,
            commit_id=commit_id, message=message, status=status_change)
        response = api_call(self.app, params)
        repo = backend.repo.scm_instance()
        expected = {
            'msg': 'Commented on commit `%s` for repository `%s`' % (
                repo.get_changeset().raw_id, backend.repo_name),
            'status_change': status_change,
            'success': True
        }
        assert_ok(id_, expected, given=response.body)
