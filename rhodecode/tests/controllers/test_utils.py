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

from rhodecode.controllers import utils
from rhodecode.lib.vcs.exceptions import RepositoryError
import mock


@pytest.mark.parametrize('alias, expected', [
    ('hg', [None, 'name']),
    ('git', [None, 'name']),
    ('svn', ['name', 'raw_id']),
])
def test_parse_path_ref_understands_format_ref_id_result(alias, expected):
    repo = mock.Mock(alias=alias)

    # Formatting of reference ids as it is used by controllers
    format_ref_id = utils.get_format_ref_id(repo)
    formatted_ref_id = format_ref_id(name='name', raw_id='raw_id')

    # Parsing such a reference back as it is used by controllers
    result = utils.parse_path_ref(formatted_ref_id)

    assert list(result) == expected


@pytest.mark.parametrize('ref, default_path, expected', [
    ('a', None, (None, 'a')),
    ('a', 'path', ('path', 'a')),
    ('p@a', 'path', ('p', 'a')),
    ('p@a', None, ('p', 'a')),
])
def test_parse_path_ref(ref, default_path, expected):
    result = utils.parse_path_ref(ref, default_path)
    assert list(result) == list(expected)


@pytest.mark.parametrize('alias, expected', [
    ('hg', 'name'),
    ('git', 'name'),
    ('svn', 'name@raw_id'),
])
def test_format_ref_id(alias, expected):
    repo = mock.Mock(alias=alias)
    format_ref_id = utils.get_format_ref_id(repo)
    result = format_ref_id(name='name', raw_id='raw_id')
    assert result == expected


class TestGetCommit(object):
    @pytest.mark.parametrize('ref_type', [None, 'book', 'tag', 'branch'])
    def test_get_commit_from_ref_name_found(self, ref_type):
        ref_name = 'a_None_id'
        repo = mock.Mock()
        scm_instance = repo.scm_instance()
        scm_instance.branches = {ref_name: 'a_branch_id'}
        scm_instance.tags = {ref_name: 'a_tag_id'}
        scm_instance.bookmarks = {ref_name: 'a_book_id'}

        scm_instance.get_commit.return_value = 'test'
        commit = utils.get_commit_from_ref_name(repo, ref_name, ref_type)
        scm_instance.get_commit.assert_called_once_with('a_%s_id' % ref_type)
        assert commit == 'test'

    @pytest.mark.parametrize('ref_type', ['book', 'tag', 'branch'])
    def test_get_commit_from_ref_name_not_found(self, ref_type):
        ref_name = 'invalid_ref'
        repo = mock.Mock()
        scm_instance = repo.scm_instance()
        repo.scm_instance().branches = {}
        repo.scm_instance().tags = {}
        repo.scm_instance().bookmarks = {}
        with pytest.raises(RepositoryError):
            utils.get_commit_from_ref_name(repo, ref_name, ref_type)
