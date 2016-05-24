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

import shutil
import time
import datetime

import pytest

from rhodecode.lib.vcs.backends import get_backend
from rhodecode.lib.vcs.backends.base import Config
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.tests import get_new_dir
from rhodecode.tests.utils import check_skip_backends, check_xfail_backends
from rhodecode.tests.vcs.base import BackendTestMixin


@pytest.fixture()
def vcs_repository_support(
        request, backend_alias, pylonsapp, _vcs_repo_container):
    """
    Provide a test repository for the test run.

    Depending on the value of `recreate_repo_per_test` a new repo for each
    test will be created.

    The parameter `--backends` can be used to limit this fixture to specific
    backend implementations.
    """
    cls = request.cls

    check_skip_backends(request.node, backend_alias)
    check_xfail_backends(request.node, backend_alias)

    if _should_create_repo_per_test(cls):
        _vcs_repo_container = _create_vcs_repo_container(request)

    repo = _vcs_repo_container.get_repo(cls, backend_alias=backend_alias)

    # TODO: johbo: Supporting old test class api, think about removing this
    cls.repo = repo
    cls.repo_path = repo.path
    cls.default_branch = repo.DEFAULT_BRANCH_NAME
    cls.Backend = cls.backend_class = repo.__class__
    cls.imc = repo.in_memory_commit

    return (backend_alias, repo)


@pytest.fixture(scope='class')
def _vcs_repo_container(request):
    """
    Internal fixture intended to help support class based scoping on demand.
    """
    return _create_vcs_repo_container(request)


def _create_vcs_repo_container(request):
    repo_container = VcsRepoContainer()
    if not request.config.getoption('--keep-tmp-path'):
        request.addfinalizer(repo_container.cleanup)
    return repo_container


class VcsRepoContainer(object):

    def __init__(self):
        self._cleanup_paths = []
        self._repos = {}

    def get_repo(self, test_class, backend_alias):
        if backend_alias not in self._repos:
            repo = _create_empty_repository(test_class, backend_alias)
            self._cleanup_paths.append(repo.path)
            self._repos[backend_alias] = repo
        return self._repos[backend_alias]

    def cleanup(self):
        for repo_path in reversed(self._cleanup_paths):
            shutil.rmtree(repo_path)


def _should_create_repo_per_test(cls):
    return getattr(cls, 'recreate_repo_per_test', False)


def _create_empty_repository(cls, backend_alias=None):
    Backend = get_backend(backend_alias or cls.backend_alias)
    repo_path = get_new_dir(str(time.time()))
    repo = Backend(repo_path, create=True)
    if hasattr(cls, '_get_commits'):
        cls.tip = _add_commits_to_repo(repo, cls._get_commits())

    return repo


@pytest.fixture
def config():
    """
    Instance of a repository config.

    The instance contains only one value:

    - Section: "section-a"
    - Key:     "a-1"
    - Value:   "value-a-1"

    The intended usage is for cases where a config instance is needed but no
    specific content is required.
    """
    config = Config()
    config.set('section-a', 'a-1', 'value-a-1')
    return config


def _add_commits_to_repo(repo, commits):
    imc = repo.in_memory_commit
    commit = None

    for commit in commits:
        for node in commit.get('added', []):
            imc.add(FileNode(node.path, content=node.content))
        for node in commit.get('changed', []):
            imc.change(FileNode(node.path, content=node.content))
        for node in commit.get('removed', []):
            imc.remove(FileNode(node.path))

        commit = imc.commit(
            message=unicode(commit['message']),
            author=unicode(commit['author']),
            date=commit['date'],
            branch=commit.get('branch'))

    return commit


@pytest.fixture
def vcs_repo(request, backend_alias):
    Backend = get_backend(backend_alias)
    repo_path = get_new_dir(str(time.time()))
    repo = Backend(repo_path, create=True)

    @request.addfinalizer
    def cleanup():
        shutil.rmtree(repo_path)

    return repo


@pytest.fixture
def generate_repo_with_commits(vcs_repo):
    """
    Creates a fabric to generate N comits with some file nodes on a randomly
    generated repository
    """

    def commit_generator(num):
        start_date = datetime.datetime(2010, 1, 1, 20)
        for x in xrange(num):
            yield {
                'message': 'Commit %d' % x,
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': start_date + datetime.timedelta(hours=12 * x),
                'added': [
                    FileNode('file_%d.txt' % x, content='Foobar %d' % x),
                ],
                'modified': [
                    FileNode('file_%d.txt' % x,
                             content='Foobar %d modified' % (x-1)),
                ]
            }

    def commit_maker(num=5):
        _add_commits_to_repo(vcs_repo, commit_generator(num))
        return vcs_repo

    return commit_maker


@pytest.fixture
def hg_repo(request, vcs_repo):
    repo = vcs_repo

    commits = BackendTestMixin._get_commits()
    _add_commits_to_repo(repo, commits)

    return repo


@pytest.fixture
def hg_commit(hg_repo):
    return hg_repo.get_commit()
