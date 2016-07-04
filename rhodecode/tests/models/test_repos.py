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

import tempfile

import mock
import pytest

from rhodecode.lib.exceptions import AttachedForksError
from rhodecode.lib.utils import make_db_config
from rhodecode.model.db import Repository
from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel
from rhodecode.model.scm import ScmModel
from rhodecode.lib.utils2 import safe_unicode


class TestRepoModel:

    def test_remove_repo(self, backend):
        repo = backend.create_repo()
        Session().commit()
        RepoModel().delete(repo=repo)
        Session().commit()

        repos = ScmModel().repo_scan()

        assert Repository.get_by_repo_name(repo_name=backend.repo_name) is None
        assert repo.repo_name not in repos

    def test_remove_repo_raises_exc_when_attached_forks(self, backend):
        repo = backend.create_repo()
        Session().commit()
        backend.create_fork()
        Session().commit()

        with pytest.raises(AttachedForksError):
            RepoModel().delete(repo=repo)

    def test_remove_repo_delete_forks(self, backend):
        repo = backend.create_repo()
        Session().commit()

        fork = backend.create_fork()
        Session().commit()

        fork_of_fork = backend.create_fork()
        Session().commit()

        RepoModel().delete(repo=repo, forks='delete')
        Session().commit()

        assert Repository.get_by_repo_name(repo_name=repo.repo_name) is None
        assert Repository.get_by_repo_name(repo_name=fork.repo_name) is None
        assert (
            Repository.get_by_repo_name(repo_name=fork_of_fork.repo_name)
            is None)

    def test_remove_repo_detach_forks(self, backend):
        repo = backend.create_repo()
        Session().commit()

        fork = backend.create_fork()
        Session().commit()

        fork_of_fork = backend.create_fork()
        Session().commit()

        RepoModel().delete(repo=repo, forks='detach')
        Session().commit()

        assert Repository.get_by_repo_name(repo_name=repo.repo_name) is None
        assert (
            Repository.get_by_repo_name(repo_name=fork.repo_name) is not None)
        assert (
            Repository.get_by_repo_name(repo_name=fork_of_fork.repo_name)
            is not None)

    @pytest.mark.parametrize("filename, expected", [
        ("README", True),
        ("README.rst", False),
    ])
    def test_filenode_is_link(self, vcsbackend, filename, expected):
        repo = vcsbackend.repo
        assert repo.get_commit().is_link(filename) is expected

    def test_get_commit(self, backend):
        backend.repo.get_commit()

    def test_get_changeset_is_deprecated(self, backend):
        repo = backend.repo
        pytest.deprecated_call(repo.get_changeset)

    def test_clone_url_encrypted_value(self, backend):
        repo = backend.create_repo()
        Session().commit()

        repo.clone_url = 'https://marcink:qweqwe@code.rhodecode.com'
        Session().add(repo)
        Session().commit()

        assert repo.clone_url == 'https://marcink:qweqwe@code.rhodecode.com'

    @pytest.mark.backends("git", "svn")
    def test_create_filesystem_repo_installs_hooks(self, tmpdir, backend):
        hook_methods = {
            'git': 'install_git_hook',
            'svn': 'install_svn_hooks'
        }
        repo = backend.create_repo()
        repo_name = repo.repo_name
        model = RepoModel()
        repo_location = tempfile.mkdtemp()
        model.repos_path = repo_location
        method = hook_methods[backend.alias]
        with mock.patch.object(ScmModel, method) as hooks_mock:
            model._create_filesystem_repo(
                repo_name, backend.alias, repo_group='', clone_uri=None)
        assert hooks_mock.call_count == 1
        hook_args, hook_kwargs = hooks_mock.call_args
        assert hook_args[0].name == repo_name

    @pytest.mark.parametrize("use_global_config, repo_name_passed", [
        (True, False),
        (False, True)
    ])
    def test_per_repo_config_is_generated_during_filesystem_repo_creation(
            self, tmpdir, backend, use_global_config, repo_name_passed):
        repo_name = 'test-{}-repo-{}'.format(backend.alias, use_global_config)
        config = make_db_config()
        model = RepoModel()
        with mock.patch('rhodecode.model.repo.make_db_config') as config_mock:
            config_mock.return_value = config
            model._create_filesystem_repo(
                repo_name, backend.alias, repo_group='', clone_uri=None,
                use_global_config=use_global_config)
        expected_repo_name = repo_name if repo_name_passed else None
        expected_call = mock.call(clear_session=False, repo=expected_repo_name)
        assert expected_call in config_mock.call_args_list

    def test_update_commit_cache_with_config(serf, backend):
        repo = backend.create_repo()
        with mock.patch('rhodecode.model.db.Repository.scm_instance') as scm:
            scm_instance = mock.Mock()
            scm_instance.get_commit.return_value = {
                'raw_id': 40*'0',
                'revision': 1
            }
            scm.return_value = scm_instance
            repo.update_commit_cache()
            scm.assert_called_with(cache=False, config=None)
            config = {'test': 'config'}
            repo.update_commit_cache(config=config)
            scm.assert_called_with(
                cache=False, config=config)


class TestGetUsers(object):
    def test_returns_active_users(self, backend, user_util):
        for i in range(4):
            is_active = i % 2 == 0
            user_util.create_user(active=is_active, lastname='Fake user')

        with mock.patch('rhodecode.lib.helpers.gravatar_url'):
            users = RepoModel().get_users()
        fake_users = [u for u in users if u['last_name'] == 'Fake user']
        assert len(fake_users) == 2

        expected_keys = (
            'id', 'first_name', 'last_name', 'username', 'icon_link',
            'value_display', 'value', 'value_type')
        for user in users:
            assert user['value_type'] is 'user'
            for key in expected_keys:
                assert key in user

    def test_returns_user_filtered_by_last_name(self, backend, user_util):
        keywords = ('aBc', u'ünicode')
        for keyword in keywords:
            for i in range(2):
                user_util.create_user(
                    active=True, lastname=u'Fake {} user'.format(keyword))

        with mock.patch('rhodecode.lib.helpers.gravatar_url'):
            keyword = keywords[1].lower()
            users = RepoModel().get_users(name_contains=keyword)

        fake_users = [u for u in users if u['last_name'].startswith('Fake')]
        assert len(fake_users) == 2
        for user in fake_users:
            assert user['last_name'] == safe_unicode('Fake ünicode user')

    def test_returns_user_filtered_by_first_name(self, backend, user_util):
        created_users = []
        keywords = ('aBc', u'ünicode')
        for keyword in keywords:
            for i in range(2):
                created_users.append(user_util.create_user(
                    active=True, lastname='Fake user',
                    firstname=u'Fake {} user'.format(keyword)))

        keyword = keywords[1].lower()
        with mock.patch('rhodecode.lib.helpers.gravatar_url'):
            users = RepoModel().get_users(name_contains=keyword)

        fake_users = [u for u in users if u['last_name'].startswith('Fake')]
        assert len(fake_users) == 2
        for user in fake_users:
            assert user['first_name'] == safe_unicode('Fake ünicode user')

    def test_returns_user_filtered_by_username(self, backend, user_util):
        created_users = []
        for i in range(5):
            created_users.append(user_util.create_user(
                active=True, lastname='Fake user'))

        user_filter = created_users[-1].username[-2:]
        with mock.patch('rhodecode.lib.helpers.gravatar_url'):
            users = RepoModel().get_users(name_contains=user_filter)

        fake_users = [u for u in users if u['last_name'].startswith('Fake')]
        assert len(fake_users) == 1
        assert fake_users[0]['username'] == created_users[-1].username

    def test_returns_limited_user_list(self, backend, user_util):
        created_users = []
        for i in range(5):
            created_users.append(user_util.create_user(
                active=True, lastname='Fake user'))

        with mock.patch('rhodecode.lib.helpers.gravatar_url'):
            users = RepoModel().get_users(name_contains='Fake', limit=3)

        fake_users = [u for u in users if u['last_name'].startswith('Fake')]
        assert len(fake_users) == 3


class TestGetUserGroups(object):
    def test_returns_filtered_list(self, backend, user_util):
        created_groups = []
        for i in range(4):
            created_groups.append(
                user_util.create_user_group(users_group_active=True))

        group_filter = created_groups[-1].users_group_name[-2:]
        with self._patch_user_group_list():
            groups = RepoModel().get_user_groups(group_filter)

        fake_groups = [
            u for u in groups if u['value'].startswith('test_returns')]
        assert len(fake_groups) == 1
        assert fake_groups[0]['value'] == created_groups[-1].users_group_name
        assert fake_groups[0]['value_display'].startswith(
            'Group: test_returns')

    def test_returns_limited_list(self, backend, user_util):
        created_groups = []
        for i in range(3):
            created_groups.append(
                user_util.create_user_group(users_group_active=True))

        with self._patch_user_group_list():
            groups = RepoModel().get_user_groups('test_returns')

        fake_groups = [
            u for u in groups if u['value'].startswith('test_returns')]
        assert len(fake_groups) == 3

    def test_returns_active_user_groups(self, backend, user_util):
        for i in range(4):
            is_active = i % 2 == 0
            user_util.create_user_group(users_group_active=is_active)

        with self._patch_user_group_list():
            groups = RepoModel().get_user_groups()
        expected = ('id', 'icon_link', 'value_display', 'value', 'value_type')
        for group in groups:
            assert group['value_type'] is 'user_group'
            for key in expected:
                assert key in group

        fake_groups = [
            u for u in groups if u['value'].startswith('test_returns')]
        assert len(fake_groups) == 2
        for user in fake_groups:
            assert user['value_display'].startswith('Group: test_returns')

    def _patch_user_group_list(self):
        def side_effect(group_list, perm_set):
            return group_list
        return mock.patch(
            'rhodecode.model.repo.UserGroupList', side_effect=side_effect)
