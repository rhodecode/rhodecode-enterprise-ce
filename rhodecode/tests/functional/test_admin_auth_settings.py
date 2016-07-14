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

from rhodecode.tests import assert_session_flash
from rhodecode.tests.utils import AssertResponse
from rhodecode.model.db import Session
from rhodecode.model.settings import SettingsModel


def assert_auth_settings_updated(response):
    assert response.status_int == 302, 'Expected response HTTP Found 302'
    assert_session_flash(response, 'Auth settings updated successfully')


@pytest.mark.usefixtures("autologin_user", "app")
class TestAuthSettingsController(object):

    def _enable_plugins(self, plugins_list, csrf_token, override=None,
                        verify_response=False):
        test_url = '/_admin/auth'
        params = {
            'auth_plugins': plugins_list,
            'csrf_token': csrf_token,
        }
        if override:
            params.update(override)
        _enabled_plugins = []
        for plugin in plugins_list.split(','):
            plugin_name = plugin.partition('#')[-1]
            enabled_plugin = '%s_enabled' % plugin_name
            cache_ttl = '%s_auth_cache_ttl' % plugin_name

            # default params that are needed for each plugin,
            # `enabled` and `auth_cache_ttl`
            params.update({
                enabled_plugin: True,
                cache_ttl: 0
            })
            _enabled_plugins.append(enabled_plugin)

        # we need to clean any enabled plugin before, since they require
        # form params to be present
        db_plugin = SettingsModel().get_setting_by_name('auth_plugins')
        db_plugin.app_settings_value = \
            'egg:rhodecode-enterprise-ce#rhodecode'
        Session().add(db_plugin)
        Session().commit()
        for _plugin in _enabled_plugins:
            db_plugin = SettingsModel().get_setting_by_name(_plugin)
            if db_plugin:
                Session.delete(db_plugin)
        Session().commit()

        response = self.app.post(url=test_url, params=params)

        if verify_response:
            assert_auth_settings_updated(response)
        return params

    def _post_ldap_settings(self, params, override=None, force=False):

        params.update({
            'filter': 'user',
            'user_member_of': '',
            'user_search_base': '',
            'user_search_filter': 'test_filter',

            'host': 'dc.example.com',
            'port': '999',
            'tls_kind': 'PLAIN',
            'tls_reqcert': 'NEVER',

            'dn_user': 'test_user',
            'dn_pass': 'test_pass',
            'base_dn': 'test_base_dn',
            'search_scope': 'BASE',
            'attr_login': 'test_attr_login',
            'attr_firstname': 'ima',
            'attr_lastname': 'tester',
            'attr_email': 'test@example.com',
            'auth_cache_ttl': '0',
        })
        if force:
            params = {}
        params.update(override or {})

        test_url = '/_admin/auth/ldap/'

        response = self.app.post(url=test_url, params=params)
        return response

    def test_index(self):
        response = self.app.get('/_admin/auth')
        response.mustcontain('Authentication Plugins')

    @pytest.mark.parametrize("disable_plugin, needs_import", [
        ('egg:rhodecode-enterprise-ce#headers', None),
        ('egg:rhodecode-enterprise-ce#crowd', None),
        ('egg:rhodecode-enterprise-ce#jasig_cas', None),
        ('egg:rhodecode-enterprise-ce#ldap', None),
        ('egg:rhodecode-enterprise-ce#pam',  "pam"),
    ])
    def test_disable_plugin(self, csrf_token, disable_plugin, needs_import):
        # TODO: johbo: "pam" is currently not available on darwin,
        # although the docs state that it should work on darwin.
        if needs_import:
            pytest.importorskip(needs_import)

        self._enable_plugins(
            'egg:rhodecode-enterprise-ce#rhodecode,' + disable_plugin,
            csrf_token, verify_response=True)

        self._enable_plugins(
            'egg:rhodecode-enterprise-ce#rhodecode', csrf_token,
            verify_response=True)

    def test_ldap_save_settings(self, csrf_token):
        params = self._enable_plugins(
            'egg:rhodecode-enterprise-ce#rhodecode,'
            'egg:rhodecode-enterprise-ce#ldap',
            csrf_token)
        response = self._post_ldap_settings(params)
        assert_auth_settings_updated(response)

        new_settings = SettingsModel().get_auth_settings()
        assert new_settings['auth_ldap_host'] == u'dc.example.com', \
            'fail db write compare'

    def test_ldap_error_form_wrong_port_number(self, csrf_token):
        params = self._enable_plugins(
            'egg:rhodecode-enterprise-ce#rhodecode,'
            'egg:rhodecode-enterprise-ce#ldap',
            csrf_token)
        invalid_port_value = 'invalid-port-number'
        response = self._post_ldap_settings(params, override={
            'port': invalid_port_value,
        })
        assertr = AssertResponse(response)
        assertr.element_contains(
            '.form .field #port ~ .error-message',
            invalid_port_value)

    def test_ldap_error_form(self, csrf_token):
        params = self._enable_plugins(
            'egg:rhodecode-enterprise-ce#rhodecode,'
            'egg:rhodecode-enterprise-ce#ldap',
            csrf_token)
        response = self._post_ldap_settings(params, override={
            'attr_login': '',
        })
        response.mustcontain("""<span class="error-message">The LDAP Login"""
                             """ attribute of the CN must be specified""")

    def test_post_ldap_group_settings(self, csrf_token):
        params = self._enable_plugins(
            'egg:rhodecode-enterprise-ce#rhodecode,'
            'egg:rhodecode-enterprise-ce#ldap',
            csrf_token)

        response = self._post_ldap_settings(params, override={
            'host': 'dc-legacy.example.com',
            'port': '999',
            'tls_kind': 'PLAIN',
            'tls_reqcert': 'NEVER',
            'dn_user': 'test_user',
            'dn_pass': 'test_pass',
            'base_dn': 'test_base_dn',
            'filter': 'test_filter',
            'search_scope': 'BASE',
            'attr_login': 'test_attr_login',
            'attr_firstname': 'ima',
            'attr_lastname': 'tester',
            'attr_email': 'test@example.com',
            'auth_cache_ttl': '60',
            'csrf_token': csrf_token,
            }
        )
        assert_auth_settings_updated(response)

        new_settings = SettingsModel().get_auth_settings()
        assert new_settings['auth_ldap_host'] == u'dc-legacy.example.com', \
            'fail db write compare'
