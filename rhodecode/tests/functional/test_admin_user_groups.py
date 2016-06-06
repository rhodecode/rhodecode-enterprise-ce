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

from rhodecode.tests import (
    TestController, url, assert_session_flash, link_to)
from rhodecode.model.db import User, UserGroup
from rhodecode.model.meta import Session
from rhodecode.tests.fixture import Fixture

TEST_USER_GROUP = 'admins_test'

fixture = Fixture()


class TestAdminUsersGroupsController(TestController):

    def test_index(self):
        self.log_user()
        response = self.app.get(url('users_groups'))
        response.status_int == 200

    def test_create(self):
        self.log_user()
        users_group_name = TEST_USER_GROUP
        response = self.app.post(url('users_groups'), {
            'users_group_name': users_group_name,
            'user_group_description': 'DESC',
            'active': True,
            'csrf_token': self.csrf_token})

        user_group_link = link_to(
            users_group_name,
            url('edit_users_group',
                user_group_id=UserGroup.get_by_group_name(
                    users_group_name).users_group_id))
        assert_session_flash(
            response,
            'Created user group %s' % user_group_link)

    def test_delete(self):
        self.log_user()
        users_group_name = TEST_USER_GROUP + 'another'
        response = self.app.post(url('users_groups'), {
            'users_group_name': users_group_name,
            'user_group_description': 'DESC',
            'active': True,
            'csrf_token': self.csrf_token})

        user_group_link = link_to(
            users_group_name,
            url('edit_users_group',
                user_group_id=UserGroup.get_by_group_name(
                    users_group_name).users_group_id))
        assert_session_flash(
            response,
            'Created user group %s' % user_group_link)

        group = Session().query(UserGroup).filter(
            UserGroup.users_group_name == users_group_name).one()

        response = self.app.post(
            url('delete_users_group', user_group_id=group.users_group_id),
            params={'_method': 'delete', 'csrf_token': self.csrf_token})

        group = Session().query(UserGroup).filter(
            UserGroup.users_group_name == users_group_name).scalar()

        assert group is None

    @pytest.mark.parametrize('repo_create, repo_create_write, user_group_create, repo_group_create, fork_create, inherit_default_permissions, expect_error, expect_form_error', [
        ('hg.create.none', 'hg.create.write_on_repogroup.false', 'hg.usergroup.create.false', 'hg.repogroup.create.false', 'hg.fork.none', 'hg.inherit_default_perms.false', False, False),
        ('hg.create.repository', 'hg.create.write_on_repogroup.true', 'hg.usergroup.create.true', 'hg.repogroup.create.true', 'hg.fork.repository', 'hg.inherit_default_perms.false', False, False),
        ('hg.create.XXX', 'hg.create.write_on_repogroup.true', 'hg.usergroup.create.true', 'hg.repogroup.create.true', 'hg.fork.repository', 'hg.inherit_default_perms.false', False, True),
        ('', '', '', '', '', '', True, False),
    ])
    def test_global_perms_on_group(
            self, repo_create, repo_create_write, user_group_create,
            repo_group_create, fork_create, expect_error, expect_form_error,
            inherit_default_permissions):
        self.log_user()
        users_group_name = TEST_USER_GROUP + 'another2'
        response = self.app.post(url('users_groups'),
                                 {'users_group_name': users_group_name,
                                  'user_group_description': 'DESC',
                                  'active': True,
                                  'csrf_token': self.csrf_token})

        ug = UserGroup.get_by_group_name(users_group_name)
        user_group_link = link_to(
            users_group_name,
            url('edit_users_group', user_group_id=ug.users_group_id))
        assert_session_flash(
            response,
            'Created user group %s' % user_group_link)
        response.follow()

        # ENABLE REPO CREATE ON A GROUP
        perm_params = {
            'inherit_default_permissions': False,
            'default_repo_create': repo_create,
            'default_repo_create_on_write': repo_create_write,
            'default_user_group_create': user_group_create,
            'default_repo_group_create': repo_group_create,
            'default_fork_create': fork_create,
            'default_inherit_default_permissions': inherit_default_permissions,

            '_method': 'put',
            'csrf_token': self.csrf_token,
        }
        response = self.app.post(
            url('edit_user_group_global_perms',
                user_group_id=ug.users_group_id),
            params=perm_params)

        if expect_form_error:
            assert response.status_int == 200
            response.mustcontain('Value must be one of')
        else:
            if expect_error:
                msg = 'An error occurred during permissions saving'
            else:
                msg = 'User Group global permissions updated successfully'
                ug = UserGroup.get_by_group_name(users_group_name)
                del perm_params['_method']
                del perm_params['csrf_token']
                del perm_params['inherit_default_permissions']
                assert perm_params == ug.get_default_perms()
            assert_session_flash(response, msg)

        fixture.destroy_user_group(users_group_name)

    def test_edit(self):
        self.log_user()
        response = self.app.get(url('edit_users_group', user_group_id=1))

    def test_edit_user_group_members(self):
        self.log_user()
        response = self.app.get(url('edit_user_group_members', user_group_id=1))
        response.mustcontain('No members yet')

    def test_usergroup_escape(self):
        user = User.get_by_username('test_admin')
        user.name = '<img src="/image1" onload="alert(\'Hello, World!\');">'
        user.lastname = (
            '<img src="/image2" onload="alert(\'Hello, World!\');">')
        Session().add(user)
        Session().commit()

        self.log_user()
        users_group_name = 'samplegroup'
        data = {
            'users_group_name': users_group_name,
            'user_group_description': (
                '<strong onload="alert();">DESC</strong>'),
            'active': True,
            'csrf_token': self.csrf_token
        }

        response = self.app.post(url('users_groups'), data)
        response = self.app.get(url('users_groups'))

        response.mustcontain(
            '&lt;strong onload=&#34;alert();&#34;&gt;'
            'DESC&lt;/strong&gt;')
        response.mustcontain(
            '&lt;img src=&#34;/image2&#34; onload=&#34;'
            'alert(&#39;Hello, World!&#39;);&#34;&gt;')
