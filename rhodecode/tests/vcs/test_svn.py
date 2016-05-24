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

import os

import mock
import pytest

from rhodecode.tests import SVN_REPO, TEST_DIR, TESTS_TMP_PATH
from rhodecode.lib.vcs.backends.svn.repository import SubversionRepository
from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import VCSError


pytestmark = [
    pytest.mark.backends("svn"),
    pytest.mark.usefixtures("pylonsapp"),
]


@pytest.fixture
def repo(pylonsapp):
    repo = SubversionRepository(os.path.join(TESTS_TMP_PATH, SVN_REPO))
    return repo


@pytest.fixture
def head(repo):
    return repo.get_commit()


def test_init_fails_if_path_does_not_exist():
    path = os.path.join(TEST_DIR, 'i-do-not-exist')
    with pytest.raises(VCSError):
        SubversionRepository(path)


def test_init_fails_if_path_is_not_a_valid_repository(tmpdir):
    path = unicode(tmpdir.mkdir(u'unicode ä'))
    with pytest.raises(VCSError):
        SubversionRepository(path)


def test_repo_clone(vcsbackend, reposerver):
    source = vcsbackend.create_repo(number_of_commits=3)
    reposerver.serve(source)
    repo = SubversionRepository(
        vcsbackend.new_repo_path(),
        create=True,
        src_url=reposerver.url)

    assert source.commit_ids == repo.commit_ids
    assert source[0].message == repo[0].message


def test_latest_commit(head):
    assert head.raw_id == '393'


def test_commit_description(head):
    assert head.message == """Added a symlink"""


def test_commit_author(head):
    assert head.author == 'marcin'


@pytest.mark.parametrize("filename, content, mime_type", [
    ('test.txt', 'Text content\n', None),
    ('test.bin', '\0 binary \0', 'application/octet-stream'),
], ids=['text', 'binary'])
def test_sets_mime_type_correctly(vcsbackend, filename, content, mime_type):
    repo = vcsbackend.create_repo()
    vcsbackend.ensure_file(filename, content)
    file_properties = repo._remote.node_properties(filename, 1)
    assert file_properties.get('svn:mime-type') == mime_type


def test_slice_access(repo):
    page_size = 5
    page = 0
    start = page * page_size
    end = start + page_size - 1

    commits = list(repo[start:end])
    assert [commit.raw_id for commit in commits] == ['1', '2', '3', '4']


def test_walk_changelog_page(repo):
    page_size = 5
    page = 0
    start = page * page_size
    end = start + page_size - 1

    commits = list(repo[start:end])
    changelog = [
        'r%s, %s, %s' % (c.raw_id, c.author, c.message) for c in commits]

    expexted_messages = [
        'r1, marcin, initial import',
        'r2, marcin, hg ignore',
        'r3, marcin, Pip standards refactor',
        'r4, marcin, Base repository few new functions added']
    assert changelog == expexted_messages


def test_read_full_file_tree(head):
    for topnode, dirs, files in head.walk():
        for f in files:
            len(f.content)


def test_topnode_files_attribute(head):
    topnode = head.get_node('')
    topnode.files


@pytest.mark.parametrize("filename, content, branch, mime_type", [
    (u'branches/plain/test.txt', 'Text content\n', 'plain', None),
    (u'branches/uniçö∂e/test.bin', '\0 binary \0', u'uniçö∂e',
        'application/octet-stream'),
], ids=['text', 'binary'])
def test_unicode_refs(vcsbackend, filename, content, branch, mime_type):
    repo = vcsbackend.create_repo()
    vcsbackend.ensure_file(filename, content)
    with mock.patch(("rhodecode.lib.vcs.backends.svn.repository"
                    ".SubversionRepository._patterns_from_section"),
                    return_value=['branches/*']):
        assert u'branches/{0}'.format(branch) in repo.branches


def test_compatible_version(monkeypatch, vcsbackend):
    monkeypatch.setattr(settings, 'SVN_COMPATIBLE_VERSION', 'pre-1.8-compatible')
    path = vcsbackend.new_repo_path()
    SubversionRepository(path, create=True)
    with open('{}/db/format'.format(path)) as f:
        first_line = f.readline().strip()
        assert first_line == '4'


def test_invalid_compatible_version(monkeypatch, vcsbackend):
    monkeypatch.setattr(settings, 'SVN_COMPATIBLE_VERSION', 'i-am-an-invalid-setting')
    path = vcsbackend.new_repo_path()
    with pytest.raises(Exception):
        SubversionRepository(path, create=True)


class TestSVNCommit(object):

    @pytest.fixture(autouse=True)
    def prepare(self, repo):
        self.repo = repo

    def test_file_history_from_commits(self):
        node = self.repo[10].get_node('setup.py')
        commit_ids = [commit.raw_id for commit in node.history]
        assert ['8'] == commit_ids

        node = self.repo[20].get_node('setup.py')
        node_ids = [commit.raw_id for commit in node.history]
        assert ['18',
                '8'] == node_ids

        # special case we check history from commit that has this particular
        # file changed this means we check if it's included as well
        node = self.repo.get_commit('18').get_node('setup.py')
        node_ids = [commit.raw_id for commit in node.history]
        assert ['18',
                '8'] == node_ids
