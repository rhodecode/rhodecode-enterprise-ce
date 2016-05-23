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
from pyramid.i18n import TranslationStringFactory

from rhodecode.lib.utils2 import safe_str
from rhodecode.model.settings import SettingsModel

_ = TranslationStringFactory('rhodecode-enterprise')

log = logging.getLogger(__name__)


class AuthnResourceBase(object):
    __name__ = None
    __parent__ = None

    def get_root(self):
        current = self
        while current.__parent__ is not None:
            current = current.__parent__
        return current


class AuthnPluginResourceBase(AuthnResourceBase):

    def __init__(self, plugin):
        self.plugin = plugin
        self.__name__ = plugin.name
        self.display_name = plugin.get_display_name()


class AuthnRootResource(AuthnResourceBase):
    """
    This is the root traversal resource object for the authentication settings.
    """

    def __init__(self):
        self._store = {}
        self._resource_name_map = {}
        self.display_name = _('Global')

    def __getitem__(self, key):
        """
        Customized get item function to return only items (plugins) that are
        activated.
        """
        if self._is_item_active(key):
            return self._store[key]
        else:
            raise KeyError('Authentication plugin "{}" is not active.'.format(
                key))

    def __iter__(self):
        for key in self._store.keys():
            if self._is_item_active(key):
                yield self._store[key]

    def _is_item_active(self, key):
        activated_plugins = SettingsModel().get_auth_plugins()
        plugin_id = self.get_plugin_id(key)
        return plugin_id in activated_plugins

    def get_plugin_id(self, resource_name):
        """
        Return the plugin id for the given traversal resource name.
        """
        # TODO: Store this info in the resource element.
        return self._resource_name_map[resource_name]

    def get_sorted_list(self):
        """
        Returns a sorted list of sub resources for displaying purposes.
        """
        def sort_key(resource):
            return str.lower(safe_str(resource.display_name))

        active = [item for item in self]
        return sorted(active, key=sort_key)

    def get_nav_list(self):
        """
        Returns a sorted list of resources for displaying the navigation.
        """
        list = self.get_sorted_list()
        list.insert(0, self)
        return list

    def add_authn_resource(self, config, plugin_id, resource):
        """
        Register a traversal resource as a sub element to the authentication
        settings. This method is registered as a directive on the pyramid
        configurator object and called by plugins.
        """

        def _ensure_unique_name(name, limit=100):
            counter = 1
            current = name
            while current in self._store.keys():
                current = '{}{}'.format(name, counter)
                counter += 1
                if counter > limit:
                    raise ConfigurationError(
                        'Cannot build unique name for traversal resource "%s" '
                        'registered by plugin "%s"', name, plugin_id)
            return current

        # Allow plugin resources with identical names by rename duplicates.
        unique_name = _ensure_unique_name(resource.__name__)
        if unique_name != resource.__name__:
            log.warn('Name collision for traversal resource "%s" registered '
                     'by authentication plugin "%s"', resource.__name__,
                     plugin_id)
            resource.__name__ = unique_name

        log.debug('Register traversal resource "%s" for plugin "%s"',
                  unique_name, plugin_id)
        self._resource_name_map[unique_name] = plugin_id
        resource.__parent__ = self
        self._store[unique_name] = resource


root = AuthnRootResource()


def root_factory(request=None):
    """
    Returns the root traversal resource instance used for the authentication
    settings route.
    """
    return root
