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
"""
RhodeCode authentication library for PAM
"""

import colander
import grp
import logging
import pam
import pwd
import re
import socket

from pylons.i18n.translation import lazy_ugettext as _
from sqlalchemy.ext.hybrid import hybrid_property

from rhodecode.authentication.base import RhodeCodeExternalAuthPlugin
from rhodecode.authentication.schema import AuthnPluginSettingsSchemaBase
from rhodecode.authentication.routes import AuthnPluginResourceBase
from rhodecode.lib.colander_utils import strip_whitespace

log = logging.getLogger(__name__)


def plugin_factory(plugin_id, *args, **kwds):
    """
    Factory function that is called during plugin discovery.
    It returns the plugin instance.
    """
    plugin = RhodeCodeAuthPlugin(plugin_id)
    return plugin


class PamAuthnResource(AuthnPluginResourceBase):
    pass


class PamSettingsSchema(AuthnPluginSettingsSchemaBase):
    service = colander.SchemaNode(
        colander.String(),
        default='login',
        description=_('PAM service name to use for authentication.'),
        preparer=strip_whitespace,
        title=_('PAM service name'),
        widget='string')
    gecos = colander.SchemaNode(
        colander.String(),
        default='(?P<last_name>.+),\s*(?P<first_name>\w+)',
        description=_('Regular expression for extracting user name/email etc. '
                      'from Unix userinfo.'),
        preparer=strip_whitespace,
        title=_('Gecos Regex'),
        widget='string')


class RhodeCodeAuthPlugin(RhodeCodeExternalAuthPlugin):
    # PAM authentication can be slow. Repository operations involve a lot of
    # auth calls. Little caching helps speedup push/pull operations significantly
    AUTH_CACHE_TTL = 4

    def includeme(self, config):
        config.add_authn_plugin(self)
        config.add_authn_resource(self.get_id(), PamAuthnResource(self))
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_get',
            request_method='GET',
            route_name='auth_home',
            context=PamAuthnResource)
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_post',
            request_method='POST',
            route_name='auth_home',
            context=PamAuthnResource)

    def get_display_name(self):
        return _('PAM')

    @hybrid_property
    def name(self):
        return "pam"

    def get_settings_schema(self):
        return PamSettingsSchema()

    def use_fake_password(self):
        return True

    def auth(self, userobj, username, password, settings, **kwargs):
        if not username or not password:
            log.debug('Empty username or password skipping...')
            return None

        auth_result = pam.authenticate(username, password, settings["service"])

        if not auth_result:
            log.error("PAM was unable to authenticate user: %s" % (username, ))
            return None

        log.debug('Got PAM response %s' % (auth_result, ))

        # old attrs fetched from RhodeCode database
        default_email = "%s@%s" % (username, socket.gethostname())
        admin = getattr(userobj, 'admin', False)
        active = getattr(userobj, 'active', True)
        email = getattr(userobj, 'email', '') or default_email
        username = getattr(userobj, 'username', username)
        firstname = getattr(userobj, 'firstname', '')
        lastname = getattr(userobj, 'lastname', '')
        extern_type = getattr(userobj, 'extern_type', '')

        user_attrs = {
            'username': username,
            'firstname': firstname,
            'lastname': lastname,
            'groups': [g.gr_name for g in grp.getgrall()
                       if username in g.gr_mem],
            'email': email,
            'admin': admin,
            'active': active,
            'active_from_extern': None,
            'extern_name': username,
            'extern_type': extern_type,
        }

        try:
            user_data = pwd.getpwnam(username)
            regex = settings["gecos"]
            match = re.search(regex, user_data.pw_gecos)
            if match:
                user_attrs["firstname"] = match.group('first_name')
                user_attrs["lastname"] = match.group('last_name')
        except Exception:
            log.warning("Cannot extract additional info for PAM user")
            pass

        log.debug("pamuser: %s", user_attrs)
        log.info('user %s authenticated correctly' % user_attrs['username'])
        return user_attrs
