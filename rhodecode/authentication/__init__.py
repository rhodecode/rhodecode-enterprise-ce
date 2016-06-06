# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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

import logging
import importlib

from pkg_resources import iter_entry_points
from pyramid.authentication import SessionAuthenticationPolicy

from rhodecode.authentication.registry import AuthenticationPluginRegistry
from rhodecode.authentication.routes import root_factory
from rhodecode.authentication.routes import AuthnRootResource
from rhodecode.config.routing import ADMIN_PREFIX
from rhodecode.model.settings import SettingsModel

log = logging.getLogger(__name__)


# TODO: Currently this is only used to discover the authentication plugins.
# Later on this may be used in a generic way to look up and include all kinds
# of supported enterprise plugins. Therefore this has to be moved and
# refactored to a real 'plugin look up' machinery.
# TODO: When refactoring this think about splitting it up into distinct
# discover, load and include phases.
def _discover_plugins(config, entry_point='enterprise.plugins1'):
    _discovered_plugins = {}

    for ep in iter_entry_points(entry_point):
        plugin_id = 'egg:{}#{}'.format(ep.dist.project_name, ep.name)
        log.debug('Plugin discovered: "%s"', plugin_id)
        module = ep.load()
        plugin = module(plugin_id=plugin_id)
        config.include(plugin.includeme)

    return _discovered_plugins


def _discover_legacy_plugins(config, prefix='py:'):
    """
    Function that imports the legacy plugins stored in the 'auth_plugins'
    setting in database which are using the specified prefix. Normally 'py:' is
    used for the legacy plugins.
    """
    auth_plugins = SettingsModel().get_setting_by_name('auth_plugins')
    enabled_plugins = auth_plugins.app_settings_value
    legacy_plugins = [id_ for id_ in enabled_plugins if id_.startswith(prefix)]

    log.debug('Importing these legacy authentication plugins {}'.format(
        legacy_plugins))

    for plugin_id in legacy_plugins:
        module_name = plugin_id.split(prefix, 1)[-1]
        try:
            log.debug('Import %s', module_name)
            module = importlib.import_module(module_name)
            plugin = module.plugin_factory(plugin_id=plugin_id)
            config.include(plugin.includeme)
        except ImportError as e:
            log.error(
                'Error while importing legacy authentication plugin '
                '"{}": {}'.format(plugin_id, e.message))


def includeme(config):
    # Set authentication policy.
    authn_policy = SessionAuthenticationPolicy()
    config.set_authentication_policy(authn_policy)

    # Create authentication plugin registry and add it to the pyramid registry.
    authn_registry = AuthenticationPluginRegistry(config.get_settings())
    config.add_directive('add_authn_plugin', authn_registry.add_authn_plugin)
    config.registry.registerUtility(authn_registry)

    # Create authentication traversal root resource.
    authn_root_resource = root_factory()
    config.add_directive('add_authn_resource',
                         authn_root_resource.add_authn_resource)

    # Add the authentication traversal route.
    config.add_route('auth_home',
                     ADMIN_PREFIX + '/auth*traverse',
                     factory=root_factory)
    # Add the authentication settings root views.
    config.add_view('rhodecode.authentication.views.AuthSettingsView',
                    attr='index',
                    request_method='GET',
                    route_name='auth_home',
                    context=AuthnRootResource)
    config.add_view('rhodecode.authentication.views.AuthSettingsView',
                    attr='auth_settings',
                    request_method='POST',
                    route_name='auth_home',
                    context=AuthnRootResource)

    # Auto discover authentication plugins and include their configuration.
    _discover_plugins(config)
    _discover_legacy_plugins(config)
