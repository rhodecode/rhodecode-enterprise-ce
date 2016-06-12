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

from rhodecode.lib.auth import _RhodeCodeCryptoBCrypt
from rhodecode.authentication.base import RhodeCodeAuthPluginBase
from rhodecode.authentication.plugins.auth_ldap import RhodeCodeAuthPlugin
from rhodecode.model import db


def test_authenticate_returns_from_auth(stub_auth_data):
    plugin = RhodeCodeAuthPluginBase('stub_id')
    with mock.patch.object(plugin, 'auth') as auth_mock:
        auth_mock.return_value = stub_auth_data
        result = plugin._authenticate(mock.Mock(), 'test', 'password', {})
    assert stub_auth_data == result


def test_authenticate_returns_empty_auth_data():
    auth_data = {}
    plugin = RhodeCodeAuthPluginBase('stub_id')
    with mock.patch.object(plugin, 'auth') as auth_mock:
        auth_mock.return_value = auth_data
        result = plugin._authenticate(mock.Mock(), 'test', 'password', {})
    assert auth_data == result


def test_authenticate_skips_hash_migration_if_mismatch(stub_auth_data):
    stub_auth_data['_hash_migrate'] = 'new-hash'
    plugin = RhodeCodeAuthPluginBase('stub_id')
    with mock.patch.object(plugin, 'auth') as auth_mock:
        auth_mock.return_value = stub_auth_data
        result = plugin._authenticate(mock.Mock(), 'test', 'password', {})

    user = db.User.get_by_username(stub_auth_data['username'])
    assert user.password != 'new-hash'
    assert result == stub_auth_data


def test_authenticate_migrates_to_new_hash(stub_auth_data):
    new_password = b'new-password'
    new_hash = _RhodeCodeCryptoBCrypt().hash_create(new_password)
    stub_auth_data['_hash_migrate'] = new_hash
    plugin = RhodeCodeAuthPluginBase('stub_id')
    with mock.patch.object(plugin, 'auth') as auth_mock:
        auth_mock.return_value = stub_auth_data
        result = plugin._authenticate(
            mock.Mock(), stub_auth_data['username'], new_password, {})

    user = db.User.get_by_username(stub_auth_data['username'])
    assert user.password == new_hash
    assert result == stub_auth_data


@pytest.fixture
def stub_auth_data(user_util):
    user = user_util.create_user()
    data = {
        'username': user.username,
        'password': 'password',
        'email': 'test@example.org',
        'firstname': 'John',
        'lastname': 'Smith',
        'groups': [],
        'active': True,
        'admin': False,
        'extern_name': 'test',
        'extern_type': 'ldap',
        'active_from_extern': True
    }
    return data


class TestRhodeCodeAuthPlugin(object):
    def setup_method(self, method):
        self.finalizers = []
        self.user = mock.Mock()
        self.user.username = 'test'
        self.user.password = 'old-password'
        self.fake_auth = {
            'username': 'test',
            'password': 'test',
            'email': 'test@example.org',
            'firstname': 'John',
            'lastname': 'Smith',
            'groups': [],
            'active': True,
            'admin': False,
            'extern_name': 'test',
            'extern_type': 'ldap',
            'active_from_extern': True
        }

    def teardown_method(self, method):
        if self.finalizers:
            for finalizer in self.finalizers:
                finalizer()
            self.finalizers = []

    def test_fake_password_is_created_for_the_new_user(self):
        self._patch()
        auth_plugin = RhodeCodeAuthPlugin('stub_id')
        auth_plugin._authenticate(self.user, 'test', 'test', [])
        self.password_generator_mock.assert_called_once_with(length=16)
        create_user_kwargs = self.create_user_mock.call_args[1]
        assert create_user_kwargs['password'] == 'new-password'

    def test_fake_password_is_not_created_for_the_existing_user(self):
        self._patch()
        self.get_user_mock.return_value = self.user
        auth_plugin = RhodeCodeAuthPlugin('stub_id')
        auth_plugin._authenticate(self.user, 'test', 'test', [])
        assert self.password_generator_mock.called is False
        create_user_kwargs = self.create_user_mock.call_args[1]
        assert create_user_kwargs['password'] == self.user.password

    def _patch(self):
        get_user_patch = mock.patch('rhodecode.model.db.User.get_by_username')
        self.get_user_mock = get_user_patch.start()
        self.get_user_mock.return_value = None
        self.finalizers.append(get_user_patch.stop)

        create_user_patch = mock.patch(
            'rhodecode.model.user.UserModel.create_or_update')
        self.create_user_mock = create_user_patch.start()
        self.create_user_mock.return_value = None
        self.finalizers.append(create_user_patch.stop)

        auth_patch = mock.patch.object(RhodeCodeAuthPlugin, 'auth')
        self.auth_mock = auth_patch.start()
        self.auth_mock.return_value = self.fake_auth
        self.finalizers.append(auth_patch.stop)

        password_generator_patch = mock.patch(
            'rhodecode.lib.auth.PasswordGenerator.gen_password')
        self.password_generator_mock = password_generator_patch.start()
        self.password_generator_mock.return_value = 'new-password'
        self.finalizers.append(password_generator_patch.stop)


def test_missing_ldap():
    from rhodecode.model.validators import Missing

    try:
        import ldap_not_existing
    except ImportError:
        # means that python-ldap is not installed
        ldap_not_existing = Missing

    # missing is singleton
    assert ldap_not_existing == Missing


def test_import_ldap():
    from rhodecode.model.validators import Missing

    try:
        import ldap
    except ImportError:
        # means that python-ldap is not installed
        ldap = Missing

    # missing is singleton
    assert False is (ldap == Missing)
