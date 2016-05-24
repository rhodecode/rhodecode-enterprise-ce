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
Login controller for rhodeocode
"""

import datetime
import formencode
import logging
import urlparse
import uuid

from formencode import htmlfill
from webob.exc import HTTPFound
from pylons.i18n.translation import _
from pylons.controllers.util import redirect
from pylons import request, session, tmpl_context as c, url
from recaptcha.client.captcha import submit

import rhodecode.lib.helpers as h
from rhodecode.lib.auth import (
    AuthUser, HasPermissionAnyDecorator, CSRFRequired)
from rhodecode.authentication.base import loadplugin
from rhodecode.lib.base import BaseController, render
from rhodecode.lib.exceptions import UserCreationError
from rhodecode.lib.utils2 import safe_str
from rhodecode.model.db import User, ExternalIdentity
from rhodecode.model.forms import LoginForm, RegisterForm, PasswordResetForm
from rhodecode.model.login_session import LoginSession
from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel
from rhodecode.model.user import UserModel

log = logging.getLogger(__name__)


class LoginController(BaseController):

    def __before__(self):
        super(LoginController, self).__before__()

    def _store_user_in_session(self, username, remember=False):
        user = User.get_by_username(username, case_insensitive=True)
        auth_user = AuthUser(user.user_id)
        auth_user.set_authenticated()
        cs = auth_user.get_cookie_store()
        session['rhodecode_user'] = cs
        user.update_lastlogin()
        Session().commit()

        # If they want to be remembered, update the cookie
        if remember:
            _year = (datetime.datetime.now() +
                     datetime.timedelta(seconds=60 * 60 * 24 * 365))
            session._set_cookie_expires(_year)

        session.save()

        log.info('user %s is now authenticated and stored in '
                 'session, session attrs %s', username, cs)

        # dumps session attrs back to cookie
        session._update_cookie_out()
        # we set new cookie
        headers = None
        if session.request['set_cookie']:
            # send set-cookie headers back to response to update cookie
            headers = [('Set-Cookie', session.request['cookie_out'])]
        return headers

    def _validate_came_from(self, came_from):
        if not came_from:
            return came_from

        parsed = urlparse.urlparse(came_from)
        server_parsed = urlparse.urlparse(url.current())
        allowed_schemes = ['http', 'https']
        if parsed.scheme and parsed.scheme not in allowed_schemes:
            log.error('Suspicious URL scheme detected %s for url %s' %
                      (parsed.scheme, parsed))
            came_from = url('home')
        elif server_parsed.netloc != parsed.netloc:
            log.error('Suspicious NETLOC detected %s for url %s server url '
                      'is: %s' % (parsed.netloc, parsed, server_parsed))
            came_from = url('home')
        if any(bad_str in parsed.path for bad_str in ('\r', '\n')):
            log.error('Header injection detected `%s` for url %s server url ' %
                      (parsed.path, parsed))
            came_from = url('home')
        return came_from

    def _redirect_to_origin(self, location, headers=None):
        request.GET.pop('came_from', None)
        raise HTTPFound(location=location, headers=headers)

    def _set_came_from(self):
        _default_came_from = url('home')
        came_from = self._validate_came_from(
            safe_str(request.GET.get('came_from', '')))
        c.came_from = came_from or _default_came_from

    def index(self):
        self._set_came_from()

        not_default = c.rhodecode_user.username != User.DEFAULT_USER
        ip_allowed = c.rhodecode_user.ip_allowed
        c.social_plugins = self._get_active_social_plugins()

        # redirect if already logged in
        if c.rhodecode_user.is_authenticated and not_default and ip_allowed:
            raise self._redirect_to_origin(location=c.came_from)

        if request.POST:
            # import Login Form validator class
            login_form = LoginForm()()
            try:
                session.invalidate()
                c.form_result = login_form.to_python(dict(request.POST))
                # form checks for username/password, now we're authenticated
                headers = self._store_user_in_session(
                    username=c.form_result['username'],
                    remember=c.form_result['remember'])
                raise self._redirect_to_origin(
                    location=c.came_from, headers=headers)
            except formencode.Invalid as errors:
                defaults = errors.value
                # remove password from filling in form again
                del defaults['password']
                return htmlfill.render(
                    render('/login.html'),
                    defaults=errors.value,
                    errors=errors.error_dict or {},
                    prefix_error=False,
                    encoding="UTF-8",
                    force_defaults=False)
            except UserCreationError as e:
                # container auth or other auth functions that create users on
                # the fly can throw this exception signaling that there's issue
                # with user creation, explanation should be provided in
                # Exception itself
                h.flash(e, 'error')

        # check if we use container plugin, and try to login using it.
        from rhodecode.authentication.base import authenticate, HTTP_TYPE
        try:
            log.debug('Running PRE-AUTH for container based authentication')
            auth_info = authenticate(
                '', '', request.environ, HTTP_TYPE, skip_missing=True)
        except UserCreationError as e:
            log.error(e)
            h.flash(e, 'error')
            # render login, with flash message about limit
            return render('/login.html')

        if auth_info:
            headers = self._store_user_in_session(auth_info.get('username'))
            raise self._redirect_to_origin(
                location=c.came_from, headers=headers)
        return render('/login.html')

    # TODO: Move this to a better place.
    def _get_active_social_plugins(self):
        from rhodecode.authentication.base import AuthomaticBase
        activated_plugins = SettingsModel().get_auth_plugins()
        social_plugins = []
        for plugin_id in activated_plugins:
            plugin = loadplugin(plugin_id)
            if isinstance(plugin, AuthomaticBase) and plugin.is_active():
                    social_plugins.append(plugin)
        return social_plugins

    @HasPermissionAnyDecorator('hg.admin', 'hg.register.auto_activate',
                               'hg.register.manual_activate')
    def register(self):
        c.auto_active = 'hg.register.auto_activate' in User.get_default_user()\
            .AuthUser.permissions['global']

        settings = SettingsModel().get_all_settings()
        captcha_private_key = settings.get('rhodecode_captcha_private_key')
        c.captcha_active = bool(captcha_private_key)
        c.captcha_public_key = settings.get('rhodecode_captcha_public_key')
        c.register_message = settings.get('rhodecode_register_message') or ''

        c.social_plugins = self._get_active_social_plugins()

        social_data = session.get('rhodecode.social_auth')
        c.form_data = {}
        if social_data:
            c.form_data = {'username': social_data['user'].get('user_name'),
                           'password': str(uuid.uuid4()),
                           'email': social_data['user'].get('email')
                           }

        if request.POST:
            register_form = RegisterForm()()
            try:
                form_result = register_form.to_python(dict(request.POST))
                form_result['active'] = c.auto_active

                if c.captcha_active:
                    response = submit(
                        request.POST.get('recaptcha_challenge_field'),
                        request.POST.get('recaptcha_response_field'),
                        private_key=captcha_private_key,
                        remoteip=self.ip_addr)
                    if c.captcha_active and not response.is_valid:
                        _value = form_result
                        _msg = _('bad captcha')
                        error_dict = {'recaptcha_field': _msg}
                        raise formencode.Invalid(_msg, _value, None,
                                                 error_dict=error_dict)

                new_user = UserModel().create_registration(form_result)
                if social_data:
                    plugin_name = 'egg:rhodecode-enterprise-ee#{}'.format(
                        social_data['credentials.provider']
                    )
                    auth_plugin = loadplugin(plugin_name)
                    if auth_plugin:
                        auth_plugin.handle_social_data(
                            session, new_user.user_id, social_data)
                h.flash(_('You have successfully registered with RhodeCode'),
                        category='success')
                Session().commit()
                return redirect(url('login_home'))

            except formencode.Invalid as errors:
                return htmlfill.render(
                    render('/register.html'),
                    defaults=errors.value,
                    errors=errors.error_dict or {},
                    prefix_error=False,
                    encoding="UTF-8",
                    force_defaults=False)
            except UserCreationError as e:
                # container auth or other auth functions that create users on
                # the fly can throw this exception signaling that there's issue
                # with user creation, explanation should be provided in
                # Exception itself
                h.flash(e, 'error')

        return render('/register.html')

    def password_reset(self):
        settings = SettingsModel().get_all_settings()
        captcha_private_key = settings.get('rhodecode_captcha_private_key')
        c.captcha_active = bool(captcha_private_key)
        c.captcha_public_key = settings.get('rhodecode_captcha_public_key')

        if request.POST:
            password_reset_form = PasswordResetForm()()
            try:
                form_result = password_reset_form.to_python(dict(request.POST))
                if c.captcha_active:
                    response = submit(
                        request.POST.get('recaptcha_challenge_field'),
                        request.POST.get('recaptcha_response_field'),
                        private_key=captcha_private_key,
                        remoteip=self.ip_addr)
                    if c.captcha_active and not response.is_valid:
                        _value = form_result
                        _msg = _('bad captcha')
                        error_dict = {'recaptcha_field': _msg}
                        raise formencode.Invalid(_msg, _value, None,
                                                 error_dict=error_dict)
                UserModel().reset_password_link(form_result)
                h.flash(_('Your password reset link was sent'),
                        category='success')
                return redirect(url('login_home'))

            except formencode.Invalid as errors:
                return htmlfill.render(
                    render('/password_reset.html'),
                    defaults=errors.value,
                    errors=errors.error_dict or {},
                    prefix_error=False,
                    encoding="UTF-8",
                    force_defaults=False)

        return render('/password_reset.html')

    def password_reset_confirmation(self):
        if request.GET and request.GET.get('key'):
            try:
                user = User.get_by_auth_token(request.GET.get('key'))
                data = {'email': user.email}
                UserModel().reset_password(data)
                h.flash(_(
                    'Your password reset was successful, '
                    'a new password has been sent to your email'),
                    category='success')
            except Exception as e:
                log.error(e)
                return redirect(url('reset_password'))

        return redirect(url('login_home'))

    @CSRFRequired()
    def logout(self):
        LoginSession().destroy_user_session()
        return redirect(url('home'))

    def social_auth(self, provider_name):
        plugin_name = 'egg:rhodecode-enterprise-ee#{}'.format(
            provider_name
        )
        auth_plugin = loadplugin(plugin_name)
        if not auth_plugin:
            return self._handle_social_auth_error(request, 'No auth plugin')

        result, response = auth_plugin.get_provider_result(request)
        if result:
            if result.error:
                return self._handle_social_auth_error(request, result.error)
            elif result.user:
                return self._handle_social_auth_success(request, result)
        return response

    def _handle_social_auth_error(self, request, result):
        log.error(result)
        h.flash(_('There was an error during OAuth processing.'),
                category='error')
        return redirect(url('home'))

    def _normalize_social_data(self, result):
        social_data = {
            'user': {'data': result.user.data},
            'credentials.provider': result.user.credentials.provider_name,
            'credentials.token': result.user.credentials.token,
            'credentials.token_secret': result.user.credentials.token_secret,
            'credentials.refresh_token': result.user.credentials.refresh_token
        }
        # normalize data
        social_data['user']['id'] = result.user.id
        user_name = result.user.username or ''
        # use email name as username for google
        if (social_data['credentials.provider'] == 'google' and
                result.user.email):
            user_name = result.user.email

        social_data['user']['user_name'] = user_name
        social_data['user']['email'] = result.user.email or ''
        return social_data

    def _handle_social_auth_success(self, request, result):
        self._set_came_from()

        # Hooray, we have the user!
        # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
        # We need to update the user to get more info.
        if result.user:
            result.user.update()

        social_data = self._normalize_social_data(result)

        session['rhodecode.social_auth'] = social_data

        plugin_name = 'egg:rhodecode-enterprise-ee#{}'.format(
            social_data['credentials.provider']
        )
        auth_plugin = loadplugin(plugin_name)

        # user is logged so bind his external identity with account
        if request.user and request.user.username != User.DEFAULT_USER:
            if auth_plugin:
                auth_plugin.handle_social_data(
                    session, request.user.user_id, social_data)
                session.pop('rhodecode.social_auth', None)
                Session().commit()
            return redirect(url('my_account_oauth'))
        else:
            user = ExternalIdentity.user_by_external_id_and_provider(
                social_data['user']['id'],
                social_data['credentials.provider']
            )

            # user tokens are already found in our db
            if user:
                if auth_plugin:
                    auth_plugin.handle_social_data(
                        session, user.user_id, social_data)
                    session.pop('rhodecode.social_auth', None)
                headers = self._store_user_in_session(user.username)
                raise self._redirect_to_origin(
                    location=c.came_from, headers=headers)
            else:
                msg = _('You need to finish registration '
                        'process to bind your external identity to your '
                        'account or sign in to existing account')
                h.flash(msg, category='success')
                return redirect(url('register'))
