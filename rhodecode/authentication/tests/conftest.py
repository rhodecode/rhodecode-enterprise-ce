# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
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


class EnabledAuthPlugin():
    """
    Context manager that updates the 'auth_plugins' setting in DB to enable
    a plugin. Previous setting is restored on exit. The rhodecode auth plugin
    is also enabled because it is needed to login the test users.
    """

    def __init__(self, plugin):
        self.new_value = set([
            'egg:rhodecode-enterprise-ce#rhodecode',
            plugin.get_id()
        ])

    def __enter__(self):
        from rhodecode.model.settings import SettingsModel
        self._old_value = SettingsModel().get_auth_plugins()
        SettingsModel().create_or_update_setting(
            'auth_plugins', ','.join(self.new_value))

    def __exit__(self, type, value, traceback):
        from rhodecode.model.settings import SettingsModel
        SettingsModel().create_or_update_setting(
            'auth_plugins', ','.join(self._old_value))


class DisabledAuthPlugin():
    """
    Context manager that updates the 'auth_plugins' setting in DB to disable
    a plugin. Previous setting is restored on exit.
    """

    def __init__(self, plugin):
        self.plugin_id = plugin.get_id()

    def __enter__(self):
        from rhodecode.model.settings import SettingsModel
        self._old_value = SettingsModel().get_auth_plugins()
        new_value = [id_ for id_ in self._old_value if id_ != self.plugin_id]
        SettingsModel().create_or_update_setting(
            'auth_plugins', ','.join(new_value))

    def __exit__(self, type, value, traceback):
        from rhodecode.model.settings import SettingsModel
        SettingsModel().create_or_update_setting(
            'auth_plugins', ','.join(self._old_value))


@pytest.fixture(params=[
    ('rhodecode.authentication.plugins.auth_crowd', 'egg:rhodecode-enterprise-ce#crowd'),
    ('rhodecode.authentication.plugins.auth_headers', 'egg:rhodecode-enterprise-ce#headers'),
    ('rhodecode.authentication.plugins.auth_jasig_cas', 'egg:rhodecode-enterprise-ce#jasig_cas'),
    ('rhodecode.authentication.plugins.auth_ldap', 'egg:rhodecode-enterprise-ce#ldap'),
    ('rhodecode.authentication.plugins.auth_pam', 'egg:rhodecode-enterprise-ce#pam'),
    ('rhodecode.authentication.plugins.auth_rhodecode', 'egg:rhodecode-enterprise-ce#rhodecode'),
    ('rhodecode.authentication.plugins.auth_token', 'egg:rhodecode-enterprise-ce#token'),
])
def auth_plugin(request):
    """
    Fixture that provides instance for each authentication plugin. These
    instances are NOT the instances which are registered to the authentication
    registry.
    """
    from importlib import import_module

    # Create plugin instance.
    module, plugin_id = request.param
    plugin_module = import_module(module)
    return plugin_module.plugin_factory(plugin_id)
