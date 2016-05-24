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

import mock
import pytest

from rhodecode.model.db import User
from rhodecode.tests import TEST_USER_REGULAR_LOGIN
from rhodecode.tests.fixture import Fixture
from rhodecode.model.user_group import UserGroupModel
from rhodecode.model.meta import Session


fixture = Fixture()


def teardown_module(self):
    _delete_all_user_groups()


@pytest.mark.parametrize(
    "pre_existing, regular_should_be, external_should_be, groups, "
    "expected", [
        ([], [], [], [], []),
        # no changes of regular
        ([], ['regular'], [], [], ['regular']),
        # not added to regular group
        (['some_other'], [], [], ['some_other'], []),
        (
            [], ['regular'], ['container'], ['container'],
            ['regular', 'container']
        ),
        (
            [], ['regular'], [], ['container', 'container2'],
            ['regular', 'container', 'container2']
        ),
        # remove not used
        ([], ['regular'], ['other'], [], ['regular']),
        (
            ['some_other'], ['regular'], ['other', 'container'],
            ['container', 'container2'],
            ['regular', 'container', 'container2']
        ),
    ])
def test_enforce_groups(pre_existing, regular_should_be,
                        external_should_be, groups, expected, backend_hg):
    # TODO: anderson: adding backend_hg fixture so it sets up the database
    # for when running this file alone
    _delete_all_user_groups()

    user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
    for gr in pre_existing:
        gr = fixture.create_user_group(gr)
    Session().commit()

    # make sure use is just in those groups
    for gr in regular_should_be:
        gr = fixture.create_user_group(gr)
        Session().commit()
        UserGroupModel().add_user_to_group(gr, user)
        Session().commit()

    # now special external groups created by auth plugins
    for gr in external_should_be:
        gr = fixture.create_user_group(
            gr, user_group_data={'extern_type': 'container'})
        Session().commit()
        UserGroupModel().add_user_to_group(gr, user)
        Session().commit()

    UserGroupModel().enforce_groups(user, groups, 'container')
    Session().commit()

    user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
    in_groups = user.group_member

    expected.sort()
    assert (
        expected == sorted(x.users_group.users_group_name for x in in_groups))


def _delete_all_user_groups():
    for gr in UserGroupModel.get_all():
        fixture.destroy_user_group(gr)
    Session().commit()


def test_add_and_remove_user_from_group(user_regular, user_util):
    user_group = user_util.create_user_group()
    assert user_group.members == []
    UserGroupModel().add_user_to_group(user_group, user_regular)
    Session().commit()
    assert user_group.members[0].user == user_regular
    UserGroupModel().remove_user_from_group(user_group, user_regular)
    Session().commit()
    assert user_group.members == []


@pytest.mark.parametrize(
    'data, expected', [
        ("1", [1]), (["1", "2"], [1, 2])
    ]
)
def test_clean_members_data(data, expected):
    cleaned = UserGroupModel()._clean_members_data(data)
    assert cleaned == expected


def test_update_members_from_user_ids(user_regular, user_util):
    user_group = user_util.create_user_group()
    assert user_group.members == []
    assert user_group.user != user_regular
    expected_active_state = not user_group.users_group_active

    form_data = {
        'users_group_members': str(user_regular.user_id),
        'user': str(user_regular.username),
        'users_group_name': 'changed_name',
        'users_group_active': expected_active_state,
        'user_group_description': 'changed_description'
    }

    UserGroupModel().update(user_group, form_data)
    assert user_group.members[0].user_id == user_regular.user_id
    assert user_group.user_id == user_regular.user_id
    assert 'changed_name' in user_group.users_group_name
    assert 'changed_description' in user_group.user_group_description
    assert user_group.users_group_active == expected_active_state
    # Ignore changes on the test
    Session().rollback()


def _create_test_members():
    members = []
    for member_number in range(3):
        member = mock.Mock()
        member.user_id = member_number + 1
        member.user.user_id = member_number + 1
        members.append(member)
    return members


def test_get_added_and_removed_users():
    members = _create_test_members()
    mock_user_group = mock.Mock()
    mock_user_group.members = [members[0], members[1]]
    new_users_list = [members[1].user.user_id, members[2].user.user_id]
    model = UserGroupModel()

    added, removed = model._get_added_and_removed_user_ids(
        mock_user_group, new_users_list)

    assert added == [members[2].user.user_id]
    assert removed == [members[0].user.user_id]


def test_set_users_as_members_and_find_user_in_group(
        user_util, user_regular, user_admin):
    user_group = user_util.create_user_group()
    assert len(user_group.members) == 0
    user_list = [user_regular.user_id, user_admin.user_id]
    UserGroupModel()._set_users_as_members(user_group, user_list)
    assert len(user_group.members) == 2
    assert UserGroupModel()._find_user_in_group(user_regular, user_group)
