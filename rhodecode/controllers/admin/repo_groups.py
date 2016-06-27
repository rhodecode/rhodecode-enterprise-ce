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
Repository groups controller for RhodeCode
"""

import logging
import formencode

from formencode import htmlfill

from pylons import request, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.i18n.translation import _, ungettext

from rhodecode.lib import auth
from rhodecode.lib import helpers as h
from rhodecode.lib.ext_json import json
from rhodecode.lib.auth import (
    LoginRequired, NotAnonymous, HasPermissionAll,
    HasRepoGroupPermissionAll, HasRepoGroupPermissionAnyDecorator)
from rhodecode.lib.base import BaseController, render
from rhodecode.model.db import RepoGroup, User
from rhodecode.model.scm import RepoGroupList
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.forms import RepoGroupForm, RepoGroupPermsForm
from rhodecode.model.meta import Session
from rhodecode.lib.utils2 import safe_int


log = logging.getLogger(__name__)


class RepoGroupsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""

    @LoginRequired()
    def __before__(self):
        super(RepoGroupsController, self).__before__()

    def __load_defaults(self, allow_empty_group=False, repo_group=None):
        if self._can_create_repo_group():
            # we're global admin, we're ok and we can create TOP level groups
            allow_empty_group = True

        # override the choices for this form, we need to filter choices
        # and display only those we have ADMIN right
        groups_with_admin_rights = RepoGroupList(
            RepoGroup.query().all(),
            perm_set=['group.admin'])
        c.repo_groups = RepoGroup.groups_choices(
            groups=groups_with_admin_rights,
            show_empty_group=allow_empty_group)

        if repo_group:
            # exclude filtered ids
            exclude_group_ids = [repo_group.group_id]
            c.repo_groups = filter(lambda x: x[0] not in exclude_group_ids,
                                   c.repo_groups)
            c.repo_groups_choices = map(lambda k: unicode(k[0]), c.repo_groups)
            parent_group = repo_group.parent_group

            add_parent_group = (parent_group and (
                unicode(parent_group.group_id) not in c.repo_groups_choices))
            if add_parent_group:
                c.repo_groups_choices.append(unicode(parent_group.group_id))
                c.repo_groups.append(RepoGroup._generate_choice(parent_group))

    def __load_data(self, group_id):
        """
        Load defaults settings for edit, and update

        :param group_id:
        """
        repo_group = RepoGroup.get_or_404(group_id)
        data = repo_group.get_dict()
        data['group_name'] = repo_group.name

        # fill owner
        if repo_group.user:
            data.update({'user': repo_group.user.username})
        else:
            replacement_user = User.get_first_super_admin().username
            data.update({'user': replacement_user})

        # fill repository group users
        for p in repo_group.repo_group_to_perm:
            data.update({
                'u_perm_%s' % p.user.user_id: p.permission.permission_name})

        # fill repository group user groups
        for p in repo_group.users_group_to_perm:
            data.update({
                'g_perm_%s' % p.users_group.users_group_id:
                p.permission.permission_name})
        # html and form expects -1 as empty parent group
        data['group_parent_id'] = data['group_parent_id'] or -1
        return data

    def _revoke_perms_on_yourself(self, form_result):
        _updates = filter(lambda u: c.rhodecode_user.user_id == int(u[0]),
                          form_result['perm_updates'])
        _additions = filter(lambda u: c.rhodecode_user.user_id == int(u[0]),
                            form_result['perm_additions'])
        _deletions = filter(lambda u: c.rhodecode_user.user_id == int(u[0]),
                            form_result['perm_deletions'])
        admin_perm = 'group.admin'
        if _updates and _updates[0][1] != admin_perm or \
           _additions and _additions[0][1] != admin_perm or \
           _deletions and _deletions[0][1] != admin_perm:
            return True
        return False

    def _can_create_repo_group(self, parent_group_id=None):
        is_admin = HasPermissionAll('hg.admin')('group create controller')
        create_repo_group = HasPermissionAll(
            'hg.repogroup.create.true')('group create controller')
        if is_admin or (create_repo_group and not parent_group_id):
            # we're global admin, or we have global repo group create
            # permission
            # we're ok and we can create TOP level groups
            return True
        elif parent_group_id:
            # we check the permission if we can write to parent group
            group = RepoGroup.get(parent_group_id)
            group_name = group.group_name if group else None
            if HasRepoGroupPermissionAll('group.admin')(
                    group_name, 'check if user is an admin of group'):
                # we're an admin of passed in group, we're ok.
                return True
            else:
                return False
        return False

    @NotAnonymous()
    def index(self):
        """GET /repo_groups: All items in the collection"""
        # url('repo_groups')

        repo_group_list = RepoGroup.get_all_repo_groups()
        _perms = ['group.admin']
        repo_group_list_acl = RepoGroupList(repo_group_list, perm_set=_perms)
        repo_group_data = RepoGroupModel().get_repo_groups_as_dict(
            repo_group_list=repo_group_list_acl, admin=True)
        c.data = json.dumps(repo_group_data)
        return render('admin/repo_groups/repo_groups.html')

    # perm checks inside
    @NotAnonymous()
    @auth.CSRFRequired()
    def create(self):
        """POST /repo_groups: Create a new item"""
        # url('repo_groups')

        parent_group_id = safe_int(request.POST.get('group_parent_id'))
        can_create = self._can_create_repo_group(parent_group_id)

        self.__load_defaults()
        # permissions for can create group based on parent_id are checked
        # here in the Form
        available_groups = map(lambda k: unicode(k[0]), c.repo_groups)
        repo_group_form = RepoGroupForm(available_groups=available_groups,
                                        can_create_in_root=can_create)()
        try:
            owner = c.rhodecode_user
            form_result = repo_group_form.to_python(dict(request.POST))
            RepoGroupModel().create(
                group_name=form_result['group_name_full'],
                group_description=form_result['group_description'],
                owner=owner.user_id,
                copy_permissions=form_result['group_copy_permissions']
            )
            Session().commit()
            _new_group_name = form_result['group_name_full']
            repo_group_url = h.link_to(
                _new_group_name,
                h.url('repo_group_home', group_name=_new_group_name))
            h.flash(h.literal(_('Created repository group %s')
                    % repo_group_url), category='success')
            # TODO: in futureaction_logger(, '', '', '', self.sa)
        except formencode.Invalid as errors:
            return htmlfill.render(
                render('admin/repo_groups/repo_group_add.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception during creation of repository group")
            h.flash(_('Error occurred during creation of repository group %s')
                    % request.POST.get('group_name'), category='error')

        # TODO: maybe we should get back to the main view, not the admin one
        return redirect(url('repo_groups', parent_group=parent_group_id))

    # perm checks inside
    @NotAnonymous()
    def new(self):
        """GET /repo_groups/new: Form to create a new item"""
        # url('new_repo_group')
        # perm check for admin, create_group perm or admin of parent_group
        parent_group_id = safe_int(request.GET.get('parent_group'))
        if not self._can_create_repo_group(parent_group_id):
            return abort(403)

        self.__load_defaults()
        return render('admin/repo_groups/repo_group_add.html')

    @HasRepoGroupPermissionAnyDecorator('group.admin')
    @auth.CSRFRequired()
    def update(self, group_name):
        """PUT /repo_groups/group_name: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('repos_group', group_name=GROUP_NAME), method='put')
        # url('repo_group_home', group_name=GROUP_NAME)

        c.repo_group = RepoGroupModel()._get_repo_group(group_name)
        can_create_in_root = self._can_create_repo_group()
        show_root_location = can_create_in_root
        if not c.repo_group.parent_group:
            # this group don't have a parrent so we should show empty value
            show_root_location = True
        self.__load_defaults(allow_empty_group=show_root_location,
                             repo_group=c.repo_group)

        repo_group_form = RepoGroupForm(
            edit=True, old_data=c.repo_group.get_dict(),
            available_groups=c.repo_groups_choices,
            can_create_in_root=can_create_in_root, allow_disabled=True)()

        try:
            form_result = repo_group_form.to_python(dict(request.POST))
            gr_name = form_result['group_name']
            new_gr = RepoGroupModel().update(group_name, form_result)
            Session().commit()
            h.flash(_('Updated repository group %s') % (gr_name,),
                    category='success')
            # we now have new name !
            group_name = new_gr.group_name
            # TODO: in future action_logger(, '', '', '', self.sa)
        except formencode.Invalid as errors:
            c.active = 'settings'
            return htmlfill.render(
                render('admin/repo_groups/repo_group_edit.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception during update or repository group")
            h.flash(_('Error occurred during update of repository group %s')
                    % request.POST.get('group_name'), category='error')

        return redirect(url('edit_repo_group', group_name=group_name))

    @HasRepoGroupPermissionAnyDecorator('group.admin')
    @auth.CSRFRequired()
    def delete(self, group_name):
        """DELETE /repo_groups/group_name: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('repos_group', group_name=GROUP_NAME), method='delete')
        # url('repo_group_home', group_name=GROUP_NAME)

        gr = c.repo_group = RepoGroupModel()._get_repo_group(group_name)
        repos = gr.repositories.all()
        if repos:
            msg = ungettext(
                'This group contains %(num)d repository and cannot be deleted',
                'This group contains %(num)d repositories and cannot be'
                ' deleted',
                len(repos)) % {'num': len(repos)}
            h.flash(msg, category='warning')
            return redirect(url('repo_groups'))

        children = gr.children.all()
        if children:
            msg = ungettext(
                'This group contains %(num)d subgroup and cannot be deleted',
                'This group contains %(num)d subgroups and cannot be deleted',
                len(children)) % {'num': len(children)}
            h.flash(msg, category='warning')
            return redirect(url('repo_groups'))

        try:
            RepoGroupModel().delete(group_name)
            Session().commit()
            h.flash(_('Removed repository group %s') % group_name,
                    category='success')
            # TODO: in future action_logger(, '', '', '', self.sa)
        except Exception:
            log.exception("Exception during deletion of repository group")
            h.flash(_('Error occurred during deletion of repository group %s')
                    % group_name, category='error')

        return redirect(url('repo_groups'))

    @HasRepoGroupPermissionAnyDecorator('group.admin')
    def edit(self, group_name):
        """GET /repo_groups/group_name/edit: Form to edit an existing item"""
        # url('edit_repo_group', group_name=GROUP_NAME)
        c.active = 'settings'

        c.repo_group = RepoGroupModel()._get_repo_group(group_name)
        # we can only allow moving empty group if it's already a top-level
        # group, ie has no parents, or we're admin
        can_create_in_root = self._can_create_repo_group()
        show_root_location = can_create_in_root
        if not c.repo_group.parent_group:
            # this group don't have a parrent so we should show empty value
            show_root_location = True
        self.__load_defaults(allow_empty_group=show_root_location,
                             repo_group=c.repo_group)
        defaults = self.__load_data(c.repo_group.group_id)

        return htmlfill.render(
            render('admin/repo_groups/repo_group_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @HasRepoGroupPermissionAnyDecorator('group.admin')
    def edit_repo_group_advanced(self, group_name):
        """GET /repo_groups/group_name/edit: Form to edit an existing item"""
        # url('edit_repo_group', group_name=GROUP_NAME)
        c.active = 'advanced'
        c.repo_group = RepoGroupModel()._get_repo_group(group_name)

        return render('admin/repo_groups/repo_group_edit.html')

    @HasRepoGroupPermissionAnyDecorator('group.admin')
    def edit_repo_group_perms(self, group_name):
        """GET /repo_groups/group_name/edit: Form to edit an existing item"""
        # url('edit_repo_group', group_name=GROUP_NAME)
        c.active = 'perms'
        c.repo_group = RepoGroupModel()._get_repo_group(group_name)
        self.__load_defaults()
        defaults = self.__load_data(c.repo_group.group_id)

        return htmlfill.render(
            render('admin/repo_groups/repo_group_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @HasRepoGroupPermissionAnyDecorator('group.admin')
    @auth.CSRFRequired()
    def update_perms(self, group_name):
        """
        Update permissions for given repository group

        :param group_name:
        """

        c.repo_group = RepoGroupModel()._get_repo_group(group_name)
        valid_recursive_choices = ['none', 'repos', 'groups', 'all']
        form = RepoGroupPermsForm(valid_recursive_choices)().to_python(
            request.POST)

        if not c.rhodecode_user.is_admin:
            if self._revoke_perms_on_yourself(form):
                msg = _('Cannot change permission for yourself as admin')
                h.flash(msg, category='warning')
                return redirect(
                    url('edit_repo_group_perms', group_name=group_name))

        # iterate over all members(if in recursive mode) of this groups and
        # set the permissions !
        # this can be potentially heavy operation
        RepoGroupModel().update_permissions(
            c.repo_group,
            form['perm_additions'], form['perm_updates'],
            form['perm_deletions'], form['recursive'])

        # TODO: implement this
        # action_logger(c.rhodecode_user, 'admin_changed_repo_permissions',
        #               repo_name, self.ip_addr, self.sa)
        Session().commit()
        h.flash(_('Repository Group permissions updated'), category='success')
        return redirect(url('edit_repo_group_perms', group_name=group_name))
