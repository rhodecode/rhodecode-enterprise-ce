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

import os
import shutil

import pytest

from rhodecode.lib.vcs import VCSError, get_repo, get_backend
from rhodecode.lib.vcs.backends.hg import MercurialRepository
from rhodecode.tests import TEST_HG_REPO, TEST_GIT_REPO, TESTS_TMP_PATH


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


def test_get_repo():
    alias = 'hg'
    path = TEST_HG_REPO
    backend = get_backend(alias)
    repo = backend(path)

    assert repo.__class__, get_repo(path == alias).__class__
    assert repo.path, get_repo(path == alias).path


def test_get_repo_autoalias_hg():
    alias = 'hg'
    path = TEST_HG_REPO
    backend = get_backend(alias)
    repo = backend(path)

    assert repo.__class__ == get_repo(path).__class__
    assert repo.path == get_repo(path).path


def test_get_repo_autoalias_git():
    alias = 'git'
    path = TEST_GIT_REPO
    backend = get_backend(alias)
    repo = backend(path)

    assert repo.__class__ == get_repo(path).__class__
    assert repo.path == get_repo(path).path


def test_get_repo_err():
    blank_repo_path = os.path.join(TESTS_TMP_PATH, 'blank-error-repo')
    if os.path.isdir(blank_repo_path):
        shutil.rmtree(blank_repo_path)

    os.mkdir(blank_repo_path)
    pytest.raises(VCSError, get_repo, blank_repo_path)
    pytest.raises(VCSError, get_repo, blank_repo_path + 'non_existing')


def test_get_repo_multialias():
    multialias_repo_path = os.path.join(TESTS_TMP_PATH, 'hg-git-repo')
    if os.path.isdir(multialias_repo_path):
        shutil.rmtree(multialias_repo_path)

    os.mkdir(multialias_repo_path)

    os.mkdir(os.path.join(multialias_repo_path, '.git'))
    os.mkdir(os.path.join(multialias_repo_path, '.hg'))
    pytest.raises(VCSError, get_repo, multialias_repo_path)
