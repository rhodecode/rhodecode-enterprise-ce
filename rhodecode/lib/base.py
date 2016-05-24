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
The base Controller API
Provides the BaseController class for subclassing. And usage in different
controllers
"""

import logging
import socket

import ipaddress

from paste.auth.basic import AuthBasicAuthenticator
from paste.httpexceptions import HTTPUnauthorized, HTTPForbidden, get_exception
from paste.httpheaders import WWW_AUTHENTICATE, AUTHORIZATION
from pylons import config, tmpl_context as c, request, session, url
from pylons.controllers import WSGIController
from pylons.controllers.util import redirect
from pylons.i18n import translation
# marcink: don't remove this import
from pylons.templating import render_mako as render  # noqa
from pylons.i18n.translation import _
from webob.exc import HTTPFound


import rhodecode
from rhodecode.authentication.base import VCS_TYPE
from rhodecode.lib import auth, utils2
from rhodecode.lib import helpers as h
from rhodecode.lib.auth import AuthUser, CookieStoreWrapper
from rhodecode.lib.exceptions import UserCreationError
from rhodecode.lib.utils import (
    get_repo_slug, set_rhodecode_config, password_changed,
    get_enabled_hook_classes)
from rhodecode.lib.utils2 import (
    str2bool, safe_unicode, AttributeDict, safe_int, md5, aslist)
from rhodecode.lib.vcs.exceptions import RepositoryRequirementError
from rhodecode.model import meta
from rhodecode.model.db import Repository, User
from rhodecode.model.notification import NotificationModel
from rhodecode.model.scm import ScmModel
from rhodecode.model.settings import VcsSettingsModel, SettingsModel


log = logging.getLogger(__name__)


def _filter_proxy(ip):
    """
    Passed in IP addresses in HEADERS can be in a special format of multiple
    ips. Those comma separated IPs are passed from various proxies in the
    chain of request processing. The left-most being the original client.
    We only care about the first IP which came from the org. client.

    :param ip: ip string from headers
    """
    if ',' in ip:
        _ips = ip.split(',')
        _first_ip = _ips[0].strip()
        log.debug('Got multiple IPs %s, using %s', ','.join(_ips), _first_ip)
        return _first_ip
    return ip


def _filter_port(ip):
    """
    Removes a port from ip, there are 4 main cases to handle here.
    - ipv4 eg. 127.0.0.1
    - ipv6 eg. ::1
    - ipv4+port eg. 127.0.0.1:8080
    - ipv6+port eg. [::1]:8080

    :param ip:
    """
    def is_ipv6(ip_addr):
        if hasattr(socket, 'inet_pton'):
            try:
                socket.inet_pton(socket.AF_INET6, ip_addr)
            except socket.error:
                return False
        else:
            # fallback to ipaddress
            try:
                ipaddress.IPv6Address(ip_addr)
            except Exception:
                return False
        return True

    if ':' not in ip:  # must be ipv4 pure ip
        return ip

    if '[' in ip and ']' in ip:  # ipv6 with port
        return ip.split(']')[0][1:].lower()

    # must be ipv6 or ipv4 with port
    if is_ipv6(ip):
        return ip
    else:
        ip, _port = ip.split(':')[:2]  # means ipv4+port
        return ip


def get_ip_addr(environ):
    proxy_key = 'HTTP_X_REAL_IP'
    proxy_key2 = 'HTTP_X_FORWARDED_FOR'
    def_key = 'REMOTE_ADDR'
    _filters = lambda x: _filter_port(_filter_proxy(x))

    ip = environ.get(proxy_key)
    if ip:
        return _filters(ip)

    ip = environ.get(proxy_key2)
    if ip:
        return _filters(ip)

    ip = environ.get(def_key, '0.0.0.0')
    return _filters(ip)


def get_server_ip_addr(environ, log_errors=True):
    hostname = environ.get('SERVER_NAME')
    try:
        return socket.gethostbyname(hostname)
    except Exception as e:
        if log_errors:
            # in some cases this lookup is not possible, and we don't want to
            # make it an exception in logs
            log.exception('Could not retrieve server ip address: %s', e)
        return hostname


def get_server_port(environ):
    return environ.get('SERVER_PORT')


def get_access_path(environ):
    path = environ.get('PATH_INFO')
    org_req = environ.get('pylons.original_request')
    if org_req:
        path = org_req.environ.get('PATH_INFO')
    return path


def vcs_operation_context(
        environ, repo_name, username, action, scm, check_locking=True):
    """
    Generate the context for a vcs operation, e.g. push or pull.

    This context is passed over the layers so that hooks triggered by the
    vcs operation know details like the user, the user's IP address etc.

    :param check_locking: Allows to switch of the computation of the locking
        data. This serves mainly the need of the simplevcs middleware to be
        able to disable this for certain operations.

    """
    # Tri-state value: False: unlock, None: nothing, True: lock
    make_lock = None
    locked_by = [None, None, None]
    is_anonymous = username == User.DEFAULT_USER
    if not is_anonymous and check_locking:
        log.debug('Checking locking on repository "%s"', repo_name)
        user = User.get_by_username(username)
        repo = Repository.get_by_repo_name(repo_name)
        make_lock, __, locked_by = repo.get_locking_state(
            action, user.user_id)

    settings_model = VcsSettingsModel(repo=repo_name)
    ui_settings = settings_model.get_ui_settings()

    extras = {
        'ip': get_ip_addr(environ),
        'username': username,
        'action': action,
        'repository': repo_name,
        'scm': scm,
        'config': rhodecode.CONFIG['__file__'],
        'make_lock': make_lock,
        'locked_by': locked_by,
        'server_url': utils2.get_server_url(environ),
        'hooks': get_enabled_hook_classes(ui_settings),
    }
    return extras


class BasicAuth(AuthBasicAuthenticator):

    def __init__(self, realm, authfunc, auth_http_code=None,
                 initial_call_detection=False):
        self.realm = realm
        self.initial_call = initial_call_detection
        self.authfunc = authfunc
        self._rc_auth_http_code = auth_http_code

    def _get_response_from_code(self, http_code):
        try:
            return get_exception(safe_int(http_code))
        except Exception:
            log.exception('Failed to fetch response for code %s' % http_code)
            return HTTPForbidden

    def build_authentication(self):
        head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
        if self._rc_auth_http_code and not self.initial_call:
            # return alternative HTTP code if alternative http return code
            # is specified in RhodeCode config, but ONLY if it's not the
            # FIRST call
            custom_response_klass = self._get_response_from_code(
                self._rc_auth_http_code)
            return custom_response_klass(headers=head)
        return HTTPUnauthorized(headers=head)

    def authenticate(self, environ):
        authorization = AUTHORIZATION(environ)
        if not authorization:
            return self.build_authentication()
        (authmeth, auth) = authorization.split(' ', 1)
        if 'basic' != authmeth.lower():
            return self.build_authentication()
        auth = auth.strip().decode('base64')
        _parts = auth.split(':', 1)
        if len(_parts) == 2:
            username, password = _parts
            if self.authfunc(
                    username, password, environ, VCS_TYPE):
                return username
            if username and password:
                # we mark that we actually executed authentication once, at
                # that point we can use the alternative auth code
                self.initial_call = False

        return self.build_authentication()

    __call__ = authenticate


def attach_context_attributes(context):
    rc_config = SettingsModel().get_all_settings()

    context.rhodecode_version = rhodecode.__version__
    context.rhodecode_edition = config.get('rhodecode.edition')
    # unique secret + version does not leak the version but keep consistency
    context.rhodecode_version_hash = md5(
        config.get('beaker.session.secret', '') +
        rhodecode.__version__)[:8]

    # Default language set for the incoming request
    context.language = translation.get_lang()[0]

    # Visual options
    context.visual = AttributeDict({})

    # DB store
    context.visual.show_public_icon = str2bool(
        rc_config.get('rhodecode_show_public_icon'))
    context.visual.show_private_icon = str2bool(
        rc_config.get('rhodecode_show_private_icon'))
    context.visual.stylify_metatags = str2bool(
        rc_config.get('rhodecode_stylify_metatags'))
    context.visual.dashboard_items = safe_int(
        rc_config.get('rhodecode_dashboard_items', 100))
    context.visual.admin_grid_items = safe_int(
        rc_config.get('rhodecode_admin_grid_items', 100))
    context.visual.repository_fields = str2bool(
        rc_config.get('rhodecode_repository_fields'))
    context.visual.show_version = str2bool(
        rc_config.get('rhodecode_show_version'))
    context.visual.use_gravatar = str2bool(
        rc_config.get('rhodecode_use_gravatar'))
    context.visual.gravatar_url = rc_config.get('rhodecode_gravatar_url')
    context.visual.default_renderer = rc_config.get(
        'rhodecode_markup_renderer', 'rst')
    context.visual.rhodecode_support_url = \
        rc_config.get('rhodecode_support_url') or url('rhodecode_support')

    context.pre_code = rc_config.get('rhodecode_pre_code')
    context.post_code = rc_config.get('rhodecode_post_code')
    context.rhodecode_name = rc_config.get('rhodecode_title')
    context.default_encodings = aslist(config.get('default_encoding'), sep=',')
    # if we have specified default_encoding in the request, it has more
    # priority
    if request.GET.get('default_encoding'):
        context.default_encodings.insert(0, request.GET.get('default_encoding'))
    context.clone_uri_tmpl = rc_config.get('rhodecode_clone_uri_tmpl')

    # INI stored
    context.labs_active = str2bool(
        config.get('labs_settings_active', 'false'))
    context.visual.allow_repo_location_change = str2bool(
        config.get('allow_repo_location_change', True))
    context.visual.allow_custom_hooks_settings = str2bool(
        config.get('allow_custom_hooks_settings', True))
    context.debug_style = str2bool(config.get('debug_style', False))

    context.rhodecode_instanceid = config.get('instance_id')

    # AppEnlight
    context.appenlight_enabled = str2bool(config.get('appenlight', 'false'))
    context.appenlight_api_public_key = config.get(
        'appenlight.api_public_key', '')
    context.appenlight_server_url = config.get('appenlight.server_url', '')

    # END CONFIG VARS

    # TODO: This dosn't work when called from pylons compatibility tween.
    # Fix this and remove it from base controller.
    # context.repo_name = get_repo_slug(request)  # can be empty

    context.csrf_token = auth.get_csrf_token()
    context.backends = rhodecode.BACKENDS.keys()
    context.backends.sort()
    context.unread_notifications = NotificationModel().get_unread_cnt_for_user(
        context.rhodecode_user.user_id)


def get_auth_user(environ):
    ip_addr = get_ip_addr(environ)
    # make sure that we update permissions each time we call controller
    _auth_token = (request.GET.get('auth_token', '') or
                   request.GET.get('api_key', ''))

    if _auth_token:
        # when using API_KEY we are sure user exists.
        auth_user = AuthUser(api_key=_auth_token, ip_addr=ip_addr)
        authenticated = False
    else:
        cookie_store = CookieStoreWrapper(session.get('rhodecode_user'))
        try:
            auth_user = AuthUser(user_id=cookie_store.get('user_id', None),
                                 ip_addr=ip_addr)
        except UserCreationError as e:
            h.flash(e, 'error')
            # container auth or other auth functions that create users
            # on the fly can throw this exception signaling that there's
            # issue with user creation, explanation should be provided
            # in Exception itself. We then create a simple blank
            # AuthUser
            auth_user = AuthUser(ip_addr=ip_addr)

        if password_changed(auth_user, session):
            session.invalidate()
            cookie_store = CookieStoreWrapper(
                session.get('rhodecode_user'))
            auth_user = AuthUser(ip_addr=ip_addr)

        authenticated = cookie_store.get('is_authenticated')

    if not auth_user.is_authenticated and auth_user.is_user_object:
        # user is not authenticated and not empty
        auth_user.set_authenticated(authenticated)

    return auth_user


class BaseController(WSGIController):

    def __before__(self):
        """
        __before__ is called before controller methods and after __call__
        """
        # on each call propagate settings calls into global settings.
        set_rhodecode_config(config)
        attach_context_attributes(c)

        # TODO: Remove this when fixed in attach_context_attributes()
        c.repo_name = get_repo_slug(request)  # can be empty

        self.cut_off_limit_diff = safe_int(config.get('cut_off_limit_diff'))
        self.cut_off_limit_file = safe_int(config.get('cut_off_limit_file'))
        self.sa = meta.Session
        self.scm_model = ScmModel(self.sa)

        default_lang = c.language
        user_lang = c.language
        try:
            user_obj = self._rhodecode_user.get_instance()
            if user_obj:
                user_lang = user_obj.user_data.get('language')
        except Exception:
            log.exception('Failed to fetch user language for user %s',
                          self._rhodecode_user)

        if user_lang and user_lang != default_lang:
            log.debug('set language to %s for user %s', user_lang,
                      self._rhodecode_user)
            translation.set_lang(user_lang)

    def _dispatch_redirect(self, with_url, environ, start_response):
        resp = HTTPFound(with_url)
        environ['SCRIPT_NAME'] = ''  # handle prefix middleware
        environ['PATH_INFO'] = with_url
        return resp(environ, start_response)

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        from rhodecode.lib import helpers as h

        # Provide the Pylons context to Pyramid's debugtoolbar if it asks
        if environ.get('debugtoolbar.wants_pylons_context', False):
            environ['debugtoolbar.pylons_context'] = c._current_obj()

        _route_name = '.'.join([environ['pylons.routes_dict']['controller'],
                                environ['pylons.routes_dict']['action']])

        self.rc_config = SettingsModel().get_all_settings()
        self.ip_addr = get_ip_addr(environ)

        # The rhodecode auth user is looked up and passed through the
        # environ by the pylons compatibility tween in pyramid.
        # So we can just grab it from there.
        auth_user = environ['rc_auth_user']

        # set globals for auth user
        request.user = auth_user
        c.rhodecode_user = self._rhodecode_user = auth_user

        log.info('IP: %s User: %s accessed %s [%s]' % (
            self.ip_addr, auth_user, safe_unicode(get_access_path(environ)),
            _route_name)
        )

        # TODO: Maybe this should be move to pyramid to cover all views.
        # check user attributes for password change flag
        user_obj = auth_user.get_instance()
        if user_obj and user_obj.user_data.get('force_password_change'):
            h.flash('You are required to change your password', 'warning',
                    ignore_duplicate=True)

            skip_user_check_urls = [
                'error.document', 'login.logout', 'login.index',
                'admin/my_account.my_account_password',
                'admin/my_account.my_account_password_update'
            ]
            if _route_name not in skip_user_check_urls:
                return self._dispatch_redirect(
                    url('my_account_password'), environ, start_response)

        return WSGIController.__call__(self, environ, start_response)


class BaseRepoController(BaseController):
    """
    Base class for controllers responsible for loading all needed data for
    repository loaded items are

    c.rhodecode_repo: instance of scm repository
    c.rhodecode_db_repo: instance of db
    c.repository_requirements_missing: shows that repository specific data
        could not be displayed due to the missing requirements
    c.repository_pull_requests: show number of open pull requests
    """

    def __before__(self):
        super(BaseRepoController, self).__before__()
        if c.repo_name:  # extracted from routes
            db_repo = Repository.get_by_repo_name(c.repo_name)
            if not db_repo:
                return

            log.debug(
                'Found repository in database %s with state `%s`',
                safe_unicode(db_repo), safe_unicode(db_repo.repo_state))
            route = getattr(request.environ.get('routes.route'), 'name', '')

            # allow to delete repos that are somehow damages in filesystem
            if route in ['delete_repo']:
                return

            if db_repo.repo_state in [Repository.STATE_PENDING]:
                if route in ['repo_creating_home']:
                    return
                check_url = url('repo_creating_home', repo_name=c.repo_name)
                return redirect(check_url)

            self.rhodecode_db_repo = db_repo

            missing_requirements = False
            try:
                self.rhodecode_repo = self.rhodecode_db_repo.scm_instance()
            except RepositoryRequirementError as e:
                missing_requirements = True
                self._handle_missing_requirements(e)

            if self.rhodecode_repo is None and not missing_requirements:
                log.error('%s this repository is present in database but it '
                          'cannot be created as an scm instance', c.repo_name)

                h.flash(_(
                    "The repository at %(repo_name)s cannot be located.") %
                    {'repo_name': c.repo_name},
                    category='error', ignore_duplicate=True)
                redirect(url('home'))

            # update last change according to VCS data
            if not missing_requirements:
                commit = db_repo.get_commit(
                    pre_load=["author", "date", "message", "parents"])
                db_repo.update_commit_cache(commit)

            # Prepare context
            c.rhodecode_db_repo = db_repo
            c.rhodecode_repo = self.rhodecode_repo
            c.repository_requirements_missing = missing_requirements

            self._update_global_counters(self.scm_model, db_repo)

    def _update_global_counters(self, scm_model, db_repo):
        """
        Base variables that are exposed to every page of repository
        """
        c.repository_pull_requests = scm_model.get_pull_requests(db_repo)

    def _handle_missing_requirements(self, error):
        self.rhodecode_repo = None
        log.error(
            'Requirements are missing for repository %s: %s',
            c.repo_name, error.message)

        summary_url = url('summary_home', repo_name=c.repo_name)
        statistics_url = url('edit_repo_statistics', repo_name=c.repo_name)
        settings_update_url = url('repo', repo_name=c.repo_name)
        path = request.path
        should_redirect = (
            path not in (summary_url, settings_update_url)
            and '/settings' not in path or path == statistics_url
        )
        if should_redirect:
            redirect(summary_url)
