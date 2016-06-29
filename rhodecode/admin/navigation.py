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
from pylons.i18n.translation import lazy_ugettext
from zope.interface import implementer

import rhodecode
from rhodecode.admin.interfaces import IAdminNavigationRegistry
from rhodecode.lib.utils2 import str2bool


log = logging.getLogger(__name__)

NavListEntry = collections.namedtuple('NavListEntry', ['key', 'name', 'url'])


class NavEntry(object):

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
        NavEntry('global', lazy_ugettext('Global'), 'admin_settings_global'),
        NavEntry('vcs', lazy_ugettext('VCS'), 'admin_settings_vcs'),
        NavEntry('visual', lazy_ugettext('Visual'), 'admin_settings_visual'),
        NavEntry('mapping', lazy_ugettext('Remap and Rescan'),
                 'admin_settings_mapping'),
        NavEntry('issuetracker', lazy_ugettext('Issue Tracker'),
                 'admin_settings_issuetracker'),
        NavEntry('email', lazy_ugettext('Email'), 'admin_settings_email'),
        NavEntry('hooks', lazy_ugettext('Hooks'), 'admin_settings_hooks'),
        NavEntry('search', lazy_ugettext('Full Text Search'),
                 'admin_settings_search'),
        NavEntry('system', lazy_ugettext('System Info'),
                 'admin_settings_system'),
        NavEntry('open_source', lazy_ugettext('Open Source Licenses'),
                 'admin_settings_open_source', pyramid=True),
        # TODO: marcink: we disable supervisor now until the supervisor stats
        # page is fixed in the nix configuration
        # NavEntry('supervisor', lazy_ugettext('Supervisor'),
        #          'admin_settings_supervisor'),
    ]

    def __init__(self):
        self._registered_entries = collections.OrderedDict([
            (item.key, item) for item in self.__class__._base_entries
        ])

        # Add the labs entry when it's activated.
        labs_active = str2bool(
            rhodecode.CONFIG.get('labs_settings_active', 'false'))
        if labs_active:
            self.add_entry(
                NavEntry('labs', lazy_ugettext('Labs'), 'admin_settings_labs'))

    def add_entry(self, entry):
        self._registered_entries[entry.key] = entry

    def get_navlist(self, request):
        navlist = [NavListEntry(i.key, i.name, i.generate_url(request))
                   for i in self._registered_entries.values()]
        return navlist

navigation = NavigationRegistry()
