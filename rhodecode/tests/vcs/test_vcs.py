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

"""
Tests for main module's methods.
"""

import mock
import os
import shutil
import tempfile

import pytest

from rhodecode.lib.vcs import VCSError, get_backend, get_vcs_instance
from rhodecode.lib.vcs.backends.hg import MercurialRepository
from rhodecode.tests import TEST_HG_REPO, TEST_GIT_REPO


pytestmark = pytest.mark.usefixtures("pylonsapp")


def test_get_backend():
    hg = get_backend('hg')
    assert hg == MercurialRepository


def test_alias_detect_hg():
    alias = 'hg'
    path = TEST_HG_REPO
    backend = get_backend(alias)
    repo = backend(path)
    assert 'hg' == repo.alias


def test_alias_detect_git():
    alias = 'git'
    path = TEST_GIT_REPO
    backend = get_backend(alias)
    repo = backend(path)
    assert 'git' == repo.alias


def test_wrong_alias():
    alias = 'wrong_alias'
    with pytest.raises(VCSError):
        get_backend(alias)


def test_get_vcs_instance_by_path(vcs_repo):
    repo = get_vcs_instance(vcs_repo.path)

    assert repo.__class__ == vcs_repo.__class__
    assert repo.path == vcs_repo.path
    assert repo.alias == vcs_repo.alias
    assert repo.name == vcs_repo.name


@mock.patch('rhodecode.lib.vcs.backends.get_scm')
@mock.patch('rhodecode.lib.vcs.backends.get_backend')
def test_get_vcs_instance_by_path_args_passed(
        get_backend_mock, get_scm_mock):
    """
    Test that the arguments passed to ``get_vcs_instance_by_path`` are
    forewarded to the vcs backend class.
    """
    backend = mock.MagicMock()
    get_backend_mock.return_value = backend
    args = ['these-are-test-args', 0, True, None]
    get_vcs_instance(TEST_HG_REPO, *args)

    backend.assert_called_with(*args, repo_path=TEST_HG_REPO)


@mock.patch('rhodecode.lib.vcs.backends.get_scm')
@mock.patch('rhodecode.lib.vcs.backends.get_backend')
def test_get_vcs_instance_by_path_kwargs_passed(
        get_backend_mock, get_scm_mock):
    """
    Test that the keyword arguments passed to ``get_vcs_instance_by_path`` are
    forewarded to the vcs backend class.
    """
    backend = mock.MagicMock()
    get_backend_mock.return_value = backend
    kwargs = {
        'foo': 'these-are-test-args',
        'bar': 0,
        'baz': True,
        'foobar': None
    }
    get_vcs_instance(TEST_HG_REPO, **kwargs)

    backend.assert_called_with(repo_path=TEST_HG_REPO, **kwargs)


def test_get_vcs_instance_by_path_err(request):
    """
    Test that ``get_vcs_instance_by_path`` returns None if a path is passed
    to an empty directory.
    """
    empty_dir = tempfile.mkdtemp(prefix='pytest-empty-dir-')

    def fin():
        shutil.rmtree(empty_dir)
    request.addfinalizer(fin)

    repo = get_vcs_instance(empty_dir)

    assert repo is None


def test_get_vcs_instance_by_path_multiple_repos(request):
    """
    Test that ``get_vcs_instance_by_path`` returns None if a path is passed
    to a directory with multiple repositories.
    """
    empty_dir = tempfile.mkdtemp(prefix='pytest-empty-dir-')
    os.mkdir(os.path.join(empty_dir, '.git'))
    os.mkdir(os.path.join(empty_dir, '.hg'))

    def fin():
        shutil.rmtree(empty_dir)
    request.addfinalizer(fin)

    repo = get_vcs_instance(empty_dir)

    assert repo is None
