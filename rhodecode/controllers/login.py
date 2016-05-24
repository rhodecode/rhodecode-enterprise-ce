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
from rhodecode.model.db import User
from rhodecode.model.forms import LoginForm, RegisterForm, PasswordResetForm
from rhodecode.model.login_session import LoginSession
from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel
from rhodecode.model.user import UserModel

log = logging.getLogger(__name__)


def _store_user_in_session(username, remember=False):
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


class LoginController(BaseController):

    def __before__(self):
        super(LoginController, self).__before__()

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
                headers = _store_user_in_session(
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
            headers = _store_user_in_session(auth_info.get('username'))
            raise self._redirect_to_origin(
                location=c.came_from, headers=headers)
        return render('/login.html')

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
        c.form_data = {}

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

                UserModel().create_registration(form_result)
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
