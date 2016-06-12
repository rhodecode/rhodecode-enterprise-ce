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

import colander

from rhodecode.translation import _


class AuthnPluginSettingsSchemaBase(colander.MappingSchema):
    """
    This base schema is intended for use in authentication plugins.
    It adds a few default settings (e.g., "enabled"), so that plugin
    authors don't have to maintain a bunch of boilerplate.
    """
    enabled = colander.SchemaNode(
        colander.Bool(),
        default=False,
        description=_('Enable or disable this authentication plugin.'),
        missing=False,
        title=_('Enabled'),
        widget='bool',
    )
    cache_ttl = colander.SchemaNode(
        colander.Int(),
        default=0,
        description=_('Amount of seconds to cache the authentication '
                      'call for this plugin. Useful for long calls like '
                      'LDAP to improve the responsiveness of the '
                      'authentication system (0 means disabled).'),
        missing=0,
        title=_('Auth Cache TTL'),
        validator=colander.Range(min=0, max=None),
        widget='int',
    )
