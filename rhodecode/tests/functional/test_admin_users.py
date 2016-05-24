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
from sqlalchemy.orm.exc import NoResultFound

from rhodecode.lib.auth import check_password
from rhodecode.lib import helpers as h
from rhodecode.model import validators
from rhodecode.model.db import User, UserIpMap, UserApiKeys
from rhodecode.model.meta import Session
from rhodecode.model.user import UserModel
from rhodecode.tests import (
    TestController, url, link_to, TEST_USER_ADMIN_LOGIN,
    TEST_USER_REGULAR_LOGIN, assert_session_flash)
from rhodecode.tests.fixture import Fixture
from rhodecode.tests.utils import AssertResponse

fixture = Fixture()


class TestAdminUsersController(TestController):
    test_user_1 = 'testme'
    destroy_users = set()

    @classmethod
    def teardown_method(cls, method):
        fixture.destroy_users(cls.destroy_users)

    def test_index(self):
        self.log_user()
        self.app.get(url('users'))

    def test_create(self):
        self.log_user()
        username = 'newtestuser'
        password = 'test12'
        password_confirmation = password
        name = 'name'
        lastname = 'lastname'
        email = 'mail@mail.com'

        response = self.app.get(url('new_user'))

        response = self.app.post(url('users'), params={
            'username': username,
            'password': password,
            'password_confirmation': password_confirmation,
            'firstname': name,
            'active': True,
            'lastname': lastname,
            'extern_name': 'rhodecode',
            'extern_type': 'rhodecode',
            'email': email,
            'csrf_token': self.csrf_token,
        })
        user_link = link_to(
            username,
            url('edit_user', user_id=User.get_by_username(username).user_id))
        assert_session_flash(response, 'Created user %s' % (user_link,))
        self.destroy_users.add(username)

        new_user = User.query().filter(User.username == username).one()

        assert new_user.username == username
        assert check_password(password, new_user.password)
        assert new_user.name == name
        assert new_user.lastname == lastname
        assert new_user.email == email

        response.follow()
        response = response.follow()
        response.mustcontain(username)

    def test_create_err(self):
        self.log_user()
        username = 'new_user'
        password = ''
        name = 'name'
        lastname = 'lastname'
        email = 'errmail.com'

        response = self.app.get(url('new_user'))

        response = self.app.post(url('users'), params={
            'username': username,
            'password': password,
            'name': name,
            'active': False,
            'lastname': lastname,
            'email': email,
            'csrf_token': self.csrf_token,
        })

        msg = validators.ValidUsername(
            False, {})._messages['system_invalid_username']
        msg = h.html_escape(msg % {'username': 'new_user'})
        response.mustcontain('<span class="error-message">%s</span>' % msg)
        response.mustcontain(
            '<span class="error-message">Please enter a value</span>')
        response.mustcontain(
            '<span class="error-message">An email address must contain a'
            ' single @</span>')

        def get_user():
            Session().query(User).filter(User.username == username).one()

        with pytest.raises(NoResultFound):
            get_user()

    def test_new(self):
        self.log_user()
        self.app.get(url('new_user'))

    @pytest.mark.parametrize("name, attrs", [
        ('firstname', {'firstname': 'new_username'}),
        ('lastname', {'lastname': 'new_username'}),
        ('admin', {'admin': True}),
        ('admin', {'admin': False}),
        ('extern_type', {'extern_type': 'ldap'}),
        ('extern_type', {'extern_type': None}),
        ('extern_name', {'extern_name': 'test'}),
        ('extern_name', {'extern_name': None}),
        ('active', {'active': False}),
        ('active', {'active': True}),
        ('email', {'email': 'some@email.com'}),
        ('language', {'language': 'de'}),
        ('language', {'language': 'en'}),
        # ('new_password', {'new_password': 'foobar123',
        #                   'password_confirmation': 'foobar123'})
        ])
    def test_update(self, name, attrs):
        self.log_user()
        usr = fixture.create_user(self.test_user_1, password='qweqwe',
                                  email='testme@rhodecode.org',
                                  extern_type='rhodecode',
                                  extern_name=self.test_user_1,
                                  skip_if_exists=True)
        Session().commit()
        self.destroy_users.add(self.test_user_1)
        params = usr.get_api_data()
        cur_lang = params['language'] or 'en'
        params.update({
            'password_confirmation': '',
            'new_password': '',
            'language': cur_lang,
            '_method': 'put',
            'csrf_token': self.csrf_token,
        })
        params.update({'new_password': ''})
        params.update(attrs)
        if name == 'email':
            params['emails'] = [attrs['email']]
        elif name == 'extern_type':
            # cannot update this via form, expected value is original one
            params['extern_type'] = "rhodecode"
        elif name == 'extern_name':
            # cannot update this via form, expected value is original one
            params['extern_name'] = self.test_user_1
            # special case since this user is not
            # logged in yet his data is not filled
            # so we use creation data

        response = self.app.post(url('user', user_id=usr.user_id), params)
        assert response.status_int == 302
        assert_session_flash(response, 'User updated successfully')

        updated_user = User.get_by_username(self.test_user_1)
        updated_params = updated_user.get_api_data()
        updated_params.update({'password_confirmation': ''})
        updated_params.update({'new_password': ''})

        del params['_method']
        del params['csrf_token']
        assert params == updated_params

    def test_update_and_migrate_password(
            self, autologin_user, real_crypto_backend):
        from rhodecode.lib import auth

        # create new user, with sha256 password
        temp_user = 'test_admin_sha256'
        user = fixture.create_user(temp_user)
        user.password = auth._RhodeCodeCryptoSha256().hash_create(
            b'test123')
        Session().add(user)
        Session().commit()
        self.destroy_users.add('test_admin_sha256')

        params = user.get_api_data()

        params.update({
            'password_confirmation': 'qweqwe123',
            'new_password': 'qweqwe123',
            'language': 'en',
            '_method': 'put',
            'csrf_token': autologin_user.csrf_token,
        })

        response = self.app.post(url('user', user_id=user.user_id), params)
        assert response.status_int == 302
        assert_session_flash(response, 'User updated successfully')

        # new password should be bcrypted, after log-in and transfer
        user = User.get_by_username(temp_user)
        assert user.password.startswith('$')

        updated_user = User.get_by_username(temp_user)
        updated_params = updated_user.get_api_data()
        updated_params.update({'password_confirmation': 'qweqwe123'})
        updated_params.update({'new_password': 'qweqwe123'})

        del params['_method']
        del params['csrf_token']
        assert params == updated_params

    def test_delete(self):
        self.log_user()
        username = 'newtestuserdeleteme'

        fixture.create_user(name=username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'csrf_token': self.csrf_token})

        assert_session_flash(response, 'Successfully deleted user')

    def test_delete_owner_of_repository(self):
        self.log_user()
        username = 'newtestuserdeleteme_repo_owner'
        obj_name = 'test_repo'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_repo(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'csrf_token': self.csrf_token})

        msg = 'user "%s" still owns 1 repositories and cannot be removed. ' \
              'Switch owners or remove those repositories:%s' % (username,
                                                                 obj_name)
        assert_session_flash(response, msg)
        fixture.destroy_repo(obj_name)

    def test_delete_owner_of_repository_detaching(self):
        self.log_user()
        username = 'newtestuserdeleteme_repo_owner_detach'
        obj_name = 'test_repo'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_repo(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'user_repos': 'detach',
                                         'csrf_token': self.csrf_token})

        msg = 'Detached 1 repositories'
        assert_session_flash(response, msg)
        fixture.destroy_repo(obj_name)

    def test_delete_owner_of_repository_deleting(self):
        self.log_user()
        username = 'newtestuserdeleteme_repo_owner_delete'
        obj_name = 'test_repo'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_repo(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'user_repos': 'delete',
                                         'csrf_token': self.csrf_token})

        msg = 'Deleted 1 repositories'
        assert_session_flash(response, msg)

    def test_delete_owner_of_repository_group(self):
        self.log_user()
        username = 'newtestuserdeleteme_repo_group_owner'
        obj_name = 'test_group'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_repo_group(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'csrf_token': self.csrf_token})

        msg = 'user "%s" still owns 1 repository groups and cannot be removed. ' \
              'Switch owners or remove those repository groups:%s' % (username,
                                                                      obj_name)
        assert_session_flash(response, msg)
        fixture.destroy_repo_group(obj_name)

    def test_delete_owner_of_repository_group_detaching(self):
        self.log_user()
        username = 'newtestuserdeleteme_repo_group_owner_detach'
        obj_name = 'test_group'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_repo_group(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'user_repo_groups': 'delete',
                                         'csrf_token': self.csrf_token})

        msg = 'Deleted 1 repository groups'
        assert_session_flash(response, msg)

    def test_delete_owner_of_repository_group_deleting(self):
        self.log_user()
        username = 'newtestuserdeleteme_repo_group_owner_delete'
        obj_name = 'test_group'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_repo_group(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'user_repo_groups': 'detach',
                                         'csrf_token': self.csrf_token})

        msg = 'Detached 1 repository groups'
        assert_session_flash(response, msg)
        fixture.destroy_repo_group(obj_name)

    def test_delete_owner_of_user_group(self):
        self.log_user()
        username = 'newtestuserdeleteme_user_group_owner'
        obj_name = 'test_user_group'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_user_group(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'csrf_token': self.csrf_token})

        msg = 'user "%s" still owns 1 user groups and cannot be removed. ' \
              'Switch owners or remove those user groups:%s' % (username,
                                                                obj_name)
        assert_session_flash(response, msg)
        fixture.destroy_user_group(obj_name)

    def test_delete_owner_of_user_group_detaching(self):
        self.log_user()
        username = 'newtestuserdeleteme_user_group_owner_detaching'
        obj_name = 'test_user_group'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_user_group(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        try:
            response = self.app.post(url('user', user_id=new_user.user_id),
                                     params={'_method': 'delete',
                                             'user_user_groups': 'detach',
                                             'csrf_token': self.csrf_token})

            msg = 'Detached 1 user groups'
            assert_session_flash(response, msg)
        finally:
            fixture.destroy_user_group(obj_name)

    def test_delete_owner_of_user_group_deleting(self):
        self.log_user()
        username = 'newtestuserdeleteme_user_group_owner_deleting'
        obj_name = 'test_user_group'
        usr = fixture.create_user(name=username)
        self.destroy_users.add(username)
        fixture.create_user_group(obj_name, cur_user=usr.username)

        new_user = Session().query(User)\
            .filter(User.username == username).one()
        response = self.app.post(url('user', user_id=new_user.user_id),
                                 params={'_method': 'delete',
                                         'user_user_groups': 'delete',
                                         'csrf_token': self.csrf_token})

        msg = 'Deleted 1 user groups'
        assert_session_flash(response, msg)

    def test_show(self):
        self.app.get(url('user', user_id=1))

    def test_edit(self):
        self.log_user()
        user = User.get_by_username(TEST_USER_ADMIN_LOGIN)
        self.app.get(url('edit_user', user_id=user.user_id))

    @pytest.mark.parametrize(
        'repo_create, repo_create_write, user_group_create, repo_group_create,'
        'fork_create, inherit_default_permissions, expect_error,'
        'expect_form_error', [
            ('hg.create.none', 'hg.create.write_on_repogroup.false',
             'hg.usergroup.create.false', 'hg.repogroup.create.false',
             'hg.fork.none', 'hg.inherit_default_perms.false', False, False),
            ('hg.create.repository', 'hg.create.write_on_repogroup.false',
             'hg.usergroup.create.false', 'hg.repogroup.create.false',
             'hg.fork.none', 'hg.inherit_default_perms.false', False, False),
            ('hg.create.repository', 'hg.create.write_on_repogroup.true',
             'hg.usergroup.create.true', 'hg.repogroup.create.true',
             'hg.fork.repository', 'hg.inherit_default_perms.false', False,
             False),
            ('hg.create.XXX', 'hg.create.write_on_repogroup.true',
             'hg.usergroup.create.true', 'hg.repogroup.create.true',
             'hg.fork.repository', 'hg.inherit_default_perms.false', False,
             True),
            ('', '', '', '', '', '', True, False),
        ])
    def test_global_perms_on_user(
            self, repo_create, repo_create_write, user_group_create,
            repo_group_create, fork_create, expect_error, expect_form_error,
            inherit_default_permissions):
        self.log_user()
        user = fixture.create_user('dummy')
        uid = user.user_id

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
            url('edit_user_global_perms', user_id=uid),
            params=perm_params)

        if expect_form_error:
            assert response.status_int == 200
            response.mustcontain('Value must be one of')
        else:
            if expect_error:
                msg = 'An error occurred during permissions saving'
            else:
                msg = 'User global permissions updated successfully'
                ug = User.get(uid)
                del perm_params['_method']
                del perm_params['inherit_default_permissions']
                del perm_params['csrf_token']
                assert perm_params == ug.get_default_perms()
            assert_session_flash(response, msg)
        fixture.destroy_user(uid)

    def test_global_permissions_initial_values(self, user_util):
        self.log_user()
        user = user_util.create_user()
        uid = user.user_id
        response = self.app.get(url('edit_user_global_perms', user_id=uid))
        default_user = User.get_default_user()
        default_permissions = default_user.get_default_perms()
        assert_response = AssertResponse(response)
        expected_permissions = (
            'default_repo_create', 'default_repo_create_on_write',
            'default_fork_create', 'default_repo_group_create',
            'default_user_group_create', 'default_inherit_default_permissions')
        for permission in expected_permissions:
            css_selector = '[name={}][checked=checked]'.format(permission)
            element = assert_response.get_element(css_selector)
            assert element.value == default_permissions[permission]

    def test_ips(self):
        self.log_user()
        user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
        response = self.app.get(url('edit_user_ips', user_id=user.user_id))
        response.mustcontain('All IP addresses are allowed')

    @pytest.mark.parametrize("test_name, ip, ip_range, failure", [
        ('127/24', '127.0.0.1/24', '127.0.0.0 - 127.0.0.255', False),
        ('10/32', '10.0.0.10/32', '10.0.0.10 - 10.0.0.10', False),
        ('0/16', '0.0.0.0/16', '0.0.0.0 - 0.0.255.255', False),
        ('0/8', '0.0.0.0/8', '0.0.0.0 - 0.255.255.255', False),
        ('127_bad_mask', '127.0.0.1/99', '127.0.0.1 - 127.0.0.1', True),
        ('127_bad_ip', 'foobar', 'foobar', True),
    ])
    def test_add_ip(self, test_name, ip, ip_range, failure):
        self.log_user()
        user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
        user_id = user.user_id

        response = self.app.post(url('edit_user_ips', user_id=user_id),
                                 params={'new_ip': ip, '_method': 'put',
                                         'csrf_token': self.csrf_token})

        if failure:
            assert_session_flash(
                response, 'Please enter a valid IPv4 or IpV6 address')
            response = self.app.get(url('edit_user_ips', user_id=user_id))
            response.mustcontain(no=[ip])
            response.mustcontain(no=[ip_range])

        else:
            response = self.app.get(url('edit_user_ips', user_id=user_id))
            response.mustcontain(ip)
            response.mustcontain(ip_range)

        # cleanup
        for del_ip in UserIpMap.query().filter(
                UserIpMap.user_id == user_id).all():
            Session().delete(del_ip)
            Session().commit()

    def test_delete_ip(self):
        self.log_user()
        user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
        user_id = user.user_id
        ip = '127.0.0.1/32'
        ip_range = '127.0.0.1 - 127.0.0.1'
        new_ip = UserModel().add_extra_ip(user_id, ip)
        Session().commit()
        new_ip_id = new_ip.ip_id

        response = self.app.get(url('edit_user_ips', user_id=user_id))
        response.mustcontain(ip)
        response.mustcontain(ip_range)

        self.app.post(url('edit_user_ips', user_id=user_id),
                      params={'_method': 'delete', 'del_ip_id': new_ip_id,
                              'csrf_token': self.csrf_token})

        response = self.app.get(url('edit_user_ips', user_id=user_id))
        response.mustcontain('All IP addresses are allowed')
        response.mustcontain(no=[ip])
        response.mustcontain(no=[ip_range])

    def test_auth_tokens(self):
        self.log_user()

        user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
        response = self.app.get(
            url('edit_user_auth_tokens', user_id=user.user_id))
        response.mustcontain(user.api_key)
        response.mustcontain('expires: never')

    @pytest.mark.parametrize("desc, lifetime", [
        ('forever', -1),
        ('5mins', 60*5),
        ('30days', 60*60*24*30),
    ])
    def test_add_auth_token(self, desc, lifetime):
        self.log_user()
        user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
        user_id = user.user_id

        response = self.app.post(
            url('edit_user_auth_tokens', user_id=user_id),
            {'_method': 'put', 'description': desc, 'lifetime': lifetime,
             'csrf_token': self.csrf_token})
        assert_session_flash(response, 'Auth token successfully created')
        try:
            response = response.follow()
            user = User.get(user_id)
            for auth_token in user.auth_tokens:
                response.mustcontain(auth_token)
        finally:
            for api_key in UserApiKeys.query().filter(
                    UserApiKeys.user_id == user_id).all():
                Session().delete(api_key)
                Session().commit()

    def test_remove_auth_token(self):
        self.log_user()
        user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
        user_id = user.user_id

        response = self.app.post(
            url('edit_user_auth_tokens', user_id=user_id),
            {'_method': 'put', 'description': 'desc', 'lifetime': -1,
             'csrf_token': self.csrf_token})
        assert_session_flash(response, 'Auth token successfully created')
        response = response.follow()

        # now delete our key
        keys = UserApiKeys.query().filter(UserApiKeys.user_id == user_id).all()
        assert 1 == len(keys)

        response = self.app.post(
            url('edit_user_auth_tokens', user_id=user_id),
            {'_method': 'delete', 'del_auth_token': keys[0].api_key,
             'csrf_token': self.csrf_token})
        assert_session_flash(response, 'Auth token successfully deleted')
        keys = UserApiKeys.query().filter(UserApiKeys.user_id == user_id).all()
        assert 0 == len(keys)

    def test_reset_main_auth_token(self):
        self.log_user()
        user = User.get_by_username(TEST_USER_REGULAR_LOGIN)
        user_id = user.user_id
        api_key = user.api_key
        response = self.app.get(url('edit_user_auth_tokens', user_id=user_id))
        response.mustcontain(api_key)
        response.mustcontain('expires: never')

        response = self.app.post(
            url('edit_user_auth_tokens', user_id=user_id),
            {'_method': 'delete', 'del_auth_token_builtin': api_key,
             'csrf_token': self.csrf_token})
        assert_session_flash(response, 'Auth token successfully reset')
        response = response.follow()
        response.mustcontain(no=[api_key])
