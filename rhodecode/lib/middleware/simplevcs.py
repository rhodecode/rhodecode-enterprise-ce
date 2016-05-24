# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016  RhodeCode GmbH
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
SimpleVCS middleware for handling protocol request (push/clone etc.)
It's implemented with basic auth function
"""

import os
import logging
import importlib
from functools import wraps

from paste.httpheaders import REMOTE_USER, AUTH_TYPE
from webob.exc import (
    HTTPNotFound, HTTPForbidden, HTTPNotAcceptable, HTTPInternalServerError)

import rhodecode
from rhodecode.authentication.base import authenticate, VCS_TYPE
from rhodecode.lib.auth import AuthUser, HasPermissionAnyMiddleware
from rhodecode.lib.base import BasicAuth, get_ip_addr, vcs_operation_context
from rhodecode.lib.exceptions import (
    HTTPLockedRC, HTTPRequirementError, UserCreationError,
    NotAllowedToCreateUserError)
from rhodecode.lib.hooks_daemon import prepare_callback_daemon
from rhodecode.lib.middleware import appenlight
from rhodecode.lib.middleware.utils import scm_app
from rhodecode.lib.utils import is_valid_repo
from rhodecode.lib.utils2 import safe_str, fix_PATH, str2bool
from rhodecode.model import meta
from rhodecode.model.db import User, Repository
from rhodecode.model.scm import ScmModel
from rhodecode.model.settings import SettingsModel

log = logging.getLogger(__name__)


def initialize_generator(factory):
    """
    Initializes the returned generator by draining its first element.

    This can be used to give a generator an initializer, which is the code
    up to the first yield statement. This decorator enforces that the first
    produced element has the value ``"__init__"`` to make its special
    purpose very explicit in the using code.
    """

    @wraps(factory)
    def wrapper(*args, **kwargs):
        gen = factory(*args, **kwargs)
        try:
            init = gen.next()
        except StopIteration:
            raise ValueError('Generator must yield at least one element.')
        if init != "__init__":
            raise ValueError('First yielded element must be "__init__".')
        return gen
    return wrapper


class SimpleVCS(object):
    """Common functionality for SCM HTTP handlers."""

    SCM = 'unknown'

    def __init__(self, application, config):
        self.application = application
        self.config = config
        # base path of repo locations
        self.basepath = self.config['base_path']
        # authenticate this VCS request using authfunc
        auth_ret_code_detection = \
            str2bool(self.config.get('auth_ret_code_detection', False))
        self.authenticate = BasicAuth('', authenticate,
                                      config.get('auth_ret_code'),
                                      auth_ret_code_detection)
        self.ip_addr = '0.0.0.0'

    @property
    def scm_app(self):
        custom_implementation = self.config.get('vcs.scm_app_implementation')
        if custom_implementation:
            log.info(
                "Using custom implementation of scm_app: %s",
                custom_implementation)
            scm_app_impl = importlib.import_module(custom_implementation)
        else:
            scm_app_impl = scm_app
        return scm_app_impl

    def _get_by_id(self, repo_name):
        """
        Gets a special pattern _<ID> from clone url and tries to replace it
        with a repository_name for support of _<ID> non changable urls

        :param repo_name:
        """

        data = repo_name.split('/')
        if len(data) >= 2:
            from rhodecode.model.repo import RepoModel
            by_id_match = RepoModel().get_repo_by_id(repo_name)
            if by_id_match:
                data[1] = by_id_match.repo_name

        return safe_str('/'.join(data))

    def _invalidate_cache(self, repo_name):
        """
        Set's cache for this repository for invalidation on next access

        :param repo_name: full repo name, also a cache key
        """
        ScmModel().mark_for_invalidation(repo_name)

    def is_valid_and_existing_repo(self, repo_name, base_path, scm_type):
        db_repo = Repository.get_by_repo_name(repo_name)
        if not db_repo:
            log.debug('Repository `%s` not found inside the database.')
            return False

        if db_repo.repo_type != scm_type:
            log.warning(
                'Repository `%s` have incorrect scm_type, expected %s got %s',
                repo_name, db_repo.repo_type, scm_type)
            return False

        return is_valid_repo(repo_name, base_path, expect_scm=scm_type)

    def valid_and_active_user(self, user):
        """
        Checks if that user is not empty, and if it's actually object it checks
        if he's active.

        :param user: user object or None
        :return: boolean
        """
        if user is None:
            return False

        elif user.active:
            return True

        return False

    def _check_permission(self, action, user, repo_name, ip_addr=None):
        """
        Checks permissions using action (push/pull) user and repository
        name

        :param action: push or pull action
        :param user: user instance
        :param repo_name: repository name
        """
        # check IP
        inherit = user.inherit_default_permissions
        ip_allowed = AuthUser.check_ip_allowed(user.user_id, ip_addr,
                                               inherit_from_default=inherit)
        if ip_allowed:
            log.info('Access for IP:%s allowed', ip_addr)
        else:
            return False

        if action == 'push':
            if not HasPermissionAnyMiddleware('repository.write',
                                              'repository.admin')(user,
                                                                  repo_name):
                return False

        else:
            # any other action need at least read permission
            if not HasPermissionAnyMiddleware('repository.read',
                                              'repository.write',
                                              'repository.admin')(user,
                                                                  repo_name):
                return False

        return True

    def _check_ssl(self, environ, start_response):
        """
        Checks the SSL check flag and returns False if SSL is not present
        and required True otherwise
        """
        org_proto = environ['wsgi._org_proto']
        # check if we have SSL required  ! if not it's a bad request !
        require_ssl = str2bool(
            SettingsModel().get_ui_by_key('push_ssl').ui_value)
        if require_ssl and org_proto == 'http':
            log.debug('proto is %s and SSL is required BAD REQUEST !',
                      org_proto)
            return False
        return True

    def __call__(self, environ, start_response):
        try:
            return self._handle_request(environ, start_response)
        except Exception:
            log.exception("Exception while handling request")
            appenlight.track_exception(environ)
            return HTTPInternalServerError()(environ, start_response)
        finally:
            meta.Session.remove()

    def _handle_request(self, environ, start_response):

        if not self._check_ssl(environ, start_response):
            reason = ('SSL required, while RhodeCode was unable '
                      'to detect this as SSL request')
            log.debug('User not allowed to proceed, %s', reason)
            return HTTPNotAcceptable(reason)(environ, start_response)

        ip_addr = get_ip_addr(environ)
        username = None

        # skip passing error to error controller
        environ['pylons.status_code_redirect'] = True

        # ======================================================================
        # EXTRACT REPOSITORY NAME FROM ENV
        # ======================================================================
        environ['PATH_INFO'] = self._get_by_id(environ['PATH_INFO'])
        repo_name = self._get_repository_name(environ)
        environ['REPO_NAME'] = repo_name
        log.debug('Extracted repo name is %s', repo_name)

        # check for type, presence in database and on filesystem
        if not self.is_valid_and_existing_repo(
                repo_name, self.basepath, self.SCM):
            return HTTPNotFound()(environ, start_response)

        # ======================================================================
        # GET ACTION PULL or PUSH
        # ======================================================================
        action = self._get_action(environ)

        # ======================================================================
        # CHECK ANONYMOUS PERMISSION
        # ======================================================================
        if action in ['pull', 'push']:
            anonymous_user = User.get_default_user()
            username = anonymous_user.username
            if anonymous_user.active:
                # ONLY check permissions if the user is activated
                anonymous_perm = self._check_permission(
                    action, anonymous_user, repo_name, ip_addr)
            else:
                anonymous_perm = False

            if not anonymous_user.active or not anonymous_perm:
                if not anonymous_user.active:
                    log.debug('Anonymous access is disabled, running '
                              'authentication')

                if not anonymous_perm:
                    log.debug('Not enough credentials to access this '
                              'repository as anonymous user')

                username = None
                # ==============================================================
                # DEFAULT PERM FAILED OR ANONYMOUS ACCESS IS DISABLED SO WE
                # NEED TO AUTHENTICATE AND ASK FOR AUTH USER PERMISSIONS
                # ==============================================================

                # try to auth based on environ, container auth methods
                log.debug('Running PRE-AUTH for container based authentication')
                pre_auth = authenticate('', '', environ,VCS_TYPE)
                if pre_auth and pre_auth.get('username'):
                    username = pre_auth['username']
                log.debug('PRE-AUTH got %s as username', username)

                # If not authenticated by the container, running basic auth
                if not username:
                    self.authenticate.realm = \
                        safe_str(self.config['rhodecode_realm'])

                    try:
                        result = self.authenticate(environ)
                    except (UserCreationError, NotAllowedToCreateUserError) as e:
                        log.error(e)
                        reason = safe_str(e)
                        return HTTPNotAcceptable(reason)(environ, start_response)

                    if isinstance(result, str):
                        AUTH_TYPE.update(environ, 'basic')
                        REMOTE_USER.update(environ, result)
                        username = result
                    else:
                        return result.wsgi_application(environ, start_response)

                # ==============================================================
                # CHECK PERMISSIONS FOR THIS REQUEST USING GIVEN USERNAME
                # ==============================================================
                user = User.get_by_username(username)
                if not self.valid_and_active_user(user):
                    return HTTPForbidden()(environ, start_response)
                username = user.username
                user.update_lastactivity()
                meta.Session().commit()

                # check user attributes for password change flag
                user_obj = user
                if user_obj and user_obj.username != User.DEFAULT_USER and \
                        user_obj.user_data.get('force_password_change'):
                    reason = 'password change required'
                    log.debug('User not allowed to authenticate, %s', reason)
                    return HTTPNotAcceptable(reason)(environ, start_response)

                # check permissions for this repository
                perm = self._check_permission(action, user, repo_name, ip_addr)
                if not perm:
                    return HTTPForbidden()(environ, start_response)

        # extras are injected into UI object and later available
        # in hooks executed by rhodecode
        check_locking = _should_check_locking(environ.get('QUERY_STRING'))
        extras = vcs_operation_context(
            environ, repo_name=repo_name, username=username,
            action=action, scm=self.SCM,
            check_locking=check_locking)

        # ======================================================================
        # REQUEST HANDLING
        # ======================================================================
        str_repo_name = safe_str(repo_name)
        repo_path = os.path.join(safe_str(self.basepath), str_repo_name)
        log.debug('Repository path is %s', repo_path)

        fix_PATH()

        log.info(
            '%s action on %s repo "%s" by "%s" from %s',
            action, self.SCM, str_repo_name, safe_str(username), ip_addr)
        return self._generate_vcs_response(
            environ, start_response, repo_path, repo_name, extras, action)

    @initialize_generator
    def _generate_vcs_response(
            self, environ, start_response, repo_path, repo_name, extras,
            action):
        """
        Returns a generator for the response content.

        This method is implemented as a generator, so that it can trigger
        the cache validation after all content sent back to the client. It
        also handles the locking exceptions which will be triggered when
        the first chunk is produced by the underlying WSGI application.
        """
        callback_daemon, extras = self._prepare_callback_daemon(extras)
        config = self._create_config(extras, repo_name)
        log.debug('HOOKS extras is %s', extras)
        app = self._create_wsgi_app(repo_path, repo_name, config)

        try:
            with callback_daemon:
                try:
                    response = app(environ, start_response)
                finally:
                    # This statement works together with the decorator
                    # "initialize_generator" above. The decorator ensures that
                    # we hit the first yield statement before the generator is
                    # returned back to the WSGI server. This is needed to
                    # ensure that the call to "app" above triggers the
                    # needed callback to "start_response" before the
                    # generator is actually used.
                    yield "__init__"

                for chunk in response:
                    yield chunk
        except Exception as exc:
            # TODO: johbo: Improve "translating" back the exception.
            if getattr(exc, '_vcs_kind', None) == 'repo_locked':
                exc = HTTPLockedRC(*exc.args)
                _code = rhodecode.CONFIG.get('lock_ret_code')
                log.debug('Repository LOCKED ret code %s!', (_code,))
            elif getattr(exc, '_vcs_kind', None) == 'requirement':
                log.debug(
                    'Repository requires features unknown to this Mercurial')
                exc = HTTPRequirementError(*exc.args)
            else:
                raise

            for chunk in exc(environ, start_response):
                yield chunk
        finally:
            # invalidate cache on push
            if action == 'push':
                self._invalidate_cache(repo_name)

    def _get_repository_name(self, environ):
        """Get repository name out of the environmnent

        :param environ: WSGI environment
        """
        raise NotImplementedError()

    def _get_action(self, environ):
        """Map request commands into a pull or push command.

        :param environ: WSGI environment
        """
        raise NotImplementedError()

    def _create_wsgi_app(self, repo_path, repo_name, config):
        """Return the WSGI app that will finally handle the request."""
        raise NotImplementedError()

    def _create_config(self, extras, repo_name):
        """Create a Pyro safe config representation."""
        raise NotImplementedError()

    def _prepare_callback_daemon(self, extras):
        return prepare_callback_daemon(
            extras, protocol=self.config.get('vcs.hooks.protocol'),
            use_direct_calls=self.config.get('vcs.hooks.direct_calls'))


def _should_check_locking(query_string):
    # this is kind of hacky, but due to how mercurial handles client-server
    # server see all operation on commit; bookmarks, phases and
    # obsolescence marker in different transaction, we don't want to check
    # locking on those
    return query_string not in ['cmd=listkeys']
