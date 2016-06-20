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
