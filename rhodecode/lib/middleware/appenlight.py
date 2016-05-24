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
middleware to handle appenlight publishing of errors
"""

from appenlight_client import make_appenlight_middleware
from appenlight_client.exceptions import get_current_traceback
from appenlight_client.wsgi import AppenlightWSGIWrapper
from paste.deploy.converters import asbool


def track_exception(environ):
    if 'appenlight.client' not in environ:
        return

    # pass the traceback object to middleware
    environ['appenlight.__traceback'] = get_current_traceback(
        skip=1,
        show_hidden_frames=True,
        ignore_system_exceptions=True)


def track_extra_information(environ, section, value):
    """
    Utility function to attach extra information in case of an error condition.

    It will take care of attaching this information to the right place inside
    of `environ`, so that the appenight client can pick it up.
    """
    environ.setdefault('appenlight.extra', {})
    environ['appenlight.extra'][section] = value


def wrap_in_appenlight_if_enabled(app, config, appenlight_client=None):
    """
    Wraps the given `app` for appenlight support.

    .. important::

       Appenlight expects that the wrapper is executed only once, that's why
       the parameter `appenlight_client` can be used to pass in an already
       existing client instance to avoid that decorators are applied more than
       once.

       This is in use to support our setup of the vcs related middlewares.

    """
    if asbool(config['app_conf'].get('appenlight')):
        app = RemoteTracebackTracker(app)
        if not appenlight_client:
            app = make_appenlight_middleware(app, config)
            appenlight_client = app.appenlight_client
        else:
            app = AppenlightWSGIWrapper(app, appenlight_client)
    return app, appenlight_client


class RemoteTracebackTracker(object):
    """
    Utility middleware which forwards Pyro4 remote traceback information.
    """

    def __init__(self, app):
        self.application = app

    def __call__(self, environ, start_response):
        try:
            return self.application(environ, start_response)
        except Exception as e:
            if hasattr(e, '_pyroTraceback'):
                track_extra_information(
                    environ, 'remote_traceback', ''.join(e._pyroTraceback))
            raise
