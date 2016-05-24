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
from hashlib import sha1

import pytest
from mock import patch

from rhodecode.lib import auth
from rhodecode.lib.utils2 import md5
from rhodecode.model.db import User
from rhodecode.model.repo import RepoModel
from rhodecode.model.user import UserModel
from rhodecode.model.user_group import UserGroupModel


def test_cached_perms_data(user_regular, backend_random):
    permissions = get_permissions(user_regular)
    repo_name = backend_random.repo.repo_name
    expected_global_permissions = {
        'repository.read', 'group.read', 'usergroup.read'}
    assert expected_global_permissions.issubset(permissions['global'])
    assert permissions['repositories'][repo_name] == 'repository.read'


def test_cached_perms_data_with_admin_user(user_regular, backend_random):
    permissions = get_permissions(user_regular, user_is_admin=True)
    repo_name = backend_random.repo.repo_name
    assert 'hg.admin' in permissions['global']
    assert permissions['repositories'][repo_name] == 'repository.admin'


def test_cached_perms_data_user_group_global_permissions(user_util):
    user, user_group = user_util.create_user_with_group()
    user_group.inherit_default_permissions = False

    granted_permission = 'repository.write'
    UserGroupModel().grant_perm(user_group, granted_permission)

    permissions = get_permissions(user)
    assert granted_permission in permissions['global']


@pytest.mark.xfail(reason="Not implemented, see TODO note")
def test_cached_perms_data_user_group_global_permissions_(user_util):
    user, user_group = user_util.create_user_with_group()

    granted_permission = 'repository.write'
    UserGroupModel().grant_perm(user_group, granted_permission)

    permissions = get_permissions(user)
    assert granted_permission in permissions['global']


def test_cached_perms_data_user_global_permissions(user_util):
    user = user_util.create_user()
    UserModel().grant_perm(user, 'repository.none')

    permissions = get_permissions(user, user_inherit_default_permissions=True)
    assert 'repository.read' in permissions['global']


def test_cached_perms_data_repository_permissions_on_private_repository(
        backend_random, user_util):
    user, user_group = user_util.create_user_with_group()

    repo = backend_random.create_repo()
    repo.private = True

    granted_permission = 'repository.write'
    RepoModel().grant_user_group_permission(
        repo, user_group.users_group_name, granted_permission)

    permissions = get_permissions(user)
    assert permissions['repositories'][repo.repo_name] == granted_permission


def test_cached_perms_data_repository_permissions_for_owner(
        backend_random, user_util):
    user = user_util.create_user()

    repo = backend_random.create_repo()
    repo.user_id = user.user_id

    permissions = get_permissions(user)
    assert permissions['repositories'][repo.repo_name] == 'repository.admin'

    # TODO: johbo: Make cleanup in UserUtility smarter, then remove this hack
    repo.user_id = User.get_default_user().user_id


def test_cached_perms_data_repository_permissions_not_inheriting_defaults(
        backend_random, user_util):
    user = user_util.create_user()
    repo = backend_random.create_repo()

    # Don't inherit default object permissions
    UserModel().grant_perm(user, 'hg.inherit_default_perms.false')

    permissions = get_permissions(user)
    assert permissions['repositories'][repo.repo_name] == 'repository.none'


def test_cached_perms_data_default_permissions_on_repository_group(user_util):
    # Have a repository group with default permissions set
    repo_group = user_util.create_repo_group()
    default_user = User.get_default_user()
    user_util.grant_user_permission_to_repo_group(
        repo_group, default_user, 'repository.write')
    user = user_util.create_user()

    permissions = get_permissions(user)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'repository.write'


def test_cached_perms_data_default_permissions_on_repository_group_owner(
        user_util):
    # Have a repository group
    repo_group = user_util.create_repo_group()
    default_user = User.get_default_user()

    # Add a permission for the default user to hit the code path
    user_util.grant_user_permission_to_repo_group(
        repo_group, default_user, 'repository.write')

    # Have an owner of the group
    user = user_util.create_user()
    repo_group.user_id = user.user_id

    permissions = get_permissions(user)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.admin'


def test_cached_perms_data_default_permissions_on_repository_group_no_inherit(
        user_util):
    # Have a repository group
    repo_group = user_util.create_repo_group()
    default_user = User.get_default_user()

    # Add a permission for the default user to hit the code path
    user_util.grant_user_permission_to_repo_group(
        repo_group, default_user, 'repository.write')

    # Don't inherit default object permissions
    user = user_util.create_user()
    UserModel().grant_perm(user, 'hg.inherit_default_perms.false')

    permissions = get_permissions(user)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.none'


def test_cached_perms_data_repository_permissions_from_user_group(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()

    # Needs a second user group to make sure that we select the right
    # permissions.
    user_group2 = user_util.create_user_group()
    UserGroupModel().add_user_to_group(user_group2, user)

    repo = backend_random.create_repo()

    RepoModel().grant_user_group_permission(
        repo, user_group.users_group_name, 'repository.read')
    RepoModel().grant_user_group_permission(
        repo, user_group2.users_group_name, 'repository.write')

    permissions = get_permissions(user)
    assert permissions['repositories'][repo.repo_name] == 'repository.write'


def test_cached_perms_data_repository_permissions_from_user_group_owner(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()

    repo = backend_random.create_repo()
    repo.user_id = user.user_id

    RepoModel().grant_user_group_permission(
        repo, user_group.users_group_name, 'repository.write')

    permissions = get_permissions(user)
    assert permissions['repositories'][repo.repo_name] == 'repository.admin'


def test_cached_perms_data_user_repository_permissions(
        user_util, backend_random):
    user = user_util.create_user()
    repo = backend_random.create_repo()
    granted_permission = 'repository.write'
    RepoModel().grant_user_permission(repo, user, granted_permission)

    permissions = get_permissions(user)
    assert permissions['repositories'][repo.repo_name] == granted_permission


def test_cached_perms_data_user_repository_permissions_explicit(
        user_util, backend_random):
    user = user_util.create_user()
    repo = backend_random.create_repo()
    granted_permission = 'repository.none'
    RepoModel().grant_user_permission(repo, user, granted_permission)

    permissions = get_permissions(user, explicit=True)
    assert permissions['repositories'][repo.repo_name] == granted_permission


def test_cached_perms_data_user_repository_permissions_owner(
        user_util, backend_random):
    user = user_util.create_user()
    repo = backend_random.create_repo()
    repo.user_id = user.user_id
    RepoModel().grant_user_permission(repo, user, 'repository.write')

    permissions = get_permissions(user)
    assert permissions['repositories'][repo.repo_name] == 'repository.admin'


def test_cached_perms_data_repository_groups_permissions_inherited(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()

    # Needs a second group to hit the last condition
    user_group2 = user_util.create_user_group()
    UserGroupModel().add_user_to_group(user_group2, user)

    repo_group = user_util.create_repo_group()

    user_util.grant_user_group_permission_to_repo_group(
        repo_group, user_group, 'group.read')
    user_util.grant_user_group_permission_to_repo_group(
        repo_group, user_group2, 'group.write')

    permissions = get_permissions(user)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.write'


def test_cached_perms_data_repository_groups_permissions_inherited_owner(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()
    repo_group = user_util.create_repo_group()
    repo_group.user_id = user.user_id

    granted_permission = 'group.write'
    user_util.grant_user_group_permission_to_repo_group(
        repo_group, user_group, granted_permission)

    permissions = get_permissions(user)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.admin'


def test_cached_perms_data_repository_groups_permissions(
        user_util, backend_random):
    user = user_util.create_user()

    repo_group = user_util.create_repo_group()

    granted_permission = 'group.write'
    user_util.grant_user_permission_to_repo_group(
        repo_group, user, granted_permission)

    permissions = get_permissions(user)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.write'


def test_cached_perms_data_repository_groups_permissions_explicit(
        user_util, backend_random):
    user = user_util.create_user()

    repo_group = user_util.create_repo_group()

    granted_permission = 'group.none'
    user_util.grant_user_permission_to_repo_group(
        repo_group, user, granted_permission)

    permissions = get_permissions(user, explicit=True)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.none'


def test_cached_perms_data_repository_groups_permissions_owner(
        user_util, backend_random):
    user = user_util.create_user()

    repo_group = user_util.create_repo_group()
    repo_group.user_id = user.user_id

    granted_permission = 'group.write'
    user_util.grant_user_permission_to_repo_group(
        repo_group, user, granted_permission)

    permissions = get_permissions(user)
    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.admin'


def test_cached_perms_data_user_group_permissions_inherited(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()
    user_group2 = user_util.create_user_group()
    UserGroupModel().add_user_to_group(user_group2, user)

    target_user_group = user_util.create_user_group()

    user_util.grant_user_group_permission_to_user_group(
        target_user_group, user_group, 'usergroup.read')
    user_util.grant_user_group_permission_to_user_group(
        target_user_group, user_group2, 'usergroup.write')

    permissions = get_permissions(user)
    assert permissions['user_groups'][target_user_group.users_group_name] == \
        'usergroup.write'


def test_cached_perms_data_user_group_permissions(
        user_util, backend_random):
    user = user_util.create_user()
    user_group = user_util.create_user_group()
    UserGroupModel().grant_user_permission(user_group, user, 'usergroup.write')

    permissions = get_permissions(user)
    assert permissions['user_groups'][user_group.users_group_name] == \
        'usergroup.write'


def test_cached_perms_data_user_group_permissions_explicit(
        user_util, backend_random):
    user = user_util.create_user()
    user_group = user_util.create_user_group()
    UserGroupModel().grant_user_permission(user_group, user, 'usergroup.none')

    permissions = get_permissions(user, explicit=True)
    assert permissions['user_groups'][user_group.users_group_name] == \
        'usergroup.none'


def test_cached_perms_data_user_group_permissions_not_inheriting_defaults(
        user_util, backend_random):
    user = user_util.create_user()
    user_group = user_util.create_user_group()

    # Don't inherit default object permissions
    UserModel().grant_perm(user, 'hg.inherit_default_perms.false')

    permissions = get_permissions(user)
    assert permissions['user_groups'][user_group.users_group_name] == \
        'usergroup.none'


def test_permission_calculator_admin_permissions(
        user_util, backend_random):
    user = user_util.create_user()
    user_group = user_util.create_user_group()
    repo = backend_random.repo
    repo_group = user_util.create_repo_group()

    calculator = auth.PermissionCalculator(
        user.user_id, {}, False, False, True, 'higherwin')
    permissions = calculator._admin_permissions()

    assert permissions['repositories_groups'][repo_group.group_name] == \
        'group.admin'
    assert permissions['user_groups'][user_group.users_group_name] == \
        'usergroup.admin'
    assert permissions['repositories'][repo.repo_name] == 'repository.admin'
    assert 'hg.admin' in permissions['global']


def test_permission_calculator_repository_permissions_robustness_from_group(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()

    RepoModel().grant_user_group_permission(
        backend_random.repo, user_group.users_group_name, 'repository.write')

    calculator = auth.PermissionCalculator(
        user.user_id, {}, False, False, False, 'higherwin')
    calculator._calculate_repository_permissions()


def test_permission_calculator_repository_permissions_robustness_from_user(
        user_util, backend_random):
    user = user_util.create_user()

    RepoModel().grant_user_permission(
        backend_random.repo, user, 'repository.write')

    calculator = auth.PermissionCalculator(
        user.user_id, {}, False, False, False, 'higherwin')
    calculator._calculate_repository_permissions()


def test_permission_calculator_repo_group_permissions_robustness_from_group(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()
    repo_group = user_util.create_repo_group()

    user_util.grant_user_group_permission_to_repo_group(
        repo_group, user_group, 'group.write')

    calculator = auth.PermissionCalculator(
        user.user_id, {}, False, False, False, 'higherwin')
    calculator._calculate_repository_group_permissions()


def test_permission_calculator_repo_group_permissions_robustness_from_user(
        user_util, backend_random):
    user = user_util.create_user()
    repo_group = user_util.create_repo_group()

    user_util.grant_user_permission_to_repo_group(
        repo_group, user, 'group.write')

    calculator = auth.PermissionCalculator(
        user.user_id, {}, False, False, False, 'higherwin')
    calculator._calculate_repository_group_permissions()


def test_permission_calculator_user_group_permissions_robustness_from_group(
        user_util, backend_random):
    user, user_group = user_util.create_user_with_group()
    target_user_group = user_util.create_user_group()

    user_util.grant_user_group_permission_to_user_group(
        target_user_group, user_group, 'usergroup.write')

    calculator = auth.PermissionCalculator(
        user.user_id, {}, False, False, False, 'higherwin')
    calculator._calculate_user_group_permissions()


def test_permission_calculator_user_group_permissions_robustness_from_user(
        user_util, backend_random):
    user = user_util.create_user()
    target_user_group = user_util.create_user_group()

    user_util.grant_user_permission_to_user_group(
        target_user_group, user, 'usergroup.write')

    calculator = auth.PermissionCalculator(
        user.user_id, {}, False, False, False, 'higherwin')
    calculator._calculate_user_group_permissions()


@pytest.mark.parametrize("algo, new_permission, old_permission, expected", [
    ('higherwin', 'repository.none', 'repository.none', 'repository.none'),
    ('higherwin', 'repository.read', 'repository.none', 'repository.read'),
    ('lowerwin', 'repository.write', 'repository.write', 'repository.write'),
    ('lowerwin', 'repository.read', 'repository.write', 'repository.read'),
])
def test_permission_calculator_choose_permission(
        user_regular, algo, new_permission, old_permission, expected):
    calculator = auth.PermissionCalculator(
        user_regular.user_id, {}, False, False, False, algo)
    result = calculator._choose_permission(new_permission, old_permission)
    assert result == expected


def test_permission_calculator_choose_permission_raises_on_wrong_algo(
        user_regular):
    calculator = auth.PermissionCalculator(
        user_regular.user_id, {}, False, False, False, 'invalid')
    result = calculator._choose_permission(
        'repository.read', 'repository.read')
    # TODO: johbo: This documents the existing behavior. Think of an
    # improvement.
    assert result is None


def test_auth_user_get_cookie_store_for_normal_user(user_util):
    user = user_util.create_user()
    auth_user = auth.AuthUser(user_id=user.user_id)
    expected_data = {
        'username': user.username,
        'user_id': user.user_id,
        'password': md5(user.password),
        'is_authenticated': False
    }
    assert auth_user.get_cookie_store() == expected_data


def test_auth_user_get_cookie_store_for_default_user():
    default_user = User.get_default_user()
    auth_user = auth.AuthUser()
    expected_data = {
        'username': User.DEFAULT_USER,
        'user_id': default_user.user_id,
        'password': md5(default_user.password),
        'is_authenticated': True
    }
    assert auth_user.get_cookie_store() == expected_data


def get_permissions(user, **kwargs):
    """
    Utility filling in useful defaults into the call to `_cached_perms_data`.

    Fill in `**kwargs` if specific values are needed for a test.
    """
    call_args = {
        'user_id': user.user_id,
        'scope': {},
        'user_is_admin': False,
        'user_inherit_default_permissions': False,
        'explicit': False,
        'algo': 'higherwin',
    }
    call_args.update(kwargs)
    permissions = auth._cached_perms_data(**call_args)
    return permissions


class TestGenerateAuthToken(object):
    def test_salt_is_used_when_specified(self):
        salt = 'abcde'
        user_name = 'test_user'
        result = auth.generate_auth_token(user_name, salt)
        expected_result = sha1(user_name + salt).hexdigest()
        assert result == expected_result

    def test_salt_is_geneated_when_not_specified(self):
        user_name = 'test_user'
        random_salt = os.urandom(16)
        with patch.object(auth, 'os') as os_mock:
            os_mock.urandom.return_value = random_salt
            result = auth.generate_auth_token(user_name)
        expected_result = sha1(user_name + random_salt).hexdigest()
        assert result == expected_result
