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

from __future__ import unicode_literals

import time

from whoosh import index
import mock
import pytest

import rhodecode
from rhodecode.lib.auth import AuthUser
from rhodecode.lib.index import whoosh, searcher_from_config


@pytest.mark.parametrize("name_suffix", [
    "",
    "UpPeRcAsE",
])
def test_search_finds_results(
        tmpdir, backend_random, user_regular, name_suffix):
    repo = backend_random.create_repo(name_suffix=name_suffix)

    search_location = tmpdir.strpath
    create_commit_index_with_one_document(
        search_location, repo_name=repo.repo_name)

    auth_user = AuthUser(user_id=user_regular.user_id)
    with mock.patch.dict(rhodecode.CONFIG,
                         {'search.location': search_location}):
        searcher = searcher_from_config(rhodecode.CONFIG)

    search_result = searcher.search(
        "Test", document_type='commit', search_user=auth_user, repo_name=None)
    results = list(search_result['results'])
    assert len(results) == 1
    assert results[0]['repository'] == repo.repo_name


def create_commit_index_with_one_document(search_location, repo_name):
    """
    Provides a test index based on our search schema.

    The full details of index creation are found inside of `rhodecode-tools`.
    The intention of this function is to provide just enough so that the
    search works.
    """
    test_index = index.create_in(
        search_location, whoosh.COMMIT_SCHEMA,
        indexname=whoosh.COMMIT_INDEX_NAME)
    writer = test_index.writer()

    writer.add_document(
        commit_id="fake_commit_id",
        commit_idx=1,
        owner="Test Owner",
        date=time.time(),
        repository=repo_name,
        author="Test Author",
        message="Test Message",
        added="added_1.txt added_2.txt",
        removed="removed_1.txt removed_2.txt",
        changed="changed_1.txt changed_2.txt",
        parents="fake_parent_1_id fake_parent_2_id",
        )
    writer.commit()
