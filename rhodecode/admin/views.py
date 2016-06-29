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

import collections
import logging

from pylons import tmpl_context as c
from pyramid.view import view_config

from rhodecode.lib.auth import LoginRequired, HasPermissionAllDecorator
from rhodecode.lib.utils import read_opensource_licenses

from .navigation import navigation_list


log = logging.getLogger(__name__)


class AdminSettingsView(object):

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.session = request.session
        self._rhodecode_user = request.user

    @LoginRequired()
    @HasPermissionAllDecorator('hg.admin')
    @view_config(
        route_name='admin_settings_open_source', request_method='GET',
        renderer='rhodecode:templates/admin/settings/settings.html')
    def open_source_licenses(self):
        c.active = 'open_source'
        c.navlist = navigation_list(self.request)
        c.opensource_licenses = collections.OrderedDict(
            sorted(read_opensource_licenses().items(), key=lambda t: t[0]))

        return {}
