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
Pylons middleware initialization
"""
import logging

from paste.registry import RegistryManager
from paste.gzipper import make_gzip_middleware
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.static import static_view
from pyramid.settings import asbool, aslist
from pyramid.wsgi import wsgiapp
from routes.middleware import RoutesMiddleware
import routes.util

import rhodecode
from rhodecode.config import patches, utils
from rhodecode.config.environment import load_environment
from rhodecode.lib.middleware import csrf
from rhodecode.lib.middleware.appenlight import wrap_in_appenlight_if_enabled
from rhodecode.lib.middleware.disable_vcs import DisableVCSPagesWrapper
from rhodecode.lib.middleware.https_fixup import HttpsFixup
from rhodecode.lib.middleware.vcs import VCSMiddleware
from rhodecode.lib.plugins.utils import register_rhodecode_plugin


log = logging.getLogger(__name__)


def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether or not this application provides a full WSGI stack (by
        default, meaning it handles its own exceptions and errors).
        Disable full_stack when this application is "managed" by
        another WSGI middleware.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Apply compatibility patches
    patches.kombu_1_5_1_python_2_7_11()
    patches.inspect_getargspec()

    # Configure the Pylons environment
    config = load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp(config=config)
    if rhodecode.is_test:
        app = csrf.CSRFDetector(app)

    expected_origin = config.get('expected_origin')
    if expected_origin:
        # The API can be accessed from other Origins.
        app = csrf.OriginChecker(app, expected_origin,
                                 skip_urls=[routes.util.url_for('api')])

    # Add RoutesMiddleware. Currently we have two instances in the stack. This
    # is the lower one to make the StatusCodeRedirect middleware happy.
    # TODO: johbo: This is not optimal, search for a better solution.
    app = RoutesMiddleware(app, config['routes.map'])

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
    if asbool(config['pdebug']):
        from rhodecode.lib.profiler import ProfilingMiddleware
        app = ProfilingMiddleware(app)

    # Protect from VCS Server error related pages when server is not available
    vcs_server_enabled = asbool(config.get('vcs.server.enable', 'true'))
    if not vcs_server_enabled:
        app = DisableVCSPagesWrapper(app)

    if asbool(full_stack):

        # Appenlight monitoring and error handler
        app, appenlight_client = wrap_in_appenlight_if_enabled(app, config)

        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # we want our low level middleware to get to the request ASAP. We don't
        # need any pylons stack middleware in them
        app = VCSMiddleware(app, config, appenlight_client)
        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # enable https redirects based on HTTP_X_URL_SCHEME set by proxy
    app = HttpsFixup(app, config)

    # Establish the Registry for this application
    app = RegistryManager(app)

    app.config = config

    return app


def make_pyramid_app(global_config, **settings):
    """
    Constructs the WSGI application based on Pyramid and wraps the Pylons based
    application.

    Specials:

    * We migrate from Pylons to Pyramid. While doing this, we keep both
      frameworks functional. This involves moving some WSGI middlewares around
      and providing access to some data internals, so that the old code is
      still functional.

    * The application can also be integrated like a plugin via the call to
      `includeme`. This is accompanied with the other utility functions which
      are called. Changing this should be done with great care to not break
      cases when these fragments are assembled from another place.

    """
    # The edition string should be available in pylons too, so we add it here
    # before copying the settings.
    settings.setdefault('rhodecode.edition', 'Community Edition')

    # As long as our Pylons application does expect "unprepared" settings, make
    # sure that we keep an unmodified copy. This avoids unintentional change of
    # behavior in the old application.
    settings_pylons = settings.copy()

    # Some parts of the code expect a merge of global and app settings.
    settings_merged = global_config.copy()
    settings_merged.update(settings)

    sanitize_settings_and_apply_defaults(settings)
    config = Configurator(settings=settings)
    add_pylons_compat_data(config.registry, global_config, settings_pylons)

    # If this is a test run we prepare the test environment like
    # creating a test database, test search index and test repositories.
    # This has to be done before the database connection is initialized.
    if settings['is_test']:
        utils.initialize_test_environment(settings_merged)

    # Initialize the database connection.
    utils.initialize_database(settings_merged)

    includeme(config)
    includeme_last(config)
    pyramid_app = config.make_wsgi_app()
    pyramid_app = wrap_app_in_wsgi_middlewares(pyramid_app, config)
    return pyramid_app


def add_pylons_compat_data(registry, global_config, settings):
    """
    Attach data to the registry to support the Pylons integration.
    """
    registry._pylons_compat_global_config = global_config
    registry._pylons_compat_settings = settings


def includeme(config):
    settings = config.registry.settings

    # Includes which are required. The application would fail without them.
    config.include('pyramid_mako')
    config.include('pyramid_beaker')
    config.include('rhodecode.authentication')
    config.include('rhodecode.login')
    config.include('rhodecode.tweens')
    config.include('rhodecode.api')

    # Set the authorization policy.
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    # Set the default renderer for HTML templates to mako.
    config.add_mako_renderer('.html')

    # plugin information
    config.registry.rhodecode_plugins = {}

    config.add_directive(
        'register_rhodecode_plugin', register_rhodecode_plugin)
    # include RhodeCode plugins
    includes = aslist(settings.get('rhodecode.includes', []))
    for inc in includes:
        config.include(inc)

    # This is the glue which allows us to migrate in chunks. By registering the
    # pylons based application as the "Not Found" view in Pyramid, we will
    # fallback to the old application each time the new one does not yet know
    # how to handle a request.
    pylons_app = make_app(
        config.registry._pylons_compat_global_config,
        **config.registry._pylons_compat_settings)
    config.registry._pylons_compat_config = pylons_app.config
    pylons_app_as_view = wsgiapp(pylons_app)
    config.add_notfound_view(pylons_app_as_view)


def includeme_last(config):
    """
    The static file catchall needs to be last in the view configuration.
    """
    settings = config.registry.settings

    # Note: johbo: I would prefer to register a prefix for static files at some
    # point, e.g. move them under '_static/'. This would fully avoid that we
    # can have name clashes with a repository name. Imaging someone calling his
    # repo "css" ;-) Also having an external web server to serve out the static
    # files seems to be easier to set up if they have a common prefix.
    #
    # Example: config.add_static_view('_static', path='rhodecode:public')
    #
    # It might be an option to register both paths for a while and then migrate
    # over to the new location.

    # Serving static files with a catchall.
    if settings['static_files']:
        config.add_route('catchall_static', '/*subpath')
        config.add_view(
            static_view('rhodecode:public'), route_name='catchall_static')


def wrap_app_in_wsgi_middlewares(pyramid_app, config):
    """
    Apply outer WSGI middlewares around the application.

    Part of this has been moved up from the Pylons layer, so that the
    data is also available if old Pylons code is hit through an already ported
    view.
    """
    settings = config.registry.settings

    # Add RoutesMiddleware. Currently we have two instances in the stack. This
    # is the upper one to support the pylons compatibility tween during
    # migration to pyramid.
    pyramid_app = RoutesMiddleware(
        pyramid_app, config.registry._pylons_compat_config['routes.map'])

    # TODO: johbo: Don't really see why we enable the gzip middleware when
    # serving static files, might be something that should have its own setting
    # as well?
    if settings['static_files']:
        pyramid_app = make_gzip_middleware(
            pyramid_app, settings, compress_level=1)

    return pyramid_app


def sanitize_settings_and_apply_defaults(settings):
    """
    Applies settings defaults and does all type conversion.

    We would move all settings parsing and preparation into this place, so that
    we have only one place left which deals with this part. The remaining parts
    of the application would start to rely fully on well prepared settings.

    This piece would later be split up per topic to avoid a big fat monster
    function.
    """

    # Pyramid's mako renderer has to search in the templates folder so that the
    # old templates still work. Ported and new templates are expected to use
    # real asset specifications for the includes.
    mako_directories = settings.setdefault('mako.directories', [
        # Base templates of the original Pylons application
        'rhodecode:templates',
    ])
    log.debug(
        "Using the following Mako template directories: %s",
        mako_directories)

    # Default includes, possible to change as a user
    pyramid_includes = settings.setdefault('pyramid.includes', [
        'rhodecode.lib.middleware.request_wrapper',
    ])
    log.debug(
        "Using the following pyramid.includes: %s",
        pyramid_includes)

    # TODO: johbo: Re-think this, usually the call to config.include
    # should allow to pass in a prefix.
    settings.setdefault('rhodecode.api.url', '/_admin/api')

    _bool_setting(settings, 'vcs.server.enable', 'true')
    _bool_setting(settings, 'static_files', 'true')

    return settings


def _bool_setting(settings, name, default):
    settings[name] = asbool(settings.get(name, default))
