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


from rhodecode.admin.navigation import NavigationRegistry
from rhodecode.config.routing import ADMIN_PREFIX
from rhodecode.lib.utils2 import str2bool


def includeme(config):
    settings = config.get_settings()

    # Create admin navigation registry and add it to the pyramid registry.
    labs_active = str2bool(settings.get('labs_settings_active', False))
    navigation_registry = NavigationRegistry(labs_active=labs_active)
    config.registry.registerUtility(navigation_registry)

    config.add_route(
        name='admin_settings_open_source',
        pattern=ADMIN_PREFIX + '/settings/open_source')

    # Scan module for configuration decorators.
    config.scan()
