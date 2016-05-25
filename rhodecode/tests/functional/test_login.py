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

import urlparse

import mock
import pytest

from rhodecode.config.routing import ADMIN_PREFIX
from rhodecode.tests import (
    assert_session_flash, url, HG_REPO, TEST_USER_ADMIN_LOGIN)
from rhodecode.tests.fixture import Fixture
from rhodecode.tests.utils import AssertResponse, get_session_from_response
from rhodecode.lib.auth import check_password, generate_auth_token
from rhodecode.lib import helpers as h
from rhodecode.model.auth_token import AuthTokenModel
from rhodecode.model import validators
from rhodecode.model.db import User, Notification
from rhodecode.model.meta import Session

fixture = Fixture()

# Hardcode URLs because we don't have a request object to use
# pyramids URL generation methods.
login_url = ADMIN_PREFIX + '/login'
logut_url = ADMIN_PREFIX + '/logout'
register_url = ADMIN_PREFIX + '/register'
pwd_reset_url = ADMIN_PREFIX + '/password_reset'
pwd_reset_confirm_url = ADMIN_PREFIX + '/password_reset_confirmation'


@pytest.mark.usefixtures('app')
class TestLoginController:
    destroy_users = set()

    @classmethod
    def teardown_class(cls):
        fixture.destroy_users(cls.destroy_users)

    def teardown_method(self, method):
        for n in Notification.query().all():
            Session().delete(n)

        Session().commit()
        assert Notification.query().all() == []

    def test_index(self):
        response = self.app.get(login_url)
        assert response.status == '200 OK'
        # Test response...

    def test_login_admin_ok(self):
        response = self.app.post(login_url,
                                 {'username': 'test_admin',
                                  'password': 'test12'})
        assert response.status == '302 Found'
        session = get_session_from_response(response)
        username = session['rhodecode_user'].get('username')
        assert username == 'test_admin'
        response = response.follow()
        response.mustcontain('/%s' % HG_REPO)

    def test_login_regular_ok(self):
        response = self.app.post(login_url,
                                 {'username': 'test_regular',
                                  'password': 'test12'})

        assert response.status == '302 Found'
        session = get_session_from_response(response)
        username = session['rhodecode_user'].get('username')
        assert username == 'test_regular'
        response = response.follow()
        response.mustcontain('/%s' % HG_REPO)

    def test_login_ok_came_from(self):
        test_came_from = '/_admin/users?branch=stable'
        _url = '{}?came_from={}'.format(login_url, test_came_from)
        response = self.app.post(
            _url, {'username': 'test_admin', 'password': 'test12'})
        assert response.status == '302 Found'
        assert 'branch=stable' in response.location
        response = response.follow()

        assert response.status == '200 OK'
        response.mustcontain('Users administration')

    def test_redirect_to_login_with_get_args(self):
        with fixture.anon_access(False):
            kwargs = {'branch': 'stable'}
            response = self.app.get(
                url('summary_home', repo_name=HG_REPO, **kwargs))
            assert response.status == '302 Found'
            response_query = urlparse.parse_qsl(response.location)
            assert 'branch=stable' in response_query[0][1]

    def test_login_form_with_get_args(self):
        _url = '{}?came_from=/_admin/users,branch=stable'.format(login_url)
        response = self.app.get(_url)
        assert 'branch%3Dstable' in response.form.action

    @pytest.mark.parametrize("url_came_from", [
        'data:text/html,<script>window.alert("xss")</script>',
        'mailto:test@rhodecode.org',
        'file:///etc/passwd',
        'ftp://some.ftp.server',
        'http://other.domain',
        '/\r\nX-Forwarded-Host: http://example.org',
    ])
    def test_login_bad_came_froms(self, url_came_from):
        _url = '{}?came_from={}'.format(login_url, url_came_from)
        response = self.app.post(
            _url,
            {'username': 'test_admin', 'password': 'test12'})
        assert response.status == '302 Found'
        response = response.follow()
        assert response.status == '200 OK'
        assert response.request.path == '/'

    def test_login_short_password(self):
        response = self.app.post(login_url,
                                 {'username': 'test_admin',
                                  'password': 'as'})
        assert response.status == '200 OK'

        response.mustcontain('Enter 3 characters or more')

    def test_login_wrong_non_ascii_password(self, user_regular):
        response = self.app.post(
            login_url,
            {'username': user_regular.username,
             'password': u'invalid-non-asci\xe4'.encode('utf8')})

        response.mustcontain('invalid user name')
        response.mustcontain('invalid password')

    def test_login_with_non_ascii_password(self, user_util):
        password = u'valid-non-ascii\xe4'
        user = user_util.create_user(password=password)
        response = self.app.post(
            login_url,
            {'username': user.username,
             'password': password.encode('utf-8')})
        assert response.status_code == 302

    def test_login_wrong_username_password(self):
        response = self.app.post(login_url,
                                 {'username': 'error',
                                  'password': 'test12'})

        response.mustcontain('invalid user name')
        response.mustcontain('invalid password')

    def test_login_admin_ok_password_migration(self, real_crypto_backend):
        from rhodecode.lib import auth

        # create new user, with sha256 password
        temp_user = 'test_admin_sha256'
        user = fixture.create_user(temp_user)
        user.password = auth._RhodeCodeCryptoSha256().hash_create(
            b'test123')
        Session().add(user)
        Session().commit()
        self.destroy_users.add(temp_user)
        response = self.app.post(login_url,
                                 {'username': temp_user,
                                  'password': 'test123'})

        assert response.status == '302 Found'
        session = get_session_from_response(response)
        username = session['rhodecode_user'].get('username')
        assert username == temp_user
        response = response.follow()
        response.mustcontain('/%s' % HG_REPO)

        # new password should be bcrypted, after log-in and transfer
        user = User.get_by_username(temp_user)
        assert user.password.startswith('$')

    # REGISTRATIONS
    def test_register(self):
        response = self.app.get(register_url)
        response.mustcontain('Create an Account')

    def test_register_err_same_username(self):
        uname = 'test_admin'
        response = self.app.post(
            register_url,
            {
                'username': uname,
                'password': 'test12',
                'password_confirmation': 'test12',
                'email': 'goodmail@domain.com',
                'firstname': 'test',
                'lastname': 'test'
            }
        )

        assertr = AssertResponse(response)
        msg = validators.ValidUsername()._messages['username_exists']
        msg = msg % {'username': uname}
        assertr.element_contains('#username+.error-message', msg)

    def test_register_err_same_email(self):
        response = self.app.post(
            register_url,
            {
                'username': 'test_admin_0',
                'password': 'test12',
                'password_confirmation': 'test12',
                'email': 'test_admin@mail.com',
                'firstname': 'test',
                'lastname': 'test'
            }
        )

        assertr = AssertResponse(response)
        msg = validators.UniqSystemEmail()()._messages['email_taken']
        assertr.element_contains('#email+.error-message', msg)

    def test_register_err_same_email_case_sensitive(self):
        response = self.app.post(
            register_url,
            {
                'username': 'test_admin_1',
                'password': 'test12',
                'password_confirmation': 'test12',
                'email': 'TesT_Admin@mail.COM',
                'firstname': 'test',
                'lastname': 'test'
            }
        )
        assertr = AssertResponse(response)
        msg = validators.UniqSystemEmail()()._messages['email_taken']
        assertr.element_contains('#email+.error-message', msg)

    def test_register_err_wrong_data(self):
        response = self.app.post(
            register_url,
            {
                'username': 'xs',
                'password': 'test',
                'password_confirmation': 'test',
                'email': 'goodmailm',
                'firstname': 'test',
                'lastname': 'test'
            }
        )
        assert response.status == '200 OK'
        response.mustcontain('An email address must contain a single @')
        response.mustcontain('Enter a value 6 characters long or more')

    def test_register_err_username(self):
        response = self.app.post(
            register_url,
            {
                'username': 'error user',
                'password': 'test12',
                'password_confirmation': 'test12',
                'email': 'goodmailm',
                'firstname': 'test',
                'lastname': 'test'
            }
        )

        response.mustcontain('An email address must contain a single @')
        response.mustcontain(
            'Username may only contain '
            'alphanumeric characters underscores, '
            'periods or dashes and must begin with '
            'alphanumeric character')

    def test_register_err_case_sensitive(self):
        usr = 'Test_Admin'
        response = self.app.post(
            register_url,
            {
                'username': usr,
                'password': 'test12',
                'password_confirmation': 'test12',
                'email': 'goodmailm',
                'firstname': 'test',
                'lastname': 'test'
            }
        )

        assertr = AssertResponse(response)
        msg = validators.ValidUsername()._messages['username_exists']
        msg = msg % {'username': usr}
        assertr.element_contains('#username+.error-message', msg)

    def test_register_special_chars(self):
        response = self.app.post(
            register_url,
            {
                'username': 'xxxaxn',
                'password': 'ąćźżąśśśś',
                'password_confirmation': 'ąćźżąśśśś',
                'email': 'goodmailm@test.plx',
                'firstname': 'test',
                'lastname': 'test'
            }
        )

        msg = validators.ValidPassword()._messages['invalid_password']
        response.mustcontain(msg)

    def test_register_password_mismatch(self):
        response = self.app.post(
            register_url,
            {
                'username': 'xs',
                'password': '123qwe',
                'password_confirmation': 'qwe123',
                'email': 'goodmailm@test.plxa',
                'firstname': 'test',
                'lastname': 'test'
            }
        )
        msg = validators.ValidPasswordsMatch()._messages['password_mismatch']
        response.mustcontain(msg)

    def test_register_ok(self):
        username = 'test_regular4'
        password = 'qweqwe'
        email = 'marcin@test.com'
        name = 'testname'
        lastname = 'testlastname'

        response = self.app.post(
            register_url,
            {
                'username': username,
                'password': password,
                'password_confirmation': password,
                'email': email,
                'firstname': name,
                'lastname': lastname,
                'admin': True
            }
        )  # This should be overriden
        assert response.status == '302 Found'
        assert_session_flash(
            response, 'You have successfully registered with RhodeCode')

        ret = Session().query(User).filter(
            User.username == 'test_regular4').one()
        assert ret.username == username
        assert check_password(password, ret.password)
        assert ret.email == email
        assert ret.name == name
        assert ret.lastname == lastname
        assert ret.api_key is not None
        assert not ret.admin

    def test_forgot_password_wrong_mail(self):
        bad_email = 'marcin@wrongmail.org'
        response = self.app.post(
            pwd_reset_url,
            {'email': bad_email, }
        )

        msg = validators.ValidSystemEmail()._messages['non_existing_email']
        msg = h.html_escape(msg % {'email': bad_email})
        response.mustcontain()

    def test_forgot_password(self):
        response = self.app.get(pwd_reset_url)
        assert response.status == '200 OK'

        username = 'test_password_reset_1'
        password = 'qweqwe'
        email = 'marcin@python-works.com'
        name = 'passwd'
        lastname = 'reset'

        new = User()
        new.username = username
        new.password = password
        new.email = email
        new.name = name
        new.lastname = lastname
        new.api_key = generate_auth_token(username)
        Session().add(new)
        Session().commit()

        response = self.app.post(pwd_reset_url,
                                 {'email': email, })

        assert_session_flash(
            response, 'Your password reset link was sent')

        response = response.follow()

        # BAD KEY

        key = "bad"
        confirm_url = '{}?key={}'.format(pwd_reset_confirm_url, key)
        response = self.app.get(confirm_url)
        assert response.status == '302 Found'
        assert response.location.endswith(pwd_reset_url)

        # GOOD KEY

        key = User.get_by_username(username).api_key
        confirm_url = '{}?key={}'.format(pwd_reset_confirm_url, key)
        response = self.app.get(confirm_url)
        assert response.status == '302 Found'
        assert response.location.endswith(login_url)

        assert_session_flash(
            response,
            'Your password reset was successful, '
            'a new password has been sent to your email')

        response = response.follow()

    def _get_api_whitelist(self, values=None):
        config = {'api_access_controllers_whitelist': values or []}
        return config

    @pytest.mark.parametrize("test_name, auth_token", [
        ('none', None),
        ('empty_string', ''),
        ('fake_number', '123456'),
        ('proper_auth_token', None)
    ])
    def test_access_not_whitelisted_page_via_auth_token(self, test_name,
                                                        auth_token):
        whitelist = self._get_api_whitelist([])
        with mock.patch.dict('rhodecode.CONFIG', whitelist):
            assert [] == whitelist['api_access_controllers_whitelist']
            if test_name == 'proper_auth_token':
                # use builtin if api_key is None
                auth_token = User.get_first_admin().api_key

            with fixture.anon_access(False):
                self.app.get(url(controller='changeset',
                                 action='changeset_raw',
                                 repo_name=HG_REPO, revision='tip',
                                 api_key=auth_token),
                             status=302)

    @pytest.mark.parametrize("test_name, auth_token, code", [
        ('none', None, 302),
        ('empty_string', '', 302),
        ('fake_number', '123456', 302),
        ('proper_auth_token', None, 200)
    ])
    def test_access_whitelisted_page_via_auth_token(self, test_name,
                                                    auth_token, code):
        whitelist = self._get_api_whitelist(
            ['ChangesetController:changeset_raw'])
        with mock.patch.dict('rhodecode.CONFIG', whitelist):
            assert ['ChangesetController:changeset_raw'] == \
                whitelist['api_access_controllers_whitelist']
            if test_name == 'proper_auth_token':
                auth_token = User.get_first_admin().api_key

            with fixture.anon_access(False):
                self.app.get(url(controller='changeset',
                                 action='changeset_raw',
                                 repo_name=HG_REPO, revision='tip',
                                 api_key=auth_token),
                             status=code)

    def test_access_page_via_extra_auth_token(self):
        whitelist = self._get_api_whitelist(
            ['ChangesetController:changeset_raw'])
        with mock.patch.dict('rhodecode.CONFIG', whitelist):
            assert ['ChangesetController:changeset_raw'] == \
                whitelist['api_access_controllers_whitelist']

            new_auth_token = AuthTokenModel().create(
                TEST_USER_ADMIN_LOGIN, 'test')
            Session().commit()
            with fixture.anon_access(False):
                self.app.get(url(controller='changeset',
                                 action='changeset_raw',
                                 repo_name=HG_REPO, revision='tip',
                                 api_key=new_auth_token.api_key),
                             status=200)

    def test_access_page_via_expired_auth_token(self):
        whitelist = self._get_api_whitelist(
            ['ChangesetController:changeset_raw'])
        with mock.patch.dict('rhodecode.CONFIG', whitelist):
            assert ['ChangesetController:changeset_raw'] == \
                whitelist['api_access_controllers_whitelist']

            new_auth_token = AuthTokenModel().create(
                TEST_USER_ADMIN_LOGIN, 'test')
            Session().commit()
            # patch the api key and make it expired
            new_auth_token.expires = 0
            Session().add(new_auth_token)
            Session().commit()
            with fixture.anon_access(False):
                self.app.get(url(controller='changeset',
                                 action='changeset_raw',
                                 repo_name=HG_REPO, revision='tip',
                                 api_key=new_auth_token.api_key),
                             status=302)
