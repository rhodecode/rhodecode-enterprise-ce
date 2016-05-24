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

from pyramid.exceptions import ConfigurationError
from zope.interface import implementer

from rhodecode.authentication.interface import IAuthnPluginRegistry
from rhodecode.lib.utils2 import safe_str

log = logging.getLogger(__name__)


@implementer(IAuthnPluginRegistry)
class AuthenticationPluginRegistry(object):
    def __init__(self):
        self._plugins = {}

    def add_authn_plugin(self, config, plugin):
        plugin_id = plugin.get_id()
        if plugin_id in self._plugins.keys():
            raise ConfigurationError(
                'Cannot register authentication plugin twice: "%s"', plugin_id)
        else:
            log.debug('Register authentication plugin: "%s"', plugin_id)
            self._plugins[plugin_id] = plugin

    def get_plugins(self):
        def sort_key(plugin):
            return str.lower(safe_str(plugin.get_display_name()))

        return sorted(self._plugins.values(), key=sort_key)

    def get_plugin(self, plugin_id):
        return self._plugins.get(plugin_id, None)
