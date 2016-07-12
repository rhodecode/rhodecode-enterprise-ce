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

"""
RhodeCode authentication token plugin for built in internal auth
"""

import logging

from sqlalchemy.ext.hybrid import hybrid_property

from rhodecode.translation import _
from rhodecode.authentication.base import RhodeCodeAuthPluginBase, VCS_TYPE
from rhodecode.authentication.routes import AuthnPluginResourceBase
from rhodecode.model.db import User, UserApiKeys


log = logging.getLogger(__name__)


def plugin_factory(plugin_id, *args, **kwds):
    plugin = RhodeCodeAuthPlugin(plugin_id)
    return plugin


class RhodecodeAuthnResource(AuthnPluginResourceBase):
    pass


class RhodeCodeAuthPlugin(RhodeCodeAuthPluginBase):
    """
    Enables usage of authentication tokens for vcs operations.
    """

    def includeme(self, config):
        config.add_authn_plugin(self)
        config.add_authn_resource(self.get_id(), RhodecodeAuthnResource(self))
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_get',
            renderer='rhodecode:templates/admin/auth/plugin_settings.html',
            request_method='GET',
            route_name='auth_home',
            context=RhodecodeAuthnResource)
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_post',
            renderer='rhodecode:templates/admin/auth/plugin_settings.html',
            request_method='POST',
            route_name='auth_home',
            context=RhodecodeAuthnResource)

    def get_display_name(self):
        return _('Rhodecode Token Auth')

    @hybrid_property
    def name(self):
        return "authtoken"

    def user_activation_state(self):
        def_user_perms = User.get_default_user().AuthUser.permissions['global']
        return 'hg.register.auto_activate' in def_user_perms

    def allows_authentication_from(
            self, user, allows_non_existing_user=True,
            allowed_auth_plugins=None, allowed_auth_sources=None):
        """
        Custom method for this auth that doesn't accept empty users. And also
        allows users from all other active plugins to use it and also
        authenticate against it. But only via vcs mode
        """
        from rhodecode.authentication.base import get_authn_registry
        authn_registry = get_authn_registry()

        active_plugins = set(
            [x.name for x in authn_registry.get_plugins_for_authentication()])
        active_plugins.discard(self.name)

        allowed_auth_plugins = [self.name] + list(active_plugins)
        # only for vcs operations
        allowed_auth_sources = [VCS_TYPE]

        return super(RhodeCodeAuthPlugin, self).allows_authentication_from(
            user, allows_non_existing_user=False,
            allowed_auth_plugins=allowed_auth_plugins,
            allowed_auth_sources=allowed_auth_sources)

    def auth(self, userobj, username, password, settings, **kwargs):
        if not userobj:
            log.debug('userobj was:%s skipping' % (userobj, ))
            return None

        user_attrs = {
            "username": userobj.username,
            "firstname": userobj.firstname,
            "lastname": userobj.lastname,
            "groups": [],
            "email": userobj.email,
            "admin": userobj.admin,
            "active": userobj.active,
            "active_from_extern": userobj.active,
            "extern_name": userobj.user_id,
            "extern_type": userobj.extern_type,
        }

        log.debug('Authenticating user with args %s', user_attrs)
        if userobj.active:
            role = UserApiKeys.ROLE_VCS
            active_tokens = [x.api_key for x in
                             User.extra_valid_auth_tokens(userobj, role=role)]
            if userobj.username == username and password in active_tokens:
                log.info(
                    'user `%s` successfully authenticated via %s',
                    user_attrs['username'], self.name)
                return user_attrs
            log.error(
                'user `%s` failed to authenticate via %s, reason: bad or '
                'inactive token.', username, self.name)
        else:
            log.warning(
                'user `%s` failed to authenticate via %s, reason: account not '
                'active.', username, self.name)
        return None
