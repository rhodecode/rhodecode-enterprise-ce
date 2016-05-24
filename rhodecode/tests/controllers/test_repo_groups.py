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
import pylons
import pytest
from pylons import tmpl_context as c


@pytest.fixture
def current_user(request, user_util):
    user = user_util.create_user()

    request_mock = mock.Mock(user=user)
    pylons.request._push_object(request_mock)

    @request.addfinalizer
    def cleanup():
        pylons.request._pop_object()
    return user


@pytest.fixture
def personal_group_with_parent(user_util, current_user):
    group_read_only = user_util.create_repo_group()
    user_util.grant_user_permission_to_repo_group(
        group_read_only, current_user, 'group.read')

    # TODO: johbo: This should go into the business models
    group_as_admin = user_util.create_repo_group(
        owner=current_user)
    group_as_admin.parent_group = group_read_only
    group_as_admin.group_name = group_as_admin.get_new_name(
        group_as_admin.group_name)

    return group_as_admin


@pytest.fixture
def controller():
    from rhodecode.controllers.admin import repo_groups
    return repo_groups.RepoGroupsController()


def test_repo_groups_load_defaults(
        current_user, personal_group_with_parent, controller):
    personal_group = personal_group_with_parent
    controller._RepoGroupsController__load_defaults(True, personal_group)

    expected_list = ['-1', personal_group.parent_group.group_id]
    returned_group_ids = [group[0] for group in c.repo_groups]
    assert returned_group_ids == expected_list


def test_repo_groups_load_defaults_with_missing_group(
        current_user, personal_group_with_parent, controller):
    personal_group = personal_group_with_parent
    controller._RepoGroupsController__load_defaults(True)

    expected_list = sorted(['-1', personal_group.group_id])
    returned_group_ids = sorted([group[0] for group in c.repo_groups])
    assert returned_group_ids == expected_list
