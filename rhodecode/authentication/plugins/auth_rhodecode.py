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
RhodeCode authentication plugin for built in internal auth
"""

import logging

from pylons.i18n.translation import lazy_ugettext as _
from sqlalchemy.ext.hybrid import hybrid_property

from rhodecode.authentication.base import RhodeCodeAuthPluginBase
from rhodecode.authentication.routes import AuthnPluginResourceBase
from rhodecode.lib.utils2 import safe_str
from rhodecode.model.db import User

log = logging.getLogger(__name__)


def plugin_factory(plugin_id, *args, **kwds):
    plugin = RhodeCodeAuthPlugin(plugin_id)
    return plugin


class RhodecodeAuthnResource(AuthnPluginResourceBase):
    pass


class RhodeCodeAuthPlugin(RhodeCodeAuthPluginBase):

    def includeme(self, config):
        config.add_authn_plugin(self)
        config.add_authn_resource(self.get_id(), RhodecodeAuthnResource(self))
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_get',
            request_method='GET',
            route_name='auth_home',
            context=RhodecodeAuthnResource)
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_post',
            request_method='POST',
            route_name='auth_home',
            context=RhodecodeAuthnResource)

    def get_display_name(self):
        return _('Rhodecode')

    @hybrid_property
    def name(self):
        return "rhodecode"

    def user_activation_state(self):
        def_user_perms = User.get_default_user().AuthUser.permissions['global']
        return 'hg.register.auto_activate' in def_user_perms

    def allows_authentication_from(
            self, user, allows_non_existing_user=True,
            allowed_auth_plugins=None, allowed_auth_sources=None):
        """
        Custom method for this auth that doesn't accept non existing users.
        We know that user exists in our database.
        """
        allows_non_existing_user = False
        return super(RhodeCodeAuthPlugin, self).allows_authentication_from(
            user, allows_non_existing_user=allows_non_existing_user)

    def auth(self, userobj, username, password, settings, **kwargs):
        if not userobj:
            log.debug('userobj was:%s skipping' % (userobj, ))
            return None
        if userobj.extern_type != self.name:
            log.warning(
                "userobj:%s extern_type mismatch got:`%s` expected:`%s`" %
                (userobj, userobj.extern_type, self.name))
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

        log.debug("User attributes:%s" % (user_attrs, ))
        if userobj.active:
            from rhodecode.lib import auth
            crypto_backend = auth.crypto_backend()
            password_encoded = safe_str(password)
            password_match, new_hash = crypto_backend.hash_check_with_upgrade(
                password_encoded, userobj.password)

            if password_match and new_hash:
                log.debug('user %s properly authenticated, but '
                          'requires hash change to bcrypt', userobj)
                # if password match, and we use OLD deprecated hash,
                # we should migrate this user hash password to the new hash
                # we store the new returned by hash_check_with_upgrade function
                user_attrs['_hash_migrate'] = new_hash

            if userobj.username == User.DEFAULT_USER and userobj.active:
                log.info(
                    'user %s authenticated correctly as anonymous user', userobj)
                return user_attrs

            elif userobj.username == username and password_match:
                log.info('user %s authenticated correctly', userobj)
                return user_attrs
            log.info("user %s had a bad password when "
                     "authenticating on this plugin", userobj)
            return None
        else:
            log.warning('user %s tried auth but is disabled', userobj)
            return None
