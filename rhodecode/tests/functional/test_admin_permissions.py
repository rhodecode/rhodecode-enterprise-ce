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
from rhodecode.model.db import User, UserIpMap
from rhodecode.model.permission import PermissionModel
from rhodecode.tests import (
    TestController, url, clear_all_caches, assert_session_flash)


class TestAdminPermissionsController(TestController):

    @pytest.fixture(scope='class', autouse=True)
    def prepare(self, request):
        # cleanup and reset to default permissions after
        @request.addfinalizer
        def cleanup():
            PermissionModel().create_default_user_permissions(
                User.get_default_user(), force=True)

    def test_index_application(self):
        self.log_user()
        self.app.get(url('admin_permissions_application'))

    @pytest.mark.parametrize(
        'anonymous, default_register, default_register_message,'
        'default_extern_activate, expect_error, expect_form_error', [
            (True, 'hg.register.none', '', 'hg.extern_activate.manual',
             False, False),
            (True, 'hg.register.manual_activate', '', 'hg.extern_activate.auto',
             False, False),
            (True, 'hg.register.auto_activate', '', 'hg.extern_activate.manual',
             False, False),
            (True, 'hg.register.auto_activate', '', 'hg.extern_activate.manual',
             False, False),
            (True, 'hg.register.XXX', '', 'hg.extern_activate.manual',
             False, True),
            (True, '', '', '', True, False),
        ])
    def test_update_application_permissions(
            self, anonymous, default_register, default_register_message,
            default_extern_activate, expect_error, expect_form_error):

        self.log_user()

        # TODO: anonymous access set here to False, breaks some other tests
        params = {
            'csrf_token': self.csrf_token,
            'anonymous': anonymous,
            'default_register': default_register,
            'default_register_message': default_register_message,
            'default_extern_activate': default_extern_activate,
        }
        response = self.app.post(url('admin_permissions_application'),
                                 params=params)
        if expect_form_error:
            assert response.status_int == 200
            response.mustcontain('Value must be one of')
        else:
            if expect_error:
                msg = 'Error occurred during update of permissions'
            else:
                msg = 'Application permissions updated successfully'
            assert_session_flash(response, msg)

    def test_index_object(self):
        self.log_user()
        self.app.get(url('admin_permissions_object'))

    @pytest.mark.parametrize(
        'repo, repo_group, user_group, expect_error, expect_form_error', [
            ('repository.none', 'group.none', 'usergroup.none', False, False),
            ('repository.read', 'group.read', 'usergroup.read', False, False),
            ('repository.write', 'group.write', 'usergroup.write',
             False, False),
            ('repository.admin', 'group.admin', 'usergroup.admin',
             False, False),
            ('repository.XXX', 'group.admin', 'usergroup.admin', False, True),
            ('', '', '', True, False),
        ])
    def test_update_object_permissions(self, repo, repo_group, user_group,
                                       expect_error, expect_form_error):
        self.log_user()

        params = {
            'csrf_token': self.csrf_token,
            'default_repo_perm': repo,
            'overwrite_default_repo': False,
            'default_group_perm': repo_group,
            'overwrite_default_group': False,
            'default_user_group_perm': user_group,
            'overwrite_default_user_group': False,
        }
        response = self.app.post(url('admin_permissions_object'),
                                 params=params)
        if expect_form_error:
            assert response.status_int == 200
            response.mustcontain('Value must be one of')
        else:
            if expect_error:
                msg = 'Error occurred during update of permissions'
            else:
                msg = 'Object permissions updated successfully'
            assert_session_flash(response, msg)

    def test_index_global(self):
        self.log_user()
        self.app.get(url('admin_permissions_global'))

    @pytest.mark.parametrize(
        'repo_create, repo_create_write, user_group_create, repo_group_create,'
        'fork_create, inherit_default_permissions, expect_error,'
        'expect_form_error', [
            ('hg.create.none', 'hg.create.write_on_repogroup.false',
             'hg.usergroup.create.false', 'hg.repogroup.create.false',
             'hg.fork.none', 'hg.inherit_default_perms.false', False, False),
            ('hg.create.repository', 'hg.create.write_on_repogroup.true',
             'hg.usergroup.create.true', 'hg.repogroup.create.true',
             'hg.fork.repository', 'hg.inherit_default_perms.false',
             False, False),
            ('hg.create.XXX', 'hg.create.write_on_repogroup.true',
             'hg.usergroup.create.true', 'hg.repogroup.create.true',
             'hg.fork.repository', 'hg.inherit_default_perms.false',
             False, True),
            ('', '', '', '', '', '', True, False),
        ])
    def test_update_global_permissions(
            self, repo_create, repo_create_write, user_group_create,
            repo_group_create, fork_create, inherit_default_permissions,
            expect_error, expect_form_error):
        self.log_user()

        params = {
            'csrf_token': self.csrf_token,
            'default_repo_create': repo_create,
            'default_repo_create_on_write': repo_create_write,
            'default_user_group_create': user_group_create,
            'default_repo_group_create': repo_group_create,
            'default_fork_create': fork_create,
            'default_inherit_default_permissions': inherit_default_permissions
        }
        response = self.app.post(url('admin_permissions_global'),
                                 params=params)
        if expect_form_error:
            assert response.status_int == 200
            response.mustcontain('Value must be one of')
        else:
            if expect_error:
                msg = 'Error occurred during update of permissions'
            else:
                msg = 'Global permissions updated successfully'
            assert_session_flash(response, msg)

    def test_index_ips(self):
        self.log_user()
        response = self.app.get(url('admin_permissions_ips'))
        # TODO: Test response...
        response.mustcontain('All IP addresses are allowed')

    def test_add_delete_ips(self):
        self.log_user()
        clear_all_caches()

        # ADD
        default_user_id = User.get_default_user().user_id
        response = self.app.post(
            url('edit_user_ips', user_id=default_user_id),
            params={'new_ip': '127.0.0.0/24', '_method': 'put',
                    'csrf_token': self.csrf_token})

        response = self.app.get(url('admin_permissions_ips'))
        response.mustcontain('127.0.0.0/24')
        response.mustcontain('127.0.0.0 - 127.0.0.255')

        # DELETE
        default_user_id = User.get_default_user().user_id
        del_ip_id = UserIpMap.query().filter(UserIpMap.user_id ==
                                             default_user_id).first().ip_id

        response = self.app.post(
            url('edit_user_ips', user_id=default_user_id),
            params={'_method': 'delete', 'del_ip_id': del_ip_id,
                    'csrf_token': self.csrf_token})
        clear_all_caches()
        response = self.app.get(url('admin_permissions_ips'))
        response.mustcontain('All IP addresses are allowed')
        response.mustcontain(no=['127.0.0.0/24'])
        response.mustcontain(no=['127.0.0.0 - 127.0.0.255'])

    def test_index_overview(self):
        self.log_user()
        self.app.get(url('admin_permissions_overview'))
