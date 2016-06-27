# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016  RhodeCode GmbH
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
User Groups crud controller for pylons
"""

import logging
import formencode

from formencode import htmlfill
from pylons import request, tmpl_context as c, url, config
from pylons.controllers.util import redirect
from pylons.i18n.translation import _

from sqlalchemy.orm import joinedload

from rhodecode.lib import auth
from rhodecode.lib import helpers as h
from rhodecode.lib.exceptions import UserGroupAssignedException,\
    RepoGroupAssignmentError
from rhodecode.lib.utils import jsonify, action_logger
from rhodecode.lib.utils2 import safe_unicode, str2bool, safe_int
from rhodecode.lib.auth import (
    LoginRequired, NotAnonymous, HasUserGroupPermissionAnyDecorator,
    HasPermissionAnyDecorator)
from rhodecode.lib.base import BaseController, render
from rhodecode.model.permission import PermissionModel
from rhodecode.model.scm import UserGroupList
from rhodecode.model.user_group import UserGroupModel
from rhodecode.model.db import (
    User, UserGroup, UserGroupRepoToPerm, UserGroupRepoGroupToPerm)
from rhodecode.model.forms import (
    UserGroupForm, UserGroupPermsForm, UserIndividualPermissionsForm,
    UserPermissionsForm)
from rhodecode.model.meta import Session
from rhodecode.lib.utils import action_logger
from rhodecode.lib.ext_json import json

log = logging.getLogger(__name__)


class UserGroupsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""

    @LoginRequired()
    def __before__(self):
        super(UserGroupsController, self).__before__()
        c.available_permissions = config['available_permissions']
        PermissionModel().set_global_permission_choices(c, translator=_)

    def __load_data(self, user_group_id):
        c.group_members_obj = [x.user for x in c.user_group.members]
        c.group_members_obj.sort(key=lambda u: u.username.lower())

        c.group_members = [(x.user_id, x.username) for x in c.group_members_obj]

        c.available_members = [(x.user_id, x.username)
                               for x in User.query().all()]
        c.available_members.sort(key=lambda u: u[1].lower())

    def __load_defaults(self, user_group_id):
        """
        Load defaults settings for edit, and update

        :param user_group_id:
        """
        user_group = UserGroup.get_or_404(user_group_id)
        data = user_group.get_dict()
        # fill owner
        if user_group.user:
            data.update({'user': user_group.user.username})
        else:
            replacement_user = User.get_first_super_admin().username
            data.update({'user': replacement_user})
        return data

    def _revoke_perms_on_yourself(self, form_result):
        _updates = filter(lambda u: c.rhodecode_user.user_id == int(u[0]),
                          form_result['perm_updates'])
        _additions = filter(lambda u: c.rhodecode_user.user_id == int(u[0]),
                            form_result['perm_additions'])
        _deletions = filter(lambda u: c.rhodecode_user.user_id == int(u[0]),
                            form_result['perm_deletions'])
        admin_perm = 'usergroup.admin'
        if _updates   and _updates[0][1]   != admin_perm or \
           _additions and _additions[0][1] != admin_perm or \
           _deletions and _deletions[0][1] != admin_perm:
            return True
        return False

    # permission check inside
    @NotAnonymous()
    def index(self):
        """GET /users_groups: All items in the collection"""
        # url('users_groups')

        from rhodecode.lib.utils import PartialRenderer
        _render = PartialRenderer('data_table/_dt_elements.html')

        def user_group_name(user_group_id, user_group_name):
            return _render("user_group_name", user_group_id, user_group_name)

        def user_group_actions(user_group_id, user_group_name):
            return _render("user_group_actions", user_group_id, user_group_name)

        ## json generate
        group_iter = UserGroupList(UserGroup.query().all(),
                                   perm_set=['usergroup.admin'])

        user_groups_data = []
        for user_gr in group_iter:
            user_groups_data.append({
                "group_name": user_group_name(
                    user_gr.users_group_id, h.escape(user_gr.users_group_name)),
                "group_name_raw": user_gr.users_group_name,
                "desc": h.escape(user_gr.user_group_description),
                "members": len(user_gr.members),
                "active": h.bool2icon(user_gr.users_group_active),
                "owner": h.escape(h.link_to_user(user_gr.user.username)),
                "action": user_group_actions(
                    user_gr.users_group_id, user_gr.users_group_name)
            })

        c.data = json.dumps(user_groups_data)
        return render('admin/user_groups/user_groups.html')

    @HasPermissionAnyDecorator('hg.admin', 'hg.usergroup.create.true')
    @auth.CSRFRequired()
    def create(self):
        """POST /users_groups: Create a new item"""
        # url('users_groups')

        users_group_form = UserGroupForm()()
        try:
            form_result = users_group_form.to_python(dict(request.POST))
            user_group = UserGroupModel().create(
                name=form_result['users_group_name'],
                description=form_result['user_group_description'],
                owner=c.rhodecode_user.user_id,
                active=form_result['users_group_active'])
            Session().flush()

            user_group_name = form_result['users_group_name']
            action_logger(c.rhodecode_user,
                          'admin_created_users_group:%s' % user_group_name,
                          None, self.ip_addr, self.sa)
            user_group_link = h.link_to(h.escape(user_group_name),
                                        url('edit_users_group',
                                            user_group_id=user_group.users_group_id))
            h.flash(h.literal(_('Created user group %(user_group_link)s')
                              % {'user_group_link': user_group_link}),
                    category='success')
            Session().commit()
        except formencode.Invalid as errors:
            return htmlfill.render(
                render('admin/user_groups/user_group_add.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception creating user group")
            h.flash(_('Error occurred during creation of user group %s') \
                    % request.POST.get('users_group_name'), category='error')

        return redirect(
            url('edit_users_group', user_group_id=user_group.users_group_id))

    @HasPermissionAnyDecorator('hg.admin', 'hg.usergroup.create.true')
    def new(self):
        """GET /user_groups/new: Form to create a new item"""
        # url('new_users_group')
        return render('admin/user_groups/user_group_add.html')

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    @auth.CSRFRequired()
    def update(self, user_group_id):
        """PUT /user_groups/user_group_id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('users_group', user_group_id=ID),
        #           method='put')
        # url('users_group', user_group_id=ID)

        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'settings'
        self.__load_data(user_group_id)

        available_members = [safe_unicode(x[0]) for x in c.available_members]

        users_group_form = UserGroupForm(
            edit=True, old_data=c.user_group.get_dict(),
            available_members=available_members, allow_disabled=True)()

        try:
            form_result = users_group_form.to_python(request.POST)
            UserGroupModel().update(c.user_group, form_result)
            gr = form_result['users_group_name']
            action_logger(c.rhodecode_user,
                          'admin_updated_users_group:%s' % gr,
                          None, self.ip_addr, self.sa)
            h.flash(_('Updated user group %s') % gr, category='success')
            Session().commit()
        except formencode.Invalid as errors:
            defaults = errors.value
            e = errors.error_dict or {}

            return htmlfill.render(
                render('admin/user_groups/user_group_edit.html'),
                defaults=defaults,
                errors=e,
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception during update of user group")
            h.flash(_('Error occurred during update of user group %s')
                    % request.POST.get('users_group_name'), category='error')

        return redirect(url('edit_users_group', user_group_id=user_group_id))

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    @auth.CSRFRequired()
    def delete(self, user_group_id):
        """DELETE /user_groups/user_group_id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('users_group', user_group_id=ID),
        #           method='delete')
        # url('users_group', user_group_id=ID)
        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        force = str2bool(request.POST.get('force'))

        try:
            UserGroupModel().delete(c.user_group, force=force)
            Session().commit()
            h.flash(_('Successfully deleted user group'), category='success')
        except UserGroupAssignedException as e:
            h.flash(str(e), category='error')
        except Exception:
            log.exception("Exception during deletion of user group")
            h.flash(_('An error occurred during deletion of user group'),
                    category='error')
        return redirect(url('users_groups'))

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    def edit(self, user_group_id):
        """GET /user_groups/user_group_id/edit: Form to edit an existing item"""
        # url('edit_users_group', user_group_id=ID)

        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'settings'
        self.__load_data(user_group_id)

        defaults = self.__load_defaults(user_group_id)

        return htmlfill.render(
            render('admin/user_groups/user_group_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    def edit_perms(self, user_group_id):
        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'perms'

        defaults = {}
        # fill user group users
        for p in c.user_group.user_user_group_to_perm:
            defaults.update({'u_perm_%s' % p.user.user_id:
                             p.permission.permission_name})

        for p in c.user_group.user_group_user_group_to_perm:
            defaults.update({'g_perm_%s' % p.user_group.users_group_id:
                             p.permission.permission_name})

        return htmlfill.render(
            render('admin/user_groups/user_group_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    @auth.CSRFRequired()
    def update_perms(self, user_group_id):
        """
        grant permission for given usergroup

        :param user_group_id:
        """
        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        form = UserGroupPermsForm()().to_python(request.POST)

        if not c.rhodecode_user.is_admin:
            if self._revoke_perms_on_yourself(form):
                msg = _('Cannot change permission for yourself as admin')
                h.flash(msg, category='warning')
                return redirect(url('edit_user_group_perms', user_group_id=user_group_id))

        try:
            UserGroupModel().update_permissions(user_group_id,
                form['perm_additions'], form['perm_updates'], form['perm_deletions'])
        except RepoGroupAssignmentError:
            h.flash(_('Target group cannot be the same'), category='error')
            return redirect(url('edit_user_group_perms', user_group_id=user_group_id))
        #TODO: implement this
        #action_logger(c.rhodecode_user, 'admin_changed_repo_permissions',
        #              repo_name, self.ip_addr, self.sa)
        Session().commit()
        h.flash(_('User Group permissions updated'), category='success')
        return redirect(url('edit_user_group_perms', user_group_id=user_group_id))

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    def edit_perms_summary(self, user_group_id):
        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'perms_summary'
        permissions = {
            'repositories': {},
            'repositories_groups': {},
        }
        ugroup_repo_perms = UserGroupRepoToPerm.query()\
            .options(joinedload(UserGroupRepoToPerm.permission))\
            .options(joinedload(UserGroupRepoToPerm.repository))\
            .filter(UserGroupRepoToPerm.users_group_id == user_group_id)\
            .all()

        for gr in ugroup_repo_perms:
            permissions['repositories'][gr.repository.repo_name]  \
                = gr.permission.permission_name

        ugroup_group_perms = UserGroupRepoGroupToPerm.query()\
            .options(joinedload(UserGroupRepoGroupToPerm.permission))\
            .options(joinedload(UserGroupRepoGroupToPerm.group))\
            .filter(UserGroupRepoGroupToPerm.users_group_id == user_group_id)\
            .all()

        for gr in ugroup_group_perms:
            permissions['repositories_groups'][gr.group.group_name] \
                = gr.permission.permission_name
        c.permissions = permissions
        return render('admin/user_groups/user_group_edit.html')

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    def edit_global_perms(self, user_group_id):
        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'global_perms'

        c.default_user = User.get_default_user()
        defaults = c.user_group.get_dict()
        defaults.update(c.default_user.get_default_perms(suffix='_inherited'))
        defaults.update(c.user_group.get_default_perms())

        return htmlfill.render(
            render('admin/user_groups/user_group_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    @auth.CSRFRequired()
    def update_global_perms(self, user_group_id):
        """PUT /users_perm/user_group_id: Update an existing item"""
        # url('users_group_perm', user_group_id=ID, method='put')
        user_group_id = safe_int(user_group_id)
        user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'global_perms'

        try:
            # first stage that verifies the checkbox
            _form = UserIndividualPermissionsForm()
            form_result = _form.to_python(dict(request.POST))
            inherit_perms = form_result['inherit_default_permissions']
            user_group.inherit_default_permissions = inherit_perms
            Session().add(user_group)

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
                form_result.update({'perm_user_group_id': user_group.users_group_id})

                PermissionModel().update_user_group_permissions(form_result)

            Session().commit()
            h.flash(_('User Group global permissions updated successfully'),
                    category='success')

        except formencode.Invalid as errors:
            defaults = errors.value
            c.user_group = user_group
            return htmlfill.render(
                render('admin/user_groups/user_group_edit.html'),
                defaults=defaults,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)

        except Exception:
            log.exception("Exception during permissions saving")
            h.flash(_('An error occurred during permissions saving'),
                    category='error')

        return redirect(url('edit_user_group_global_perms', user_group_id=user_group_id))

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    def edit_advanced(self, user_group_id):
        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'advanced'
        c.group_members_obj = sorted(
            (x.user for x in c.user_group.members),
            key=lambda u: u.username.lower())

        c.group_to_repos = sorted(
            (x.repository for x in c.user_group.users_group_repo_to_perm),
            key=lambda u: u.repo_name.lower())

        c.group_to_repo_groups = sorted(
            (x.group for x in c.user_group.users_group_repo_group_to_perm),
            key=lambda u: u.group_name.lower())

        return render('admin/user_groups/user_group_edit.html')

    @HasUserGroupPermissionAnyDecorator('usergroup.admin')
    def edit_members(self, user_group_id):
        user_group_id = safe_int(user_group_id)
        c.user_group = UserGroup.get_or_404(user_group_id)
        c.active = 'members'
        c.group_members_obj = sorted((x.user for x in c.user_group.members),
                                     key=lambda u: u.username.lower())

        group_members = [(x.user_id, x.username) for x in c.group_members_obj]

        if request.is_xhr:
            return jsonify(lambda *a, **k: {
                'members': group_members
            })

        c.group_members = group_members
        return render('admin/user_groups/user_group_edit.html')
