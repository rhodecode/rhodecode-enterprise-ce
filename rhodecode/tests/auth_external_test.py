# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
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
External module for testing plugins

rhodecode.tests.auth_external_test

"""
import logging
import traceback

from rhodecode.authentication.base import RhodeCodeExternalAuthPlugin
from sqlalchemy.ext.hybrid import hybrid_property
from rhodecode.model.db import User
from rhodecode.lib.ext_json import formatted_json

log = logging.getLogger(__name__)


class RhodeCodeAuthPlugin(RhodeCodeExternalAuthPlugin):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @hybrid_property
    def allows_creating_users(self):
        return True

    @hybrid_property
    def name(self):
        return "external_test"

    def settings(self):
        settings = [
        ]
        return settings

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

        try:
            user_dn = username

            # # old attrs fetched from RhodeCode database
            admin = getattr(userobj, 'admin', False)
            active = getattr(userobj, 'active', True)
            email = getattr(userobj, 'email', '')
            firstname = getattr(userobj, 'firstname', '')
            lastname = getattr(userobj, 'lastname', '')
            extern_type = getattr(userobj, 'extern_type', '')
            #
            user_attrs = {
                'username': username,
                'firstname': firstname,
                'lastname': lastname,
                'groups': [],
                'email': '%s@rhodecode.com' % username,
                'admin': admin,
                'active': active,
                "active_from_extern": None,
                'extern_name': user_dn,
                'extern_type': extern_type,
            }

            log.debug('EXTERNAL user: \n%s' % formatted_json(user_attrs))
            log.info('user %s authenticated correctly' % user_attrs['username'])

            return user_attrs

        except (Exception,):
            log.error(traceback.format_exc())
            return None
