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


import logging
import collections

from pylons import url
from zope.interface import implementer

from rhodecode.admin.interfaces import IAdminNavigationRegistry
from rhodecode.lib.utils import get_registry
from rhodecode.translation import _


log = logging.getLogger(__name__)

NavListEntry = collections.namedtuple('NavListEntry', ['key', 'name', 'url'])


class NavEntry(object):
    """
    Represents an entry in the admin navigation.

    :param key: Unique identifier used to store reference in an OrderedDict.
    :param name: Display name, usually a translation string.
    :param view_name: Name of the view, used generate the URL.
    :param pyramid: Indicator to use pyramid for URL generation. This should
        be removed as soon as we are fully migrated to pyramid.
    """

    def __init__(self, key, name, view_name, pyramid=False):
        self.key = key
        self.name = name
        self.view_name = view_name
        self.pyramid = pyramid

    def generate_url(self, request):
        if self.pyramid:
            if hasattr(request, 'route_path'):
                return request.route_path(self.view_name)
            else:
                # TODO: johbo: Remove this after migrating to pyramid.
                # We need the pyramid request here to generate URLs to pyramid
                # views from within pylons views.
                from pyramid.threadlocal import get_current_request
                pyramid_request = get_current_request()
                return pyramid_request.route_path(self.view_name)
        else:
            return url(self.view_name)


@implementer(IAdminNavigationRegistry)
class NavigationRegistry(object):

    _base_entries = [
        NavEntry('global', _('Global'), 'admin_settings_global'),
        NavEntry('vcs', _('VCS'), 'admin_settings_vcs'),
        NavEntry('visual', _('Visual'), 'admin_settings_visual'),
        NavEntry('mapping', _('Remap and Rescan'), 'admin_settings_mapping'),
        NavEntry('issuetracker', _('Issue Tracker'),
                 'admin_settings_issuetracker'),
        NavEntry('email', _('Email'), 'admin_settings_email'),
        NavEntry('hooks', _('Hooks'), 'admin_settings_hooks'),
        NavEntry('search', _('Full Text Search'), 'admin_settings_search'),
        NavEntry('integrations', _('Integrations'),
                 'global_integrations_home', pyramid=True),
        NavEntry('system', _('System Info'), 'admin_settings_system'),
        NavEntry('open_source', _('Open Source Licenses'),
                 'admin_settings_open_source', pyramid=True),
        # TODO: marcink: we disable supervisor now until the supervisor stats
        # page is fixed in the nix configuration
        # NavEntry('supervisor', _('Supervisor'), 'admin_settings_supervisor'),
    ]

    _labs_entry = NavEntry('labs', _('Labs'),
                           'admin_settings_labs')

    def __init__(self, labs_active=False):
        self._registered_entries = collections.OrderedDict([
            (item.key, item) for item in self.__class__._base_entries
        ])

        if labs_active:
            self.add_entry(self._labs_entry)

    def add_entry(self, entry):
        self._registered_entries[entry.key] = entry

    def get_navlist(self, request):
        navlist = [NavListEntry(i.key, i.name, i.generate_url(request))
                   for i in self._registered_entries.values()]
        return navlist


def navigation_registry(request):
    """
    Helper that returns the admin navigation registry.
    """
    pyramid_registry = get_registry(request)
    nav_registry = pyramid_registry.queryUtility(IAdminNavigationRegistry)
    return nav_registry


def navigation_list(request):
    """
    Helper that returns the admin navigation as list of NavListEntry objects.
    """
    return navigation_registry(request).get_navlist(request)
