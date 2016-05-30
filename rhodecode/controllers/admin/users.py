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
Users crud controller for pylons
"""

import logging
import formencode

from formencode import htmlfill
from pylons import request, tmpl_context as c, url, config
from pylons.controllers.util import redirect
from pylons.i18n.translation import _

from rhodecode.authentication.plugins import auth_rhodecode
from rhodecode.lib.exceptions import (
    DefaultUserException, UserOwnsReposException, UserOwnsRepoGroupsException,
    UserOwnsUserGroupsException, UserCreationError)
from rhodecode.lib import helpers as h
from rhodecode.lib import auth
from rhodecode.lib.auth import (
    LoginRequired, HasPermissionAllDecorator, AuthUser, generate_auth_token)
from rhodecode.lib.base import BaseController, render
from rhodecode.model.auth_token import AuthTokenModel

from rhodecode.model.db import (
    PullRequestReviewers, User, UserEmailMap, UserIpMap, RepoGroup)
from rhodecode.model.forms import (
    UserForm, UserPermissionsForm, UserIndividualPermissionsForm)
from rhodecode.model.user import UserModel
from rhodecode.model.meta import Session
from rhodecode.model.permission import PermissionModel
from rhodecode.lib.utils import action_logger
from rhodecode.lib.ext_json import json
from rhodecode.lib.utils2 import datetime_to_time, safe_int

log = logging.getLogger(__name__)


class UsersController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""

    @LoginRequired()
    def __before__(self):
        super(UsersController, self).__before__()
        c.available_permissions = config['available_permissions']
        c.allowed_languages = [
            ('en', 'English (en)'),
            ('de', 'German (de)'),
            ('fr', 'French (fr)'),
            ('it', 'Italian (it)'),
            ('ja', 'Japanese (ja)'),
            ('pl', 'Polish (pl)'),
            ('pt', 'Portuguese (pt)'),
            ('ru', 'Russian (ru)'),
            ('zh', 'Chinese (zh)'),
        ]
        PermissionModel().set_global_permission_choices(c, translator=_)

    @HasPermissionAllDecorator('hg.admin')
    def index(self):
        """GET /users: All items in the collection"""
        # url('users')

        from rhodecode.lib.utils import PartialRenderer
        _render = PartialRenderer('data_table/_dt_elements.html')

        def grav_tmpl(user_email, size):
            return _render("user_gravatar", user_email, size)

        def username(user_id, username):
            return _render("user_name", user_id, username)

        def user_actions(user_id, username):
            return _render("user_actions", user_id, username)

        # json generate
        c.users_list = User.query()\
            .filter(User.username != User.DEFAULT_USER) \
            .all()

        users_data = []
        for user in c.users_list:
            users_data.append({
                "gravatar": grav_tmpl(user.email, 20),
                "username": h.link_to(
                    user.username, h.url('user_profile', username=user.username)),
                "username_raw": user.username,
                "email": user.email,
                "first_name": h.escape(user.name),
                "last_name": h.escape(user.lastname),
                "last_login": h.format_date(user.last_login),
                "last_login_raw": datetime_to_time(user.last_login),
                "last_activity": h.format_date(
                    h.time_to_datetime(user.user_data.get('last_activity', 0))),
                "last_activity_raw": user.user_data.get('last_activity', 0),
                "active": h.bool2icon(user.active),
                "active_raw": user.active,
                "admin": h.bool2icon(user.admin),
                "admin_raw": user.admin,
                "extern_type": user.extern_type,
                "extern_name": user.extern_name,
                "action": user_actions(user.user_id, user.username),
            })


        c.data = json.dumps(users_data)
        return render('admin/users/users.html')

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def create(self):
        """POST /users: Create a new item"""
        # url('users')
        c.default_extern_type = auth_rhodecode.RhodeCodeAuthPlugin.name
        user_model = UserModel()
        user_form = UserForm()()
        try:
            form_result = user_form.to_python(dict(request.POST))
            user = user_model.create(form_result)
            Session().flush()
            username = form_result['username']
            action_logger(c.rhodecode_user, 'admin_created_user:%s' % username,
                          None, self.ip_addr, self.sa)

            user_link = h.link_to(h.escape(username),
                                  url('edit_user',
                                      user_id=user.user_id))
            h.flash(h.literal(_('Created user %(user_link)s')
                              % {'user_link': user_link}), category='success')
            Session().commit()
        except formencode.Invalid as errors:
            return htmlfill.render(
                render('admin/users/user_add.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except UserCreationError as e:
            h.flash(e, 'error')
        except Exception:
            log.exception("Exception creation of user")
            h.flash(_('Error occurred during creation of user %s')
                    % request.POST.get('username'), category='error')
        return redirect(url('users'))

    @HasPermissionAllDecorator('hg.admin')
    def new(self):
        """GET /users/new: Form to create a new item"""
        # url('new_user')
        c.default_extern_type = auth_rhodecode.RhodeCodeAuthPlugin.name
        return render('admin/users/user_add.html')

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def update(self, user_id):
        """PUT /users/user_id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        # <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('update_user', user_id=ID),
        #           method='put')
        # url('user', user_id=ID)
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        c.active = 'profile'
        c.extern_type = c.user.extern_type
        c.extern_name = c.user.extern_name
        c.perm_user = AuthUser(user_id=user_id, ip_addr=self.ip_addr)
        available_languages = [x[0] for x in c.allowed_languages]
        _form = UserForm(edit=True, available_languages=available_languages,
                         old_data={'user_id': user_id,
                                   'email': c.user.email})()
        form_result = {}
        try:
            form_result = _form.to_python(dict(request.POST))
            skip_attrs = ['extern_type', 'extern_name']
            # TODO: plugin should define if username can be updated
            if c.extern_type != "rhodecode":
                # forbid updating username for external accounts
                skip_attrs.append('username')

            UserModel().update_user(user_id, skip_attrs=skip_attrs, **form_result)
            usr = form_result['username']
            action_logger(c.rhodecode_user, 'admin_updated_user:%s' % usr,
                          None, self.ip_addr, self.sa)
            h.flash(_('User updated successfully'), category='success')
            Session().commit()
        except formencode.Invalid as errors:
            defaults = errors.value
            e = errors.error_dict or {}

            return htmlfill.render(
                render('admin/users/user_edit.html'),
                defaults=defaults,
                errors=e,
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except UserCreationError as e:
            h.flash(e, 'error')
        except Exception:
            log.exception("Exception updating user")
            h.flash(_('Error occurred during update of user %s')
                    % form_result.get('username'), category='error')
        return redirect(url('edit_user', user_id=user_id))

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def delete(self, user_id):
        """DELETE /users/user_id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        # <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('delete_user', user_id=ID),
        #           method='delete')
        # url('user', user_id=ID)
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)

        _repos = c.user.repositories
        _repo_groups = c.user.repository_groups
        _user_groups = c.user.user_groups

        handle_repos = None
        handle_repo_groups = None
        handle_user_groups = None
        # dummy call for flash of handle
        set_handle_flash_repos = lambda: None
        set_handle_flash_repo_groups = lambda: None
        set_handle_flash_user_groups = lambda: None

        if _repos and request.POST.get('user_repos'):
            do = request.POST['user_repos']
            if do == 'detach':
                handle_repos = 'detach'
                set_handle_flash_repos = lambda: h.flash(
                    _('Detached %s repositories') % len(_repos),
                    category='success')
            elif do == 'delete':
                handle_repos = 'delete'
                set_handle_flash_repos = lambda: h.flash(
                    _('Deleted %s repositories') % len(_repos),
                    category='success')

        if _repo_groups and request.POST.get('user_repo_groups'):
            do = request.POST['user_repo_groups']
            if do == 'detach':
                handle_repo_groups = 'detach'
                set_handle_flash_repo_groups = lambda: h.flash(
                    _('Detached %s repository groups') % len(_repo_groups),
                    category='success')
            elif do == 'delete':
                handle_repo_groups = 'delete'
                set_handle_flash_repo_groups = lambda: h.flash(
                    _('Deleted %s repository groups') % len(_repo_groups),
                    category='success')

        if _user_groups and request.POST.get('user_user_groups'):
            do = request.POST['user_user_groups']
            if do == 'detach':
                handle_user_groups = 'detach'
                set_handle_flash_user_groups = lambda: h.flash(
                    _('Detached %s user groups') % len(_user_groups),
                    category='success')
            elif do == 'delete':
                handle_user_groups = 'delete'
                set_handle_flash_user_groups = lambda: h.flash(
                    _('Deleted %s user groups') % len(_user_groups),
                    category='success')

        try:
            UserModel().delete(c.user, handle_repos=handle_repos,
                               handle_repo_groups=handle_repo_groups,
                               handle_user_groups=handle_user_groups)
            Session().commit()
            set_handle_flash_repos()
            set_handle_flash_repo_groups()
            set_handle_flash_user_groups()
            h.flash(_('Successfully deleted user'), category='success')
        except (UserOwnsReposException, UserOwnsRepoGroupsException,
                UserOwnsUserGroupsException, DefaultUserException) as e:
            h.flash(e, category='warning')
        except Exception:
            log.exception("Exception during deletion of user")
            h.flash(_('An error occurred during deletion of user'),
                    category='error')
        return redirect(url('users'))

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def reset_password(self, user_id):
        """
        toggle reset password flag for this user

        :param user_id:
        """
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        try:
            old_value = c.user.user_data.get('force_password_change')
            c.user.update_userdata(force_password_change=not old_value)
            Session().commit()
            if old_value:
                msg = _('Force password change disabled for user')
            else:
                msg = _('Force password change enabled for user')
            h.flash(msg, category='success')
        except Exception:
            log.exception("Exception during password reset for user")
            h.flash(_('An error occurred during password reset for user'),
                    category='error')

        return redirect(url('edit_user_advanced', user_id=user_id))

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def create_personal_repo_group(self, user_id):
        """
        Create personal repository group for this user

        :param user_id:
        """
        from rhodecode.model.repo_group import RepoGroupModel

        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)

        try:
            desc = RepoGroupModel.PERSONAL_GROUP_DESC % {
                'username': c.user.username}
            if not RepoGroup.get_by_group_name(c.user.username):
                RepoGroupModel().create(group_name=c.user.username,
                                        group_description=desc,
                                        owner=c.user.username)

                msg = _('Created repository group `%s`' % (c.user.username,))
                h.flash(msg, category='success')
        except Exception:
            log.exception("Exception during repository group creation")
            msg = _(
                'An error occurred during repository group creation for user')
            h.flash(msg, category='error')

        return redirect(url('edit_user_advanced', user_id=user_id))

    @HasPermissionAllDecorator('hg.admin')
    def show(self, user_id):
        """GET /users/user_id: Show a specific item"""
        # url('user', user_id=ID)
        User.get_or_404(-1)

    @HasPermissionAllDecorator('hg.admin')
    def edit(self, user_id):
        """GET /users/user_id/edit: Form to edit an existing item"""
        # url('edit_user', user_id=ID)
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        c.active = 'profile'
        c.extern_type = c.user.extern_type
        c.extern_name = c.user.extern_name
        c.perm_user = AuthUser(user_id=user_id, ip_addr=self.ip_addr)

        defaults = c.user.get_dict()
        defaults.update({'language': c.user.user_data.get('language')})
        return htmlfill.render(
            render('admin/users/user_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    def edit_advanced(self, user_id):
        user_id = safe_int(user_id)
        user = c.user = User.get_or_404(user_id)
        if user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        c.active = 'advanced'
        c.perm_user = AuthUser(user_id=user_id, ip_addr=self.ip_addr)
        c.personal_repo_group = RepoGroup.get_by_group_name(user.username)
        c.first_admin = User.get_first_admin()
        defaults = user.get_dict()

        # Interim workaround if the user participated on any pull requests as a
        # reviewer.
        has_review = bool(PullRequestReviewers.query().filter(
            PullRequestReviewers.user_id == user_id).first())
        c.can_delete_user = not has_review
        c.can_delete_user_message = _(
            'The user participates as reviewer in pull requests and '
            'cannot be deleted. You can set the user to '
            '"inactive" instead of deleting it.') if has_review else ''

        return htmlfill.render(
            render('admin/users/user_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    def edit_auth_tokens(self, user_id):
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        c.active = 'auth_tokens'
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
            c.user.user_id, show_expired=show_expired)
        defaults = c.user.get_dict()
        return htmlfill.render(
            render('admin/users/user_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def add_auth_token(self, user_id):
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        lifetime = safe_int(request.POST.get('lifetime'), -1)
        description = request.POST.get('description')
        role = request.POST.get('role')
        AuthTokenModel().create(c.user.user_id, description, lifetime, role)
        Session().commit()
        h.flash(_("Auth token successfully created"), category='success')
        return redirect(url('edit_user_auth_tokens', user_id=c.user.user_id))

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def delete_auth_token(self, user_id):
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        auth_token = request.POST.get('del_auth_token')
        if request.POST.get('del_auth_token_builtin'):
            user = User.get(c.user.user_id)
            if user:
                user.api_key = generate_auth_token(user.username)
                Session().add(user)
                Session().commit()
                h.flash(_("Auth token successfully reset"), category='success')
        elif auth_token:
            AuthTokenModel().delete(auth_token, c.user.user_id)
            Session().commit()
            h.flash(_("Auth token successfully deleted"), category='success')

        return redirect(url('edit_user_auth_tokens', user_id=c.user.user_id))

    @HasPermissionAllDecorator('hg.admin')
    def edit_global_perms(self, user_id):
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        c.active = 'global_perms'

        c.default_user = User.get_default_user()
        defaults = c.user.get_dict()
        defaults.update(c.default_user.get_default_perms(suffix='_inherited'))
        defaults.update(c.default_user.get_default_perms())
        defaults.update(c.user.get_default_perms())

        return htmlfill.render(
            render('admin/users/user_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def update_global_perms(self, user_id):
        """PUT /users_perm/user_id: Update an existing item"""
        # url('user_perm', user_id=ID, method='put')
        user_id = safe_int(user_id)
        user = User.get_or_404(user_id)
        c.active = 'global_perms'
        try:
            # first stage that verifies the checkbox
            _form = UserIndividualPermissionsForm()
            form_result = _form.to_python(dict(request.POST))
            inherit_perms = form_result['inherit_default_permissions']
            user.inherit_default_permissions = inherit_perms
            Session().add(user)

            if not inherit_perms:
                # only update the individual ones if we un check the flag
                _form = UserPermissionsForm(
                    [x[0] for x in c.repo_create_choices],
                    [x[0] for x in c.repo_create_on_write_choices],
                    [x[0] for x in c.repo_group_create_choices],
                    [x[0] for x in c.user_group_create_choices],
                    [x[0] for x in c.fork_choices],
                    [x[0] for x in c.inherit_default_permission_choices])()

                form_result = _form.to_python(dict(request.POST))
                form_result.update({'perm_user_id': user.user_id})

                PermissionModel().update_user_permissions(form_result)

            Session().commit()
            h.flash(_('User global permissions updated successfully'),
                    category='success')

            Session().commit()
        except formencode.Invalid as errors:
            defaults = errors.value
            c.user = user
            return htmlfill.render(
                render('admin/users/user_edit.html'),
                defaults=defaults,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception during permissions saving")
            h.flash(_('An error occurred during permissions saving'),
                    category='error')
        return redirect(url('edit_user_global_perms', user_id=user_id))

    @HasPermissionAllDecorator('hg.admin')
    def edit_perms_summary(self, user_id):
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        c.active = 'perms_summary'
        c.perm_user = AuthUser(user_id=user_id, ip_addr=self.ip_addr)

        return render('admin/users/user_edit.html')

    @HasPermissionAllDecorator('hg.admin')
    def edit_emails(self, user_id):
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        c.active = 'emails'
        c.user_email_map = UserEmailMap.query() \
            .filter(UserEmailMap.user == c.user).all()

        defaults = c.user.get_dict()
        return htmlfill.render(
            render('admin/users/user_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def add_email(self, user_id):
        """POST /user_emails:Add an existing item"""
        # url('user_emails', user_id=ID, method='put')
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)

        email = request.POST.get('new_email')
        user_model = UserModel()

        try:
            user_model.add_extra_email(user_id, email)
            Session().commit()
            h.flash(_("Added new email address `%s` for user account") % email,
                    category='success')
        except formencode.Invalid as error:
            msg = error.error_dict['email']
            h.flash(msg, category='error')
        except Exception:
            log.exception("Exception during email saving")
            h.flash(_('An error occurred during email saving'),
                    category='error')
        return redirect(url('edit_user_emails', user_id=user_id))

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def delete_email(self, user_id):
        """DELETE /user_emails_delete/user_id: Delete an existing item"""
        # url('user_emails_delete', user_id=ID, method='delete')
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        email_id = request.POST.get('del_email_id')
        user_model = UserModel()
        user_model.delete_extra_email(user_id, email_id)
        Session().commit()
        h.flash(_("Removed email address from user account"), category='success')
        return redirect(url('edit_user_emails', user_id=user_id))

    @HasPermissionAllDecorator('hg.admin')
    def edit_ips(self, user_id):
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        if c.user.username == User.DEFAULT_USER:
            h.flash(_("You can't edit this user"), category='warning')
            return redirect(url('users'))

        c.active = 'ips'
        c.user_ip_map = UserIpMap.query() \
            .filter(UserIpMap.user == c.user).all()

        c.inherit_default_ips = c.user.inherit_default_permissions
        c.default_user_ip_map = UserIpMap.query() \
            .filter(UserIpMap.user == User.get_default_user()).all()

        defaults = c.user.get_dict()
        return htmlfill.render(
            render('admin/users/user_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def add_ip(self, user_id):
        """POST /user_ips:Add an existing item"""
        # url('user_ips', user_id=ID, method='put')

        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)
        user_model = UserModel()
        try:
            ip_list = user_model.parse_ip_range(request.POST.get('new_ip'))
        except Exception as e:
            ip_list = []
            log.exception("Exception during ip saving")
            h.flash(_('An error occurred during ip saving:%s' % (e,)),
                    category='error')

        desc = request.POST.get('description')
        added = []
        for ip in ip_list:
            try:
                user_model.add_extra_ip(user_id, ip, desc)
                Session().commit()
                added.append(ip)
            except formencode.Invalid as error:
                msg = error.error_dict['ip']
                h.flash(msg, category='error')
            except Exception:
                log.exception("Exception during ip saving")
                h.flash(_('An error occurred during ip saving'),
                        category='error')
        if added:
            h.flash(
                _("Added ips %s to user whitelist") % (', '.join(ip_list), ),
                category='success')
        if 'default_user' in request.POST:
            return redirect(url('admin_permissions_ips'))
        return redirect(url('edit_user_ips', user_id=user_id))

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def delete_ip(self, user_id):
        """DELETE /user_ips_delete/user_id: Delete an existing item"""
        # url('user_ips_delete', user_id=ID, method='delete')
        user_id = safe_int(user_id)
        c.user = User.get_or_404(user_id)

        ip_id = request.POST.get('del_ip_id')
        user_model = UserModel()
        user_model.delete_extra_ip(user_id, ip_id)
        Session().commit()
        h.flash(_("Removed ip address from user whitelist"), category='success')

        if 'default_user' in request.POST:
            return redirect(url('admin_permissions_ips'))
        return redirect(url('edit_user_ips', user_id=user_id))
