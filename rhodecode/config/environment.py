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
Pylons environment configuration
"""

import os
import logging
import rhodecode
import platform
import re
import io

from mako.lookup import TemplateLookup
from pylons.configuration import PylonsConfig
from pylons.error import handle_mako_error
from pyramid.settings import asbool

# don't remove this import it does magic for celery
from rhodecode.lib import celerypylons  # noqa

import rhodecode.lib.app_globals as app_globals

from rhodecode.config import utils
from rhodecode.config.routing import make_map
from rhodecode.config.jsroutes import generate_jsroutes_content

from rhodecode.lib import helpers
from rhodecode.lib.auth import set_available_permissions
from rhodecode.lib.utils import (
    repo2db_mapper, make_db_config, set_rhodecode_config,
    load_rcextensions)
from rhodecode.lib.utils2 import str2bool, aslist
from rhodecode.lib.vcs import connect_vcs, start_vcs_server
from rhodecode.model.scm import ScmModel

log = logging.getLogger(__name__)

def load_environment(global_conf, app_conf, initial=False,
                     test_env=None, test_index=None):
    """
    Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()


    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = {
        'root': root,
        'controllers': os.path.join(root, 'controllers'),
        'static_files': os.path.join(root, 'public'),
        'templates': [os.path.join(root, 'templates')],
    }

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='rhodecode', paths=paths)

    # store some globals into rhodecode
    rhodecode.CELERY_ENABLED = str2bool(config['app_conf'].get('use_celery'))
    rhodecode.CELERY_EAGER = str2bool(
        config['app_conf'].get('celery.always.eager'))

    config['routes.map'] = make_map(config)

    if asbool(config['debug']):
        jsroutes = config['routes.map'].jsroutes()
        jsroutes_file_content = generate_jsroutes_content(jsroutes)
        jsroutes_file_path = os.path.join(
            paths['static_files'], 'js', 'rhodecode', 'routes.js')

        with io.open(jsroutes_file_path, 'w', encoding='utf-8') as f:
            f.write(jsroutes_file_content)

    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = helpers
    rhodecode.CONFIG = config

    load_rcextensions(root_path=config['here'])

    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'])

    # sets the c attribute access when don't existing attribute are accessed
    config['pylons.strict_tmpl_context'] = True

    # Limit backends to "vcs.backends" from configuration
    backends = config['vcs.backends'] = aslist(
        config.get('vcs.backends', 'hg,git'), sep=',')
    for alias in rhodecode.BACKENDS.keys():
        if alias not in backends:
            del rhodecode.BACKENDS[alias]
    log.info("Enabled backends: %s", backends)

    # initialize vcs client and optionally run the server if enabled
    vcs_server_uri = config.get('vcs.server', '')
    vcs_server_enabled = str2bool(config.get('vcs.server.enable', 'true'))
    start_server = (
        str2bool(config.get('vcs.start_server', 'false')) and
        not int(os.environ.get('RC_VCSSERVER_TEST_DISABLE', '0')))
    if vcs_server_enabled and start_server:
        log.info("Starting vcsserver")
        start_vcs_server(server_and_port=vcs_server_uri,
                         protocol=utils.get_vcs_server_protocol(config),
                         log_level=config['vcs.server.log_level'])

    set_available_permissions(config)
    db_cfg = make_db_config(clear_session=True)

    repos_path = list(db_cfg.items('paths'))[0][1]
    config['base_path'] = repos_path

    config['vcs.hooks.direct_calls'] = _use_direct_hook_calls(config)
    config['vcs.hooks.protocol'] = _get_vcs_hooks_protocol(config)

    # store db config also in main global CONFIG
    set_rhodecode_config(config)

    # configure instance id
    utils.set_instance_id(config)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)

    # store config reference into our module to skip import magic of pylons
    rhodecode.CONFIG.update(config)

    utils.configure_pyro4(config)
    utils.configure_vcs(config)
    if vcs_server_enabled:
        connect_vcs(vcs_server_uri, utils.get_vcs_server_protocol(config))

    import_on_startup = str2bool(config.get('startup.import_repos', False))
    if vcs_server_enabled and import_on_startup:
        repo2db_mapper(ScmModel().repo_scan(repos_path), remove_obsolete=False)
    return config


def _use_direct_hook_calls(config):
    default_direct_hook_calls = 'false'
    direct_hook_calls = str2bool(
        config.get('vcs.hooks.direct_calls', default_direct_hook_calls))
    return direct_hook_calls


def _get_vcs_hooks_protocol(config):
    protocol = config.get('vcs.hooks.protocol', 'pyro4').lower()
    return protocol
