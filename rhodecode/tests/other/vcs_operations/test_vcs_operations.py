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


import os
import time

import pytest

from rhodecode.lib.vcs.backends.git.repository import GitRepository
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.model.db import Repository, UserIpMap, CacheKey
from rhodecode.model.meta import Session
from rhodecode.model.user import UserModel
from rhodecode.tests import (GIT_REPO, HG_REPO, TEST_USER_ADMIN_LOGIN)

from rhodecode.tests.other.vcs_operations import (
    Command, _check_proper_clone, _check_proper_git_push, _add_files_and_push,
    HG_REPO_WITH_GROUP, GIT_REPO_WITH_GROUP)


@pytest.mark.usefixtures("disable_locking")
class TestVCSOperations:

    def test_clone_hg_repo_by_admin(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'hg')

    def test_clone_git_repo_by_admin(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        cmd = Command('/tmp')
        stdout, stderr = cmd.execute('git clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'git')
        cmd.assert_returncode_success()

    def test_clone_hg_repo_by_id_by_admin(self, rc_web_server, tmpdir):
        repo_id = Repository.get_by_repo_name(HG_REPO).repo_id
        clone_url = rc_web_server.repo_clone_url('_%s' % repo_id)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'hg')

    def test_clone_git_repo_by_id_by_admin(self, rc_web_server, tmpdir):
        repo_id = Repository.get_by_repo_name(GIT_REPO).repo_id
        clone_url = rc_web_server.repo_clone_url('_%s' % repo_id)
        cmd = Command('/tmp')
        stdout, stderr = cmd.execute('git clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'git')
        cmd.assert_returncode_success()

    def test_clone_hg_repo_with_group_by_admin(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO_WITH_GROUP)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'hg')

    def test_clone_git_repo_with_group_by_admin(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO_WITH_GROUP)
        cmd = Command('/tmp')
        stdout, stderr = cmd.execute('git clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'git')
        cmd.assert_returncode_success()

    def test_clone_git_repo_shallow_by_admin(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        cmd = Command('/tmp')
        stdout, stderr = cmd.execute(
            'git clone --depth=1', clone_url, tmpdir.strpath)

        assert '' == stdout
        assert 'Cloning into' in stderr
        cmd.assert_returncode_success()

    def test_clone_wrong_credentials_hg(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO, passwd='bad!')
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        assert 'abort: authorization failed' in stderr

    def test_clone_wrong_credentials_git(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO, passwd='bad!')
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)
        assert 'fatal: Authentication failed' in stderr

    def test_clone_git_dir_as_hg(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        assert 'HTTP Error 404: Not Found' in stderr

    def test_clone_hg_repo_as_git(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)
        assert 'not found' in stderr

    def test_clone_non_existing_path_hg(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url('trololo')
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        assert 'HTTP Error 404: Not Found' in stderr

    def test_clone_non_existing_path_git(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url('trololo')
        stdout, stderr = Command('/tmp').execute('git clone', clone_url)
        assert 'not found' in stderr

    def test_clone_existing_path_hg_not_in_database(
            self, rc_web_server, tmpdir, fs_repo_only):

        db_name = fs_repo_only('not-in-db-hg', repo_type='hg')
        clone_url = rc_web_server.repo_clone_url(db_name)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        assert 'HTTP Error 404: Not Found' in stderr

    def test_clone_existing_path_git_not_in_database(
            self, rc_web_server, tmpdir, fs_repo_only):
        db_name = fs_repo_only('not-in-db-git', repo_type='git')
        clone_url = rc_web_server.repo_clone_url(db_name)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)
        assert 'not found' in stderr

    def test_clone_existing_path_hg_not_in_database_different_scm(
            self, rc_web_server, tmpdir, fs_repo_only):
        db_name = fs_repo_only('not-in-db-git', repo_type='git')
        clone_url = rc_web_server.repo_clone_url(db_name)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        assert 'HTTP Error 404: Not Found' in stderr

    def test_clone_existing_path_git_not_in_database_different_scm(
            self, rc_web_server, tmpdir, fs_repo_only):
        db_name = fs_repo_only('not-in-db-hg', repo_type='hg')
        clone_url = rc_web_server.repo_clone_url(db_name)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)
        assert 'not found' in stderr

    def test_push_new_file_hg(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)

        stdout, stderr = _add_files_and_push(
            'hg', tmpdir.strpath, clone_url=clone_url)

        assert 'pushing to' in stdout
        assert 'size summary' in stdout

    def test_push_new_file_git(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)

        # commit some stuff into this repo
        stdout, stderr = _add_files_and_push(
            'git', tmpdir.strpath, clone_url=clone_url)

        _check_proper_git_push(stdout, stderr)

    def test_push_invalidates_cache_hg(self, rc_web_server, tmpdir):
        key = CacheKey.query().filter(CacheKey.cache_key == HG_REPO).scalar()
        if not key:
            key = CacheKey(HG_REPO, HG_REPO)

        key.cache_active = True
        Session().add(key)
        Session().commit()

        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)

        stdout, stderr = _add_files_and_push(
            'hg', tmpdir.strpath, clone_url=clone_url, files_no=1)

        key = CacheKey.query().filter(CacheKey.cache_key == HG_REPO).one()
        assert key.cache_active is False

    def test_push_invalidates_cache_git(self, rc_web_server, tmpdir):
        key = CacheKey.query().filter(CacheKey.cache_key == GIT_REPO).scalar()
        if not key:
            key = CacheKey(GIT_REPO, GIT_REPO)

        key.cache_active = True
        Session().add(key)
        Session().commit()

        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)

        # commit some stuff into this repo
        stdout, stderr = _add_files_and_push(
            'git', tmpdir.strpath, clone_url=clone_url, files_no=1)
        _check_proper_git_push(stdout, stderr)

        key = CacheKey.query().filter(CacheKey.cache_key == GIT_REPO).one()

        assert key.cache_active is False

    def test_push_wrong_credentials_hg(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)

        push_url = rc_web_server.repo_clone_url(
            HG_REPO, user='bad', passwd='name')
        stdout, stderr = _add_files_and_push(
            'hg', tmpdir.strpath, clone_url=push_url)

        assert 'abort: authorization failed' in stderr

    def test_push_wrong_credentials_git(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)

        push_url = rc_web_server.repo_clone_url(
            GIT_REPO, user='bad', passwd='name')
        stdout, stderr = _add_files_and_push(
            'git', tmpdir.strpath, clone_url=push_url)

        assert 'fatal: Authentication failed' in stderr

    def test_push_back_to_wrong_url_hg(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO)
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)

        stdout, stderr = _add_files_and_push(
            'hg', tmpdir.strpath,
            clone_url=rc_web_server.repo_clone_url('not-existing'))

        assert 'HTTP Error 404: Not Found' in stderr

    def test_push_back_to_wrong_url_git(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO)
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)

        stdout, stderr = _add_files_and_push(
            'git', tmpdir.strpath,
            clone_url=rc_web_server.repo_clone_url('not-existing'))

        assert 'not found' in stderr

    def test_ip_restriction_hg(self, rc_web_server, tmpdir):
        user_model = UserModel()
        try:
            user_model.add_extra_ip(TEST_USER_ADMIN_LOGIN, '10.10.10.10/32')
            Session().commit()
            time.sleep(2)
            clone_url = rc_web_server.repo_clone_url(HG_REPO)
            stdout, stderr = Command('/tmp').execute(
                'hg clone', clone_url, tmpdir.strpath)
            assert 'abort: HTTP Error 403: Forbidden' in stderr
        finally:
            # release IP restrictions
            for ip in UserIpMap.getAll():
                UserIpMap.delete(ip.ip_id)
            Session().commit()

        time.sleep(2)

        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        _check_proper_clone(stdout, stderr, 'hg')

    def test_ip_restriction_git(self, rc_web_server, tmpdir):
        user_model = UserModel()
        try:
            user_model.add_extra_ip(TEST_USER_ADMIN_LOGIN, '10.10.10.10/32')
            Session().commit()
            time.sleep(2)
            clone_url = rc_web_server.repo_clone_url(GIT_REPO)
            stdout, stderr = Command('/tmp').execute(
                'git clone', clone_url, tmpdir.strpath)
            msg = "The requested URL returned error: 403"
            assert msg in stderr
        finally:
            # release IP restrictions
            for ip in UserIpMap.getAll():
                UserIpMap.delete(ip.ip_id)
            Session().commit()

        time.sleep(2)

        cmd = Command('/tmp')
        stdout, stderr = cmd.execute('git clone', clone_url, tmpdir.strpath)
        cmd.assert_returncode_success()
        _check_proper_clone(stdout, stderr, 'git')


def test_git_sets_default_branch_if_not_master(
        backend_git, tmpdir, disable_locking, rc_web_server):
    empty_repo = backend_git.create_repo()
    clone_url = rc_web_server.repo_clone_url(empty_repo.repo_name)

    cmd = Command(tmpdir.strpath)
    cmd.execute('git clone', clone_url)

    repo = GitRepository(os.path.join(tmpdir.strpath, empty_repo.repo_name))
    repo.in_memory_commit.add(FileNode('file', content=''))
    repo.in_memory_commit.commit(
        message='Commit on branch test',
        author='Automatic test',
        branch='test')

    repo_cmd = Command(repo.path)
    stdout, stderr = repo_cmd.execute('git push --verbose origin test')
    _check_proper_git_push(
        stdout, stderr, branch='test', should_set_default_branch=True)

    stdout, stderr = cmd.execute(
        'git clone', clone_url, empty_repo.repo_name + '-clone')
    _check_proper_clone(stdout, stderr, 'git')

    # Doing an explicit commit in order to get latest user logs on MySQL
    Session().commit()


def test_git_fetches_from_remote_repository_with_annotated_tags(
        backend_git, disable_locking, rc_web_server):
    # Note: This is a test specific to the git backend. It checks the
    # integration of fetching from a remote repository which contains
    # annotated tags.

    # Dulwich shows this specific behavior only when
    # operating against a remote repository.
    source_repo = backend_git['annotated-tag']
    target_vcs_repo = backend_git.create_repo().scm_instance()
    target_vcs_repo.fetch(rc_web_server.repo_clone_url(source_repo.repo_name))
