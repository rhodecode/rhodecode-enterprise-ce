# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016  RhodeCode GmbH
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
my account controller for RhodeCode admin
"""

import logging

import formencode
from formencode import htmlfill
from pylons import request, tmpl_context as c, url, session
from pylons.controllers.util import redirect
from pylons.i18n.translation import _
from sqlalchemy.orm import joinedload

from rhodecode.lib import helpers as h
from rhodecode.lib import auth
from rhodecode.lib.auth import (
    LoginRequired, NotAnonymous, AuthUser, generate_auth_token)
from rhodecode.lib.base import BaseController, render
from rhodecode.lib.utils2 import safe_int, md5
from rhodecode.lib.ext_json import json
from rhodecode.model.db import (Repository, PullRequest, PullRequestReviewers,
                                UserEmailMap, User, UserFollowing,
                                ExternalIdentity)
from rhodecode.model.forms import UserForm, PasswordChangeForm
from rhodecode.model.scm import RepoList
from rhodecode.model.user import UserModel
from rhodecode.model.repo import RepoModel
from rhodecode.model.auth_token import AuthTokenModel
from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel

log = logging.getLogger(__name__)


class MyAccountController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('setting', 'settings', controller='admin/settings',
    #         path_prefix='/admin', name_prefix='admin_')

    @LoginRequired()
    @NotAnonymous()
    def __before__(self):
        super(MyAccountController, self).__before__()

    def __load_data(self):
        c.user = User.get(c.rhodecode_user.user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user since it's"
                      " crucial for entire application"), category='warning')
            return redirect(url('users'))

    def _load_my_repos_data(self, watched=False):
        if watched:
            admin = False
            follows_repos = Session().query(UserFollowing)\
                .filter(UserFollowing.user_id == c.rhodecode_user.user_id)\
                .options(joinedload(UserFollowing.follows_repository))\
                .all()
            repo_list = [x.follows_repository for x in follows_repos]
        else:
            admin = True
            repo_list = Repository.get_all_repos(
                user_id=c.rhodecode_user.user_id)
            repo_list = RepoList(repo_list, perm_set=[
                'repository.read', 'repository.write', 'repository.admin'])

        repos_data = RepoModel().get_repos_as_dict(
            repo_list=repo_list, admin=admin)
        # json used to render the grid
        return json.dumps(repos_data)

    @auth.CSRFRequired()
    def my_account_update(self):
        """
        POST /_admin/my_account Updates info of my account
        """
        # url('my_account')
        c.active = 'profile_edit'
        self.__load_data()
        c.perm_user = AuthUser(user_id=c.rhodecode_user.user_id,
                               ip_addr=self.ip_addr)
        c.extern_type = c.user.extern_type
        c.extern_name = c.user.extern_name

        defaults = c.user.get_dict()
        update = False
        _form = UserForm(edit=True,
                         old_data={'user_id': c.rhodecode_user.user_id,
                                   'email': c.rhodecode_user.email})()
        form_result = {}
        try:
            post_data = dict(request.POST)
            post_data['new_password'] = ''
            post_data['password_confirmation'] = ''
            form_result = _form.to_python(post_data)
            # skip updating those attrs for my account
            skip_attrs = ['admin', 'active', 'extern_type', 'extern_name',
                          'new_password', 'password_confirmation']
            # TODO: plugin should define if username can be updated
            if c.extern_type != "rhodecode":
                # forbid updating username for external accounts
                skip_attrs.append('username')

            UserModel().update_user(
                c.rhodecode_user.user_id, skip_attrs=skip_attrs, **form_result)
            h.flash(_('Your account was updated successfully'),
                    category='success')
            Session().commit()
            update = True

        except formencode.Invalid as errors:
            return htmlfill.render(
                render('admin/my_account/my_account.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception updating user")
            h.flash(_('Error occurred during update of user %s')
                    % form_result.get('username'), category='error')

        if update:
            return redirect('my_account')

        return htmlfill.render(
            render('admin/my_account/my_account.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    def my_account(self):
        """
        GET /_admin/my_account Displays info about my account
        """
        # url('my_account')
        c.active = 'profile'
        self.__load_data()

        defaults = c.user.get_dict()
        return htmlfill.render(
            render('admin/my_account/my_account.html'),
            defaults=defaults, encoding="UTF-8", force_defaults=False)

    def my_account_edit(self):
        """
        GET /_admin/my_account/edit Displays edit form of my account
        """
        c.active = 'profile_edit'
        self.__load_data()
        c.perm_user = AuthUser(user_id=c.rhodecode_user.user_id,
                               ip_addr=self.ip_addr)
        c.extern_type = c.user.extern_type
        c.extern_name = c.user.extern_name

        defaults = c.user.get_dict()
        return htmlfill.render(
            render('admin/my_account/my_account.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @auth.CSRFRequired()
    def my_account_password_update(self):
        c.active = 'password'
        self.__load_data()
        _form = PasswordChangeForm(c.rhodecode_user.username)()
        try:
            form_result = _form.to_python(request.POST)
            UserModel().update_user(c.rhodecode_user.user_id, **form_result)
            instance = c.rhodecode_user.get_instance()
            instance.update_userdata(force_password_change=False)
            Session().commit()
            session.setdefault('rhodecode_user', {}).update(
                {'password': md5(instance.password)})
            session.save()
            h.flash(_("Successfully updated password"), category='success')
        except formencode.Invalid as errors:
            return htmlfill.render(
                render('admin/my_account/my_account.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception updating password")
            h.flash(_('Error occurred during update of user password'),
                    category='error')
        return render('admin/my_account/my_account.html')

    def my_account_password(self):
        c.active = 'password'
        self.__load_data()
        return render('admin/my_account/my_account.html')

    def my_account_repos(self):
        c.active = 'repos'
        self.__load_data()

        # json used to render the grid
        c.data = self._load_my_repos_data()
        return render('admin/my_account/my_account.html')

    def my_account_watched(self):
        c.active = 'watched'
        self.__load_data()

        # json used to render the grid
        c.data = self._load_my_repos_data(watched=True)
        return render('admin/my_account/my_account.html')

    def my_account_perms(self):
        c.active = 'perms'
        self.__load_data()
        c.perm_user = AuthUser(user_id=c.rhodecode_user.user_id,
                               ip_addr=self.ip_addr)

        return render('admin/my_account/my_account.html')

    def my_account_emails(self):
        c.active = 'emails'
        self.__load_data()

        c.user_email_map = UserEmailMap.query()\
            .filter(UserEmailMap.user == c.user).all()
        return render('admin/my_account/my_account.html')

    @auth.CSRFRequired()
    def my_account_emails_add(self):
        email = request.POST.get('new_email')

        try:
            UserModel().add_extra_email(c.rhodecode_user.user_id, email)
            Session().commit()
            h.flash(_("Added new email address `%s` for user account") % email,
                    category='success')
        except formencode.Invalid as error:
            msg = error.error_dict['email']
            h.flash(msg, category='error')
        except Exception:
            log.exception("Exception in my_account_emails")
            h.flash(_('An error occurred during email saving'),
                    category='error')
        return redirect(url('my_account_emails'))

    @auth.CSRFRequired()
    def my_account_emails_delete(self):
        email_id = request.POST.get('del_email_id')
        user_model = UserModel()
        user_model.delete_extra_email(c.rhodecode_user.user_id, email_id)
        Session().commit()
        h.flash(_("Removed email address from user account"),
                category='success')
        return redirect(url('my_account_emails'))

    def my_account_pullrequests(self):
        c.active = 'pullrequests'
        self.__load_data()
        c.show_closed = request.GET.get('pr_show_closed')

        def _filter(pr):
            s = sorted(pr, key=lambda o: o.created_on, reverse=True)
            if not c.show_closed:
                s = filter(lambda p: p.status != PullRequest.STATUS_CLOSED, s)
            return s

        c.my_pull_requests = _filter(
            PullRequest.query().filter(
                PullRequest.user_id == c.rhodecode_user.user_id).all())
        my_prs = [
            x.pull_request for x in PullRequestReviewers.query().filter(
                PullRequestReviewers.user_id == c.rhodecode_user.user_id).all()]
        c.participate_in_pull_requests = _filter(my_prs)
        return render('admin/my_account/my_account.html')

    def my_account_auth_tokens(self):
        c.active = 'auth_tokens'
        self.__load_data()
        show_expired = True
        c.lifetime_values = [
            (str(-1), _('forever')),
            (str(5), _('5 minutes')),
            (str(60), _('1 hour')),
            (str(60 * 24), _('1 day')),
            (str(60 * 24 * 30), _('1 month')),
        ]
        c.lifetime_options = [(c.lifetime_values, _("Lifetime"))]
        c.role_values = [(x, AuthTokenModel.cls._get_role_name(x))
                         for x in AuthTokenModel.cls.ROLES]
        c.role_options = [(c.role_values, _("Role"))]
        c.user_auth_tokens = AuthTokenModel().get_auth_tokens(
            c.rhodecode_user.user_id, show_expired=show_expired)
        return render('admin/my_account/my_account.html')

    @auth.CSRFRequired()
    def my_account_auth_tokens_add(self):
        lifetime = safe_int(request.POST.get('lifetime'), -1)
        description = request.POST.get('description')
        role = request.POST.get('role')
        AuthTokenModel().create(c.rhodecode_user.user_id, description, lifetime,
                                role)
        Session().commit()
        h.flash(_("Auth token successfully created"), category='success')
        return redirect(url('my_account_auth_tokens'))

    @auth.CSRFRequired()
    def my_account_auth_tokens_delete(self):
        auth_token = request.POST.get('del_auth_token')
        user_id = c.rhodecode_user.user_id
        if request.POST.get('del_auth_token_builtin'):
            user = User.get(user_id)
            if user:
                user.api_key = generate_auth_token(user.username)
                Session().add(user)
                Session().commit()
                h.flash(_("Auth token successfully reset"), category='success')
        elif auth_token:
            AuthTokenModel().delete(auth_token, c.rhodecode_user.user_id)
            Session().commit()
            h.flash(_("Auth token successfully deleted"), category='success')

        return redirect(url('my_account_auth_tokens'))

    def my_account_oauth(self):
        c.active = 'oauth'
        self.__load_data()
        c.user_oauth_tokens = ExternalIdentity().by_local_user_id(
            c.rhodecode_user.user_id).all()
        settings = SettingsModel().get_all_settings()
        c.social_plugins = SettingsModel().list_enabled_social_plugins(
            settings)
        return render('admin/my_account/my_account.html')

    @auth.CSRFRequired()
    def my_account_oauth_delete(self):
        token = ExternalIdentity.by_external_id_and_provider(
            request.params.get('external_id'),
            request.params.get('provider_name'),
            local_user_id=c.rhodecode_user.user_id
        )
        if token:
            Session().delete(token)
            Session().commit()
            h.flash(_("OAuth token successfully deleted"), category='success')

        return redirect(url('my_account_oauth'))
