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
Test suite for making push/pull operations, on specially modified INI files

.. important::

   You must have git >= 1.8.5 for tests to work fine. With 68b939b git started
   to redirect things to stderr instead of stdout.
"""


import pytest

from rhodecode.model.db import User, Repository
from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel

from rhodecode.tests import (
    GIT_REPO, HG_REPO, TEST_USER_ADMIN_LOGIN, TEST_USER_REGULAR_LOGIN,
    TEST_USER_REGULAR_PASS)
from rhodecode.tests.other.vcs_operations import (
    Command, _check_proper_clone, _check_proper_git_push, _add_files_and_push)


# override rc_web_server_config fixture with custom INI
@pytest.fixture(scope='module')
def rc_web_server_config(testini_factory):
    CUSTOM_PARAMS = [
        {'app:main': {'lock_ret_code': '423'}},
    ]
    return testini_factory(CUSTOM_PARAMS)


@pytest.mark.usefixtures("disable_locking")
class TestVCSOperationsOnCustomIniConfig:

    def test_clone_and_create_lock_hg(self, rc_web_server, tmpdir):
        # enable locking
        r = Repository.get_by_repo_name(HG_REPO)
        r.enable_locking = True
        Session().add(r)
        Session().commit()
        # clone
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)

        # check if lock was made
        r = Repository.get_by_repo_name(HG_REPO)
        assert r.locked[0] == User.get_by_username(
            TEST_USER_ADMIN_LOGIN).user_id

    def test_clone_and_create_lock_git(self, rc_web_server, tmpdir):
        # enable locking
        r = Repository.get_by_repo_name(GIT_REPO)
        r.enable_locking = True
        Session().add(r)
        Session().commit()
        # clone
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)

        # check if lock was made
        r = Repository.get_by_repo_name(GIT_REPO)
        assert r.locked[0] == User.get_by_username(
            TEST_USER_ADMIN_LOGIN).user_id

    def test_clone_after_repo_was_locked_hg(self, rc_web_server, tmpdir):
        # lock repo
        r = Repository.get_by_repo_name(HG_REPO)
        Repository.lock(r, User.get_by_username(TEST_USER_ADMIN_LOGIN).user_id)
        # pull fails since repo is locked
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        msg = ("""abort: HTTP Error 423: Repository `%s` locked by user `%s`"""
               % (HG_REPO, TEST_USER_ADMIN_LOGIN))
        assert msg in stderr

    def test_clone_after_repo_was_locked_git(self, rc_web_server, tmpdir):
        # lock repo
        r = Repository.get_by_repo_name(GIT_REPO)
        Repository.lock(r, User.get_by_username(TEST_USER_ADMIN_LOGIN).user_id)
        # pull fails since repo is locked
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)

        lock_msg = (
            'remote: ERROR: Repository `vcs_test_git` locked by user ' +
            '`test_admin`. Reason:`lock_auto`')
        assert lock_msg in stderr
        assert 'remote: Pre pull hook failed: aborting' in stderr
        assert 'fatal: remote did not send all necessary objects' in stderr

    def test_push_on_locked_repo_by_other_user_hg(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)

        # lock repo
        r = Repository.get_by_repo_name(HG_REPO)
        # let this user actually push !
        RepoModel().grant_user_permission(repo=r, user=TEST_USER_REGULAR_LOGIN,
                                          perm='repository.write')
        Session().commit()
        Repository.lock(r, User.get_by_username(TEST_USER_ADMIN_LOGIN).user_id)

        # push fails repo is locked by other user !
        push_url = rc_web_server.repo_clone_url(
            HG_REPO,
            user=TEST_USER_REGULAR_LOGIN, passwd=TEST_USER_REGULAR_PASS)
        stdout, stderr = _add_files_and_push(
            'hg', tmpdir.strpath, clone_url=push_url)
        msg = ("""abort: HTTP Error 423: Repository `%s` locked by user `%s`"""
               % (HG_REPO, TEST_USER_ADMIN_LOGIN))
        assert msg in stderr

    def test_push_on_locked_repo_by_other_user_git(
            self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)

        # lock repo
        r = Repository.get_by_repo_name(GIT_REPO)
        # let this user actually push !
        RepoModel().grant_user_permission(repo=r, user=TEST_USER_REGULAR_LOGIN,
                                          perm='repository.write')
        Session().commit()
        Repository.lock(r, User.get_by_username(TEST_USER_ADMIN_LOGIN).user_id)

        # push fails repo is locked by other user!
        push_url = rc_web_server.repo_clone_url(
            GIT_REPO,
            user=TEST_USER_REGULAR_LOGIN, passwd=TEST_USER_REGULAR_PASS)
        stdout, stderr = _add_files_and_push(
            'git', tmpdir.strpath, clone_url=push_url)

        err = 'Repository `%s` locked by user `%s`' % (
            GIT_REPO, TEST_USER_ADMIN_LOGIN)
        # err = 'RPC failed; result=22, HTTP code = 423'
        assert err in stderr

    def test_push_unlocks_repository_hg(self, rc_web_server, tmpdir):
        # enable locking
        r = Repository.get_by_repo_name(HG_REPO)
        r.enable_locking = True
        Session().add(r)
        Session().commit()

        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'hg')

        # check for lock repo after clone
        r = Repository.get_by_repo_name(HG_REPO)
        uid = User.get_by_username(TEST_USER_ADMIN_LOGIN).user_id
        assert r.locked[0] == uid

        # push is ok and repo is now unlocked
        stdout, stderr = _add_files_and_push(
            'hg', tmpdir.strpath, clone_url=clone_url)
        assert ('remote: Released lock on repo `%s`' % HG_REPO) in stdout
        # we need to cleanup the Session Here !
        Session.remove()
        r = Repository.get_by_repo_name(HG_REPO)
        assert r.locked == [None, None, None]

    def test_push_unlocks_repository_git(self, rc_web_server, tmpdir):

        # Note: Did a first debugging session. Seems that
        # Repository.get_locking_state is called twice. The second call
        # has the action "pull" and does not reset the lock.

        # enable locking
        r = Repository.get_by_repo_name(GIT_REPO)
        r.enable_locking = True
        Session().add(r)
        Session().commit()

        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'git')

        # check for lock repo after clone
        r = Repository.get_by_repo_name(GIT_REPO)
        assert r.locked[0] == User.get_by_username(
            TEST_USER_ADMIN_LOGIN).user_id

        # push is ok and repo is now unlocked
        stdout, stderr = _add_files_and_push(
            'git', tmpdir.strpath, clone_url=clone_url)
        _check_proper_git_push(stdout, stderr)

        # assert ('remote: Released lock on repo `%s`' % GIT_REPO) in stdout
        # we need to cleanup the Session Here !
        Session.remove()
        r = Repository.get_by_repo_name(GIT_REPO)
        assert r.locked == [None, None, None]
