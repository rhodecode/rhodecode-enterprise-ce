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
RhodeCode authentication plugin for Jasig CAS
http://www.jasig.org/cas
"""


import colander
import logging
import rhodecode
import urllib
import urllib2

from pylons.i18n.translation import lazy_ugettext as _
from sqlalchemy.ext.hybrid import hybrid_property

from rhodecode.authentication.base import RhodeCodeExternalAuthPlugin
from rhodecode.authentication.schema import AuthnPluginSettingsSchemaBase
from rhodecode.authentication.routes import AuthnPluginResourceBase
from rhodecode.lib.colander_utils import strip_whitespace
from rhodecode.lib.utils2 import safe_unicode
from rhodecode.model.db import User

log = logging.getLogger(__name__)


def plugin_factory(plugin_id, *args, **kwds):
    """
    Factory function that is called during plugin discovery.
    It returns the plugin instance.
    """
    plugin = RhodeCodeAuthPlugin(plugin_id)
    return plugin


class JasigCasAuthnResource(AuthnPluginResourceBase):
    pass


class JasigCasSettingsSchema(AuthnPluginSettingsSchemaBase):
    service_url = colander.SchemaNode(
        colander.String(),
        default='https://domain.com/cas/v1/tickets',
        description=_('The url of the Jasig CAS REST service'),
        preparer=strip_whitespace,
        title=_('URL'),
        widget='string')


class RhodeCodeAuthPlugin(RhodeCodeExternalAuthPlugin):

    def includeme(self, config):
        config.add_authn_plugin(self)
        config.add_authn_resource(self.get_id(), JasigCasAuthnResource(self))
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_get',
            renderer='rhodecode:templates/admin/auth/plugin_settings.html',
            request_method='GET',
            route_name='auth_home',
            context=JasigCasAuthnResource)
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_post',
            renderer='rhodecode:templates/admin/auth/plugin_settings.html',
            request_method='POST',
            route_name='auth_home',
            context=JasigCasAuthnResource)

    def get_settings_schema(self):
        return JasigCasSettingsSchema()

    def get_display_name(self):
        return _('Jasig-CAS')

    @hybrid_property
    def name(self):
        return "jasig-cas"

    @hybrid_property
    def is_container_auth(self):
        return True

    def use_fake_password(self):
        return True

    def user_activation_state(self):
        def_user_perms = User.get_default_user().AuthUser.permissions['global']
        return 'hg.extern_activate.auto' in def_user_perms

    def auth(self, userobj, username, password, settings, **kwargs):
        """
        Given a user object (which may be null), username, a plaintext password,
        and a settings object (containing all the keys needed as listed in settings()),
        authenticate this user's login attempt.

        Return None on failure. On success, return a dictionary of the form:

            see: RhodeCodeAuthPluginBase.auth_func_attrs
        This is later validated for correctness
        """
        if not username or not password:
            log.debug('Empty username or password skipping...')
            return None

        log.debug("Jasig CAS settings: %s", settings)
        params = urllib.urlencode({'username': username, 'password': password})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "User-Agent": "RhodeCode-auth-%s" % rhodecode.__version__}
        url = settings["service_url"]

        log.debug("Sent Jasig CAS: \n%s",
                  {"url": url, "body": params, "headers": headers})
        request = urllib2.Request(url, params, headers)
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            log.debug("HTTPError when requesting Jasig CAS (status code: %d)" % e.code)
            return None
        except urllib2.URLError as e:
            log.debug("URLError when requesting Jasig CAS url: %s " % url)
            return None

        # old attrs fetched from RhodeCode database
        admin = getattr(userobj, 'admin', False)
        active = getattr(userobj, 'active', True)
        email = getattr(userobj, 'email', '')
        username = getattr(userobj, 'username', username)
        firstname = getattr(userobj, 'firstname', '')
        lastname = getattr(userobj, 'lastname', '')
        extern_type = getattr(userobj, 'extern_type', '')

        user_attrs = {
            'username': username,
            'firstname': safe_unicode(firstname or username),
            'lastname': safe_unicode(lastname or ''),
            'groups': [],
            'email': email or '',
            'admin': admin or False,
            'active': active,
            'active_from_extern': True,
            'extern_name': username,
            'extern_type': extern_type,
        }

        log.info('user %s authenticated correctly' % user_attrs['username'])
        return user_attrs
