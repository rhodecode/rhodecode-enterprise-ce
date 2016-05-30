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
import logging

from sqlalchemy.ext.hybrid import hybrid_property

from rhodecode.authentication.base import RhodeCodeExternalAuthPlugin
from rhodecode.authentication.schema import AuthnPluginSettingsSchemaBase
from rhodecode.authentication.routes import AuthnPluginResourceBase
from rhodecode.lib.colander_utils import strip_whitespace
from rhodecode.lib.utils2 import str2bool, safe_unicode
from rhodecode.model.db import User
from rhodecode.translation import _


log = logging.getLogger(__name__)


def plugin_factory(plugin_id, *args, **kwds):
    """
    Factory function that is called during plugin discovery.
    It returns the plugin instance.
    """
    plugin = RhodeCodeAuthPlugin(plugin_id)
    return plugin


class HeadersAuthnResource(AuthnPluginResourceBase):
    pass


class HeadersSettingsSchema(AuthnPluginSettingsSchemaBase):
    header = colander.SchemaNode(
        colander.String(),
        default='REMOTE_USER',
        description=_('Header to extract the user from'),
        preparer=strip_whitespace,
        title=_('Header'),
        widget='string')
    fallback_header = colander.SchemaNode(
        colander.String(),
        default='HTTP_X_FORWARDED_USER',
        description=_('Header to extract the user from when main one fails'),
        preparer=strip_whitespace,
        title=_('Fallback header'),
        widget='string')
    clean_username = colander.SchemaNode(
        colander.Boolean(),
        default=True,
        description=_('Perform cleaning of user, if passed user has @ in '
                      'username then first part before @ is taken. '
                      'If there\'s \\ in the username only the part after '
                      ' \\ is taken'),
        missing=False,
        title=_('Clean username'),
        widget='bool')


class RhodeCodeAuthPlugin(RhodeCodeExternalAuthPlugin):

    def includeme(self, config):
        config.add_authn_plugin(self)
        config.add_authn_resource(self.get_id(), HeadersAuthnResource(self))
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_get',
            request_method='GET',
            route_name='auth_home',
            context=HeadersAuthnResource)
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_post',
            request_method='POST',
            route_name='auth_home',
            context=HeadersAuthnResource)

    def get_display_name(self):
        return _('Headers')

    def get_settings_schema(self):
        return HeadersSettingsSchema()

    @hybrid_property
    def name(self):
        return 'headers'

    @hybrid_property
    def is_container_auth(self):
        return True

    def use_fake_password(self):
        return True

    def user_activation_state(self):
        def_user_perms = User.get_default_user().AuthUser.permissions['global']
        return 'hg.extern_activate.auto' in def_user_perms

    def _clean_username(self, username):
        # Removing realm and domain from username
        username = username.split('@')[0]
        username = username.rsplit('\\')[-1]
        return username

    def _get_username(self, environ, settings):
        username = None
        environ = environ or {}
        if not environ:
            log.debug('got empty environ: %s' % environ)

        settings = settings or {}
        if settings.get('header'):
            header = settings.get('header')
            username = environ.get(header)
            log.debug('extracted %s:%s' % (header, username))

        # fallback mode
        if not username and settings.get('fallback_header'):
            header = settings.get('fallback_header')
            username = environ.get(header)
            log.debug('extracted %s:%s' % (header, username))

        if username and str2bool(settings.get('clean_username')):
            log.debug('Received username `%s` from headers' % username)
            username = self._clean_username(username)
            log.debug('New cleanup user is:%s' % username)
        return username

    def get_user(self, username=None, **kwargs):
        """
        Helper method for user fetching in plugins, by default it's using
        simple fetch by username, but this method can be custimized in plugins
        eg. headers auth plugin to fetch user by environ params
        :param username: username if given to fetch
        :param kwargs: extra arguments needed for user fetching.
        """
        environ = kwargs.get('environ') or {}
        settings = kwargs.get('settings') or {}
        username = self._get_username(environ, settings)
        # we got the username, so use default method now
        return super(RhodeCodeAuthPlugin, self).get_user(username)

    def auth(self, userobj, username, password, settings, **kwargs):
        """
        Get's the headers_auth username (or email). It tries to get username
        from REMOTE_USER if this plugin is enabled, if that fails
        it tries to get username from HTTP_X_FORWARDED_USER if fallback header
        is set. clean_username extracts the username from this data if it's
        having @ in it.
        Return None on failure. On success, return a dictionary of the form:

            see: RhodeCodeAuthPluginBase.auth_func_attrs

        :param userobj:
        :param username:
        :param password:
        :param settings:
        :param kwargs:
        """
        environ = kwargs.get('environ')
        if not environ:
            log.debug('Empty environ data skipping...')
            return None

        if not userobj:
            userobj = self.get_user('', environ=environ, settings=settings)

        # we don't care passed username/password for headers auth plugins.
        # only way to log in is using environ
        username = None
        if userobj:
            username = getattr(userobj, 'username')

        if not username:
            # we don't have any objects in DB user doesn't exist extrac username
            # from environ based on the settings
            username = self._get_username(environ, settings)

        # if cannot fetch username, it's a no-go for this plugin to proceed
        if not username:
            return None

        # old attrs fetched from RhodeCode database
        admin = getattr(userobj, 'admin', False)
        active = getattr(userobj, 'active', True)
        email = getattr(userobj, 'email', '')
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

        log.info('user `%s` authenticated correctly' % user_attrs['username'])
        return user_attrs
