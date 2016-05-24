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
from sqlalchemy.sql.expression import true

from rhodecode.model.db import User, UserGroup, UserGroupMember, UserEmailMap,\
    Permission, UserIpMap
from rhodecode.model.meta import Session
from rhodecode.model.user import UserModel
from rhodecode.model.user_group import UserGroupModel
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.tests.fixture import Fixture

fixture = Fixture()


@pytest.fixture
def test_user(request, pylonsapp):
    usr = UserModel().create_or_update(
        username=u'test_user',
        password=u'qweqwe',
        email=u'main_email@rhodecode.org',
        firstname=u'u1', lastname=u'u1')
    Session().commit()
    assert User.get_by_username(u'test_user') == usr

    @request.addfinalizer
    def cleanup():
        if UserModel().get_user(usr.user_id) is None:
            return

        perm = Permission.query().all()
        for p in perm:
            UserModel().revoke_perm(usr, p)

        UserModel().delete(usr.user_id)
        Session().commit()

    return usr


def test_create_and_remove(test_user):
    usr = test_user

    # make user group
    user_group = fixture.create_user_group('some_example_group')
    Session().commit()

    UserGroupModel().add_user_to_group(user_group, usr)
    Session().commit()

    assert UserGroup.get(user_group.users_group_id) == user_group
    assert UserGroupMember.query().count() == 1
    UserModel().delete(usr.user_id)
    Session().commit()

    assert UserGroupMember.query().all() == []


def test_additonal_email_as_main(test_user):
    with pytest.raises(AttributeError):
        m = UserEmailMap()
        m.email = test_user.email
        m.user = test_user
        Session().add(m)
        Session().commit()


def test_extra_email_map(test_user):

    m = UserEmailMap()
    m.email = u'main_email2@rhodecode.org'
    m.user = test_user
    Session().add(m)
    Session().commit()

    u = User.get_by_email(email='main_email@rhodecode.org')
    assert test_user.user_id == u.user_id
    assert test_user.username == u.username

    u = User.get_by_email(email='main_email2@rhodecode.org')
    assert test_user.user_id == u.user_id
    assert test_user.username == u.username
    u = User.get_by_email(email='main_email3@rhodecode.org')
    assert u is None


def test_get_api_data_replaces_secret_data_by_default(test_user):
    api_data = test_user.get_api_data()
    api_key_length = 40
    expected_replacement = '*' * api_key_length

    assert api_data['api_key'] == expected_replacement
    for key in api_data['api_keys']:
        assert key == expected_replacement


def test_get_api_data_includes_secret_data_if_activated(test_user):
    api_data = test_user.get_api_data(include_secrets=True)

    assert api_data['api_key'] == test_user.api_key
    assert api_data['api_keys'] == test_user.auth_tokens


def test_add_perm(test_user):
    perm = Permission.query().all()[0]
    UserModel().grant_perm(test_user, perm)
    Session().commit()
    assert UserModel().has_perm(test_user, perm)


def test_has_perm(test_user):
    perm = Permission.query().all()
    for p in perm:
        assert not UserModel().has_perm(test_user, p)


def test_revoke_perm(test_user):
    perm = Permission.query().all()[0]
    UserModel().grant_perm(test_user, perm)
    Session().commit()
    assert UserModel().has_perm(test_user, perm)

    # revoke
    UserModel().revoke_perm(test_user, perm)
    Session().commit()
    assert not UserModel().has_perm(test_user, perm)


@pytest.mark.parametrize("ip_range, expected, expect_errors", [
    ('', [], False),
    ('127.0.0.1', ['127.0.0.1'], False),
    ('127.0.0.1,127.0.0.2', ['127.0.0.1', '127.0.0.2'], False),
    ('127.0.0.1 ,  127.0.0.2', ['127.0.0.1', '127.0.0.2'], False),
    (
        '127.0.0.1,172.172.172.0,127.0.0.2',
        ['127.0.0.1', '172.172.172.0', '127.0.0.2'], False),
    (
        '127.0.0.1-127.0.0.5',
        ['127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.4', '127.0.0.5'],
        False),
    (
        '127.0.0.1 - 127.0.0.5',
        ['127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.4', '127.0.0.5'],
        False
    ),
    ('-', [], True),
    ('127.0.0.1-32', [], True),
    (
        '127.0.0.1,127.0.0.1,127.0.0.1,127.0.0.1-127.0.0.2,127.0.0.2',
        ['127.0.0.1', '127.0.0.2'], False),
    (
        '127.0.0.1-127.0.0.2,127.0.0.4-127.0.0.6,',
        ['127.0.0.1', '127.0.0.2', '127.0.0.4', '127.0.0.5', '127.0.0.6'],
        False
    ),
    (
        '127.0.0.1-127.0.0.2,127.0.0.1-127.0.0.6,',
        ['127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.4', '127.0.0.5',
         '127.0.0.6'],
        False
    ),
])
def test_ip_range_generator(ip_range, expected, expect_errors):
    func = UserModel().parse_ip_range
    if expect_errors:
        pytest.raises(Exception, func, ip_range)
    else:
        parsed_list = func(ip_range)
        assert parsed_list == expected


def test_user_delete_cascades_ip_whitelist(test_user):
    sample_ip = '1.1.1.1'
    uid_map = UserIpMap(user_id=test_user.user_id, ip_addr=sample_ip)
    Session().add(uid_map)
    Session().delete(test_user)
    try:
        Session().flush()
    finally:
        Session().rollback()


def test_account_for_deactivation_generation(test_user):
    accounts = UserModel().get_accounts_in_creation_order(
        current_user=test_user)
    # current user should be #1 in the list
    assert accounts[0] == test_user.user_id
    active_users = User.query().filter(User.active == true()).count()
    assert active_users == len(accounts)


def test_user_delete_cascades_permissions_on_repo(backend, test_user):
    test_repo = backend.create_repo()
    RepoModel().grant_user_permission(
        test_repo, test_user, 'repository.write')
    Session().commit()

    assert test_user.repo_to_perm

    UserModel().delete(test_user)
    Session().commit()


def test_user_delete_cascades_permissions_on_repo_group(
        test_repo_group, test_user):
    RepoGroupModel().grant_user_permission(
        test_repo_group, test_user, 'group.write')
    Session().commit()

    assert test_user.repo_group_to_perm

    Session().delete(test_user)
    Session().commit()


def test_user_delete_cascades_permissions_on_user_group(
        test_user_group, test_user):
    UserGroupModel().grant_user_permission(
        test_user_group, test_user, 'usergroup.write')
    Session().commit()

    assert test_user.user_group_to_perm

    Session().delete(test_user)
    Session().commit()
