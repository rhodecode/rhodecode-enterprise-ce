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


import logging
import pylons
import rhodecode

from pylons.i18n.translation import _get_translator
from pylons.util import ContextObj
from routes.util import URLGenerator

from rhodecode.lib.base import attach_context_attributes, get_auth_user
from rhodecode.model import meta

log = logging.getLogger(__name__)


def pylons_compatibility_tween_factory(handler, registry):
    def pylons_compatibility_tween(request):
        """
        While migrating from pylons to pyramid we need to call some pylons code
        from pyramid. For example while rendering an old template that uses the
        'c' or 'h' objects. This tween sets up the needed pylons globals.
        """
        try:
            config = rhodecode.CONFIG
            environ = request.environ
            session = request.session
            session_key = (config['pylons.environ_config']
                           .get('session', 'beaker.session'))

            # Setup pylons globals.
            pylons.config._push_object(config)
            pylons.request._push_object(request)
            pylons.session._push_object(session)
            environ[session_key] = session
            pylons.url._push_object(URLGenerator(config['routes.map'],
                                                 environ))

            # TODO: Maybe we should use the language from pyramid.
            translator = _get_translator(config.get('lang'))
            pylons.translator._push_object(translator)

            # Get the rhodecode auth user object and make it available.
            auth_user = get_auth_user(environ)
            request.user = auth_user
            environ['rc_auth_user'] = auth_user

            # Setup the pylons context object ('c')
            context = ContextObj()
            context.rhodecode_user = auth_user
            attach_context_attributes(context)
            pylons.tmpl_context._push_object(context)

            return handler(request)
        finally:
            # Dispose current database session and rollback uncommitted
            # transactions.
            meta.Session.remove()

    return pylons_compatibility_tween


def includeme(config):
    config.add_subscriber('rhodecode.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('rhodecode.subscribers.add_localizer',
                          'pyramid.events.NewRequest')
    config.add_tween('rhodecode.tweens.pylons_compatibility_tween_factory')
