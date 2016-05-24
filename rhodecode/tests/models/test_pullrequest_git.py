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

from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.lib.vcs.exceptions import CommitDoesNotExistError
from rhodecode.model.pull_request import PullRequestModel


@pytest.mark.backends('git')
class TestGetDiffForPrOrVersion(object):

    def test_works_for_missing_git_references(self, pr_util):
        pull_request = self._prepare_pull_request(pr_util)
        removed_commit_id = pr_util.remove_one_commit()
        self.assert_commit_cannot_be_accessed(removed_commit_id, pull_request)

        self.assert_diff_can_be_fetched(pull_request)

    def test_works_for_missing_git_references_during_update(self, pr_util):
        pull_request = self._prepare_pull_request(pr_util)
        removed_commit_id = pr_util.remove_one_commit()
        self.assert_commit_cannot_be_accessed(removed_commit_id, pull_request)

        pr_version = PullRequestModel().get_versions(pull_request)[0]
        self.assert_diff_can_be_fetched(pr_version)

    def _prepare_pull_request(self, pr_util):
        commits = [
            {'message': 'a'},
            {'message': 'b', 'added': [FileNode('file_b', 'test_content\n')]},
            {'message': 'c', 'added': [FileNode('file_c', 'test_content\n')]},
        ]
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='c',
            revisions=['b', 'c'])
        return pull_request

    def assert_diff_can_be_fetched(self, pr_or_version):
        diff = PullRequestModel()._get_diff_from_pr_or_version(
            pr_or_version, context=6)
        assert 'file_b' in diff.raw

    def assert_commit_cannot_be_accessed(
            self, removed_commit_id, pull_request):
        source_vcs = pull_request.source_repo.scm_instance()
        with pytest.raises(CommitDoesNotExistError):
            source_vcs.get_commit(commit_id=removed_commit_id)
