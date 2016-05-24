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

from rhodecode.api.tests.utils import build_data, api_call, assert_error


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetRepoChangeset(object):
    @pytest.mark.parametrize("details", ['basic', 'extended', 'full'])
    def test_get_repo_changeset(self, details, backend):
        commit = backend.repo.get_commit(commit_idx=0)
        __, params = build_data(
            self.apikey, 'get_repo_changeset',
            repoid=backend.repo_name, revision=commit.raw_id,
            details=details,
        )
        response = api_call(self.app, params)
        result = response.json['result']
        assert result['revision'] == 0
        assert result['raw_id'] == commit.raw_id

        if details == 'full':
            assert result['refs']['bookmarks'] == getattr(
                commit, 'bookmarks', [])
            assert result['refs']['branches'] == [commit.branch]
            assert result['refs']['tags'] == commit.tags

    @pytest.mark.parametrize("details", ['basic', 'extended', 'full'])
    def test_get_repo_changeset_bad_type(self, details, backend):
        id_, params = build_data(
            self.apikey, 'get_repo_changeset',
            repoid=backend.repo_name, revision=0,
            details=details,
        )
        response = api_call(self.app, params)
        expected = 'commit_id must be a string value'
        assert_error(id_, expected, given=response.body)

    @pytest.mark.parametrize("details", ['basic', 'extended', 'full'])
    def test_get_repo_changesets(self, details, backend):
        limit = 2
        commit = backend.repo.get_commit(commit_idx=0)
        __, params = build_data(
            self.apikey, 'get_repo_changesets',
            repoid=backend.repo_name, start_rev=commit.raw_id, limit=limit,
            details=details,
        )
        response = api_call(self.app, params)
        result = response.json['result']
        assert result
        assert len(result) == limit
        for x in xrange(limit):
            assert result[x]['revision'] == x

        if details == 'full':
            for x in xrange(limit):
                assert 'bookmarks' in result[x]['refs']
                assert 'branches' in result[x]['refs']
                assert 'tags' in result[x]['refs']

    @pytest.mark.parametrize("details", ['basic', 'extended', 'full'])
    @pytest.mark.parametrize("start_rev, expected_revision", [
        ("0", 0),
        ("10", 10),
        ("20", 20),
        ])
    @pytest.mark.backends("hg", "git")
    def test_get_repo_changesets_commit_range(
            self, details, backend, start_rev, expected_revision):
        limit = 10
        __, params = build_data(
            self.apikey, 'get_repo_changesets',
            repoid=backend.repo_name, start_rev=start_rev, limit=limit,
            details=details,
        )
        response = api_call(self.app, params)
        result = response.json['result']
        assert result
        assert len(result) == limit
        for i in xrange(limit):
            assert result[i]['revision'] == int(expected_revision) + i

    @pytest.mark.parametrize("details", ['basic', 'extended', 'full'])
    @pytest.mark.parametrize("start_rev, expected_revision", [
        ("0", 0),
        ("10", 9),
        ("20", 19),
        ])
    def test_get_repo_changesets_commit_range_svn(
            self, details, backend_svn, start_rev, expected_revision):

        # TODO: johbo: SVN showed a problem here: The parameter "start_rev"
        # in our API allows to pass in a "Commit ID" as well as a
        # "Commit Index". In the case of Subversion it is not possible to
        # distinguish these cases. As a workaround we implemented this
        # behavior which gives a preference to see it as a "Commit ID".

        limit = 10
        __, params = build_data(
            self.apikey, 'get_repo_changesets',
            repoid=backend_svn.repo_name, start_rev=start_rev, limit=limit,
            details=details,
        )
        response = api_call(self.app, params)
        result = response.json['result']
        assert result
        assert len(result) == limit
        for i in xrange(limit):
            assert result[i]['revision'] == int(expected_revision) + i

    @pytest.mark.parametrize("details", ['basic', 'extended', 'full'])
    def test_get_repo_changesets_bad_type(self, details, backend):
        id_, params = build_data(
            self.apikey, 'get_repo_changesets',
            repoid=backend.repo_name, start_rev=0, limit=2,
            details=details,
        )
        response = api_call(self.app, params)
        expected = 'commit_id must be a string value'
        assert_error(id_, expected, given=response.body)
