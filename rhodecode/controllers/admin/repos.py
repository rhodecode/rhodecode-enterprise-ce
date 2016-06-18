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
Repositories controller for RhodeCode
"""

import logging
import traceback

import formencode
from formencode import htmlfill
from pylons import request, tmpl_context as c, url
from pylons.controllers.util import redirect
from pylons.i18n.translation import _
from webob.exc import HTTPForbidden, HTTPNotFound, HTTPBadRequest

from rhodecode.lib import auth, helpers as h
from rhodecode.lib.auth import (
    LoginRequired, HasPermissionAllDecorator,
    HasRepoPermissionAllDecorator, NotAnonymous, HasPermissionAny,
    HasRepoGroupPermissionAny, HasRepoPermissionAnyDecorator)
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.ext_json import json
from rhodecode.lib.exceptions import AttachedForksError
from rhodecode.lib.utils import action_logger, repo_name_slug, jsonify
from rhodecode.lib.utils2 import safe_int
from rhodecode.lib.vcs import RepositoryError
from rhodecode.model.db import (
    User, Repository, UserFollowing, RepoGroup, RepositoryField)
from rhodecode.model.forms import (
    RepoForm, RepoFieldForm, RepoPermsForm, RepoVcsSettingsForm,
    IssueTrackerPatternsForm)
from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel
from rhodecode.model.scm import ScmModel, RepoGroupList, RepoList
from rhodecode.model.settings import (
    SettingsModel, IssueTrackerSettingsModel, VcsSettingsModel,
    SettingNotFound)

log = logging.getLogger(__name__)


class ReposController(BaseRepoController):
    """
    REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('repo', 'repos')

    @LoginRequired()
    def __before__(self):
        super(ReposController, self).__before__()

    def _load_repo(self, repo_name):
        repo_obj = Repository.get_by_repo_name(repo_name)

        if repo_obj is None:
            h.not_mapped_error(repo_name)
            return redirect(url('repos'))

        return repo_obj

    def __load_defaults(self, repo=None):
        acl_groups = RepoGroupList(RepoGroup.query().all(),
                               perm_set=['group.write', 'group.admin'])
        c.repo_groups = RepoGroup.groups_choices(groups=acl_groups)
        c.repo_groups_choices = map(lambda k: unicode(k[0]), c.repo_groups)

        # in case someone no longer have a group.write access to a repository
        # pre fill the list with this entry, we don't care if this is the same
        # but it will allow saving repo data properly.

        repo_group = None
        if repo:
            repo_group = repo.group
        if repo_group and unicode(repo_group.group_id) not in c.repo_groups_choices:
            c.repo_groups_choices.append(unicode(repo_group.group_id))
            c.repo_groups.append(RepoGroup._generate_choice(repo_group))

        choices, c.landing_revs = ScmModel().get_repo_landing_revs()
        c.landing_revs_choices = choices

    def __load_data(self, repo_name=None):
        """
        Load defaults settings for edit, and update

        :param repo_name:
        """
        c.repo_info = self._load_repo(repo_name)
        self.__load_defaults(c.repo_info)

        # override defaults for exact repo info here git/hg etc
        if not c.repository_requirements_missing:
            choices, c.landing_revs = ScmModel().get_repo_landing_revs(
                c.repo_info)
            c.landing_revs_choices = choices
        defaults = RepoModel()._get_defaults(repo_name)

        return defaults

    def _log_creation_exception(self, e, repo_name):
            reason = None
            if len(e.args) == 2:
                reason = e.args[1]

            if reason == 'INVALID_CERTIFICATE':
                log.exception(
                    'Exception creating a repository: invalid certificate')
                msg = (_('Error creating repository %s: invalid certificate')
                       % repo_name)
            else:
                log.exception("Exception creating a repository")
                msg = (_('Error creating repository %s')
                       % repo_name)

            return msg

    @NotAnonymous()
    def index(self, format='html'):
        """GET /repos: All items in the collection"""
        # url('repos')

        repo_list = Repository.get_all_repos()
        c.repo_list = RepoList(repo_list, perm_set=['repository.admin'])
        repos_data = RepoModel().get_repos_as_dict(
            repo_list=c.repo_list, admin=True, super_user_actions=True)
        # json used to render the grid
        c.data = json.dumps(repos_data)

        return render('admin/repos/repos.html')

    # perms check inside
    @NotAnonymous()
    @auth.CSRFRequired()
    def create(self):
        """
        POST /repos: Create a new item"""
        # url('repos')

        self.__load_defaults()
        form_result = {}
        task_id = None
        try:
            # CanWriteToGroup validators checks permissions of this POST
            form_result = RepoForm(repo_groups=c.repo_groups_choices,
                                   landing_revs=c.landing_revs_choices)()\
                            .to_python(dict(request.POST))

            # create is done sometimes async on celery, db transaction
            # management is handled there.
            task = RepoModel().create(form_result, c.rhodecode_user.user_id)
            from celery.result import BaseAsyncResult
            if isinstance(task, BaseAsyncResult):
                task_id = task.task_id
        except formencode.Invalid as errors:
            c.personal_repo_group = RepoGroup.get_by_group_name(
                c.rhodecode_user.username)
            return htmlfill.render(
                render('admin/repos/repo_add.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)

        except Exception as e:
            msg = self._log_creation_exception(e, form_result.get('repo_name'))
            h.flash(msg, category='error')
            return redirect(url('home'))

        return redirect(h.url('repo_creating_home',
                              repo_name=form_result['repo_name_full'],
                              task_id=task_id))

    # perms check inside
    @NotAnonymous()
    def create_repository(self):
        """GET /_admin/create_repository: Form to create a new item"""
        new_repo = request.GET.get('repo', '')
        parent_group = request.GET.get('parent_group')
        if not HasPermissionAny('hg.admin', 'hg.create.repository')():
            # you're not super admin nor have global create permissions,
            # but maybe you have at least write permission to a parent group ?
            _gr = RepoGroup.get(parent_group)
            gr_name = _gr.group_name if _gr else None
            # create repositories with write permission on group is set to true
            create_on_write = HasPermissionAny('hg.create.write_on_repogroup.true')()
            group_admin = HasRepoGroupPermissionAny('group.admin')(group_name=gr_name)
            group_write = HasRepoGroupPermissionAny('group.write')(group_name=gr_name)
            if not (group_admin or (group_write and create_on_write)):
                raise HTTPForbidden

        acl_groups = RepoGroupList(RepoGroup.query().all(),
                               perm_set=['group.write', 'group.admin'])
        c.repo_groups = RepoGroup.groups_choices(groups=acl_groups)
        c.repo_groups_choices = map(lambda k: unicode(k[0]), c.repo_groups)
        choices, c.landing_revs = ScmModel().get_repo_landing_revs()
        c.personal_repo_group = RepoGroup.get_by_group_name(c.rhodecode_user.username)
        c.new_repo = repo_name_slug(new_repo)

        ## apply the defaults from defaults page
        defaults = SettingsModel().get_default_repo_settings(strip_prefix=True)
        # set checkbox to autochecked
        defaults['repo_copy_permissions'] = True
        if parent_group:
            defaults.update({'repo_group': parent_group})

        return htmlfill.render(
            render('admin/repos/repo_add.html'),
            defaults=defaults,
            errors={},
            prefix_error=False,
            encoding="UTF-8",
            force_defaults=False
        )

    @NotAnonymous()
    def repo_creating(self, repo_name):
        c.repo = repo_name
        c.task_id = request.GET.get('task_id')
        if not c.repo:
            raise HTTPNotFound()
        return render('admin/repos/repo_creating.html')

    @NotAnonymous()
    @jsonify
    def repo_check(self, repo_name):
        c.repo = repo_name
        task_id = request.GET.get('task_id')

        if task_id and task_id not in ['None']:
            from rhodecode import CELERY_ENABLED
            from celery.result import AsyncResult
            if CELERY_ENABLED:
                task = AsyncResult(task_id)
                if task.failed():
                    msg = self._log_creation_exception(task.result, c.repo)
                    h.flash(msg, category='error')
                    return redirect(url('home'), code=501)

        repo = Repository.get_by_repo_name(repo_name)
        if repo and repo.repo_state == Repository.STATE_CREATED:
            if repo.clone_uri:
                clone_uri = repo.clone_uri_hidden
                h.flash(_('Created repository %s from %s')
                        % (repo.repo_name, clone_uri), category='success')
            else:
                repo_url = h.link_to(repo.repo_name,
                                     h.url('summary_home',
                                           repo_name=repo.repo_name))
                fork = repo.fork
                if fork:
                    fork_name = fork.repo_name
                    h.flash(h.literal(_('Forked repository %s as %s')
                            % (fork_name, repo_url)), category='success')
                else:
                    h.flash(h.literal(_('Created repository %s') % repo_url),
                            category='success')
            return {'result': True}
        return {'result': False}

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def update(self, repo_name):
        """
        PUT /repos/repo_name: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('repo', repo_name=ID),
        #           method='put')
        # url('repo', repo_name=ID)

        self.__load_data(repo_name)
        c.active = 'settings'
        c.repo_fields = RepositoryField.query()\
            .filter(RepositoryField.repository == c.repo_info).all()

        repo_model = RepoModel()
        changed_name = repo_name

        # override the choices with extracted revisions !
        c.personal_repo_group = RepoGroup.get_by_group_name(
            c.rhodecode_user.username)
        repo = Repository.get_by_repo_name(repo_name)
        old_data = {
            'repo_name': repo_name,
            'repo_group': repo.group.get_dict() if repo.group else {},
            'repo_type': repo.repo_type,
        }
        _form = RepoForm(
            edit=True, old_data=old_data, repo_groups=c.repo_groups_choices,
            landing_revs=c.landing_revs_choices, allow_disabled=True)()

        try:
            form_result = _form.to_python(dict(request.POST))
            repo = repo_model.update(repo_name, **form_result)
            ScmModel().mark_for_invalidation(repo_name)
            h.flash(_('Repository %s updated successfully') % repo_name,
                    category='success')
            changed_name = repo.repo_name
            action_logger(c.rhodecode_user, 'admin_updated_repo',
                              changed_name, self.ip_addr, self.sa)
            Session().commit()
        except formencode.Invalid as errors:
            defaults = self.__load_data(repo_name)
            defaults.update(errors.value)
            return htmlfill.render(
                render('admin/repos/repo_edit.html'),
                defaults=defaults,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)

        except Exception:
            log.exception("Exception during update of repository")
            h.flash(_('Error occurred during update of repository %s') \
                    % repo_name, category='error')
        return redirect(url('edit_repo', repo_name=changed_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def delete(self, repo_name):
        """
        DELETE /repos/repo_name: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('repo', repo_name=ID),
        #           method='delete')
        # url('repo', repo_name=ID)

        repo_model = RepoModel()
        repo = repo_model.get_by_repo_name(repo_name)
        if not repo:
            h.not_mapped_error(repo_name)
            return redirect(url('repos'))
        try:
            _forks = repo.forks.count()
            handle_forks = None
            if _forks and request.POST.get('forks'):
                do = request.POST['forks']
                if do == 'detach_forks':
                    handle_forks = 'detach'
                    h.flash(_('Detached %s forks') % _forks, category='success')
                elif do == 'delete_forks':
                    handle_forks = 'delete'
                    h.flash(_('Deleted %s forks') % _forks, category='success')
            repo_model.delete(repo, forks=handle_forks)
            action_logger(c.rhodecode_user, 'admin_deleted_repo',
                  repo_name, self.ip_addr, self.sa)
            ScmModel().mark_for_invalidation(repo_name)
            h.flash(_('Deleted repository %s') % repo_name, category='success')
            Session().commit()
        except AttachedForksError:
            h.flash(_('Cannot delete %s it still contains attached forks')
                        % repo_name, category='warning')

        except Exception:
            log.exception("Exception during deletion of repository")
            h.flash(_('An error occurred during deletion of %s') % repo_name,
                    category='error')

        return redirect(url('repos'))

    @HasPermissionAllDecorator('hg.admin')
    def show(self, repo_name, format='html'):
        """GET /repos/repo_name: Show a specific item"""
        # url('repo', repo_name=ID)

    @HasRepoPermissionAllDecorator('repository.admin')
    def edit(self, repo_name):
        """GET /repo_name/settings: Form to edit an existing item"""
        # url('edit_repo', repo_name=ID)
        defaults = self.__load_data(repo_name)
        if 'clone_uri' in defaults:
            del defaults['clone_uri']

        c.repo_fields = RepositoryField.query()\
            .filter(RepositoryField.repository == c.repo_info).all()
        c.personal_repo_group = RepoGroup.get_by_group_name(
            c.rhodecode_user.username)
        c.active = 'settings'
        return htmlfill.render(
            render('admin/repos/repo_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasRepoPermissionAllDecorator('repository.admin')
    def edit_permissions(self, repo_name):
        """GET /repo_name/settings: Form to edit an existing item"""
        # url('edit_repo', repo_name=ID)
        c.repo_info = self._load_repo(repo_name)
        c.active = 'permissions'
        defaults = RepoModel()._get_defaults(repo_name)

        return htmlfill.render(
            render('admin/repos/repo_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def edit_permissions_update(self, repo_name):
        form = RepoPermsForm()().to_python(request.POST)
        RepoModel().update_permissions(repo_name,
            form['perm_additions'], form['perm_updates'], form['perm_deletions'])

        #TODO: implement this
        #action_logger(c.rhodecode_user, 'admin_changed_repo_permissions',
        #              repo_name, self.ip_addr, self.sa)
        Session().commit()
        h.flash(_('Repository permissions updated'), category='success')
        return redirect(url('edit_repo_perms', repo_name=repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    def edit_fields(self, repo_name):
        """GET /repo_name/settings: Form to edit an existing item"""
        # url('edit_repo', repo_name=ID)
        c.repo_info = self._load_repo(repo_name)
        c.repo_fields = RepositoryField.query()\
            .filter(RepositoryField.repository == c.repo_info).all()
        c.active = 'fields'
        if request.POST:

            return redirect(url('repo_edit_fields'))
        return render('admin/repos/repo_edit.html')

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def create_repo_field(self, repo_name):
        try:
            form_result = RepoFieldForm()().to_python(dict(request.POST))
            RepoModel().add_repo_field(
                repo_name, form_result['new_field_key'],
                field_type=form_result['new_field_type'],
                field_value=form_result['new_field_value'],
                field_label=form_result['new_field_label'],
                field_desc=form_result['new_field_desc'])

            Session().commit()
        except Exception as e:
            log.exception("Exception creating field")
            msg = _('An error occurred during creation of field')
            if isinstance(e, formencode.Invalid):
                msg += ". " + e.msg
            h.flash(msg, category='error')
        return redirect(url('edit_repo_fields', repo_name=repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def delete_repo_field(self, repo_name, field_id):
        field = RepositoryField.get_or_404(field_id)
        try:
            RepoModel().delete_repo_field(repo_name, field.field_key)
            Session().commit()
        except Exception as e:
            log.exception("Exception during removal of field")
            msg = _('An error occurred during removal of field')
            h.flash(msg, category='error')
        return redirect(url('edit_repo_fields', repo_name=repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    def edit_advanced(self, repo_name):
        """GET /repo_name/settings: Form to edit an existing item"""
        # url('edit_repo', repo_name=ID)
        c.repo_info = self._load_repo(repo_name)
        c.default_user_id = User.get_default_user().user_id
        c.in_public_journal = UserFollowing.query()\
            .filter(UserFollowing.user_id == c.default_user_id)\
            .filter(UserFollowing.follows_repository == c.repo_info).scalar()

        c.active = 'advanced'
        c.has_origin_repo_read_perm = False
        if c.repo_info.fork:
            c.has_origin_repo_read_perm = h.HasRepoPermissionAny(
                'repository.write', 'repository.read', 'repository.admin')(
                c.repo_info.fork.repo_name, 'repo set as fork page')

        if request.POST:
            return redirect(url('repo_edit_advanced'))
        return render('admin/repos/repo_edit.html')

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def edit_advanced_journal(self, repo_name):
        """
        Set's this repository to be visible in public journal,
        in other words assing default user to follow this repo

        :param repo_name:
        """

        try:
            repo_id = Repository.get_by_repo_name(repo_name).repo_id
            user_id = User.get_default_user().user_id
            self.scm_model.toggle_following_repo(repo_id, user_id)
            h.flash(_('Updated repository visibility in public journal'),
                    category='success')
            Session().commit()
        except Exception:
            h.flash(_('An error occurred during setting this'
                      ' repository in public journal'),
                    category='error')

        return redirect(url('edit_repo_advanced', repo_name=repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def edit_advanced_fork(self, repo_name):
        """
        Mark given repository as a fork of another

        :param repo_name:
        """

        new_fork_id = request.POST.get('id_fork_of')
        try:

            if new_fork_id and not new_fork_id.isdigit():
                log.error('Given fork id %s is not an INT', new_fork_id)

            fork_id = safe_int(new_fork_id)
            repo = ScmModel().mark_as_fork(repo_name, fork_id,
                                           c.rhodecode_user.username)
            fork = repo.fork.repo_name if repo.fork else _('Nothing')
            Session().commit()
            h.flash(_('Marked repo %s as fork of %s') % (repo_name, fork),
                    category='success')
        except RepositoryError as e:
            log.exception("Repository Error occurred")
            h.flash(str(e), category='error')
        except Exception as e:
            log.exception("Exception while editing fork")
            h.flash(_('An error occurred during this operation'),
                    category='error')

        return redirect(url('edit_repo_advanced', repo_name=repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def edit_advanced_locking(self, repo_name):
        """
        Unlock repository when it is locked !

        :param repo_name:
        """
        try:
            repo = Repository.get_by_repo_name(repo_name)
            if request.POST.get('set_lock'):
                Repository.lock(repo, c.rhodecode_user.user_id,
                                lock_reason=Repository.LOCK_WEB)
                h.flash(_('Locked repository'), category='success')
            elif request.POST.get('set_unlock'):
                Repository.unlock(repo)
                h.flash(_('Unlocked repository'), category='success')
        except Exception as e:
            log.exception("Exception during unlocking")
            h.flash(_('An error occurred during unlocking'),
                    category='error')
        return redirect(url('edit_repo_advanced', repo_name=repo_name))

    @HasRepoPermissionAnyDecorator('repository.write', 'repository.admin')
    @auth.CSRFRequired()
    def toggle_locking(self, repo_name):
        """
        Toggle locking of repository by simple GET call to url

        :param repo_name:
        """

        try:
            repo = Repository.get_by_repo_name(repo_name)

            if repo.enable_locking:
                if repo.locked[0]:
                    Repository.unlock(repo)
                    action = _('Unlocked')
                else:
                    Repository.lock(repo, c.rhodecode_user.user_id,
                                    lock_reason=Repository.LOCK_WEB)
                    action = _('Locked')

                h.flash(_('Repository has been %s') % action,
                        category='success')
        except Exception:
            log.exception("Exception during unlocking")
            h.flash(_('An error occurred during unlocking'),
                    category='error')
        return redirect(url('summary_home', repo_name=repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def edit_caches(self, repo_name):
        """PUT /{repo_name}/settings/caches: invalidate the repo caches."""
        try:
            ScmModel().mark_for_invalidation(repo_name, delete=True)
            Session().commit()
            h.flash(_('Cache invalidation successful'),
                    category='success')
        except Exception:
            log.exception("Exception during cache invalidation")
            h.flash(_('An error occurred during cache invalidation'),
                    category='error')

        return redirect(url('edit_repo_caches', repo_name=c.repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    def edit_caches_form(self, repo_name):
        """GET /repo_name/settings: Form to edit an existing item"""
        # url('edit_repo', repo_name=ID)
        c.repo_info = self._load_repo(repo_name)
        c.active = 'caches'

        return render('admin/repos/repo_edit.html')

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def edit_remote(self, repo_name):
        """PUT /{repo_name}/settings/remote: edit the repo remote."""
        try:
            ScmModel().pull_changes(repo_name, c.rhodecode_user.username)
            h.flash(_('Pulled from remote location'), category='success')
        except Exception:
            log.exception("Exception during pull from remote")
            h.flash(_('An error occurred during pull from remote location'),
                    category='error')
        return redirect(url('edit_repo_remote', repo_name=c.repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    def edit_remote_form(self, repo_name):
        """GET /repo_name/settings: Form to edit an existing item"""
        # url('edit_repo', repo_name=ID)
        c.repo_info = self._load_repo(repo_name)
        c.active = 'remote'

        return render('admin/repos/repo_edit.html')

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def edit_statistics(self, repo_name):
        """PUT /{repo_name}/settings/statistics: reset the repo statistics."""
        try:
            RepoModel().delete_stats(repo_name)
            Session().commit()
        except Exception as e:
            log.error(traceback.format_exc())
            h.flash(_('An error occurred during deletion of repository stats'),
                    category='error')
        return redirect(url('edit_repo_statistics', repo_name=c.repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    def edit_statistics_form(self, repo_name):
        """GET /repo_name/settings: Form to edit an existing item"""
        # url('edit_repo', repo_name=ID)
        c.repo_info = self._load_repo(repo_name)
        repo = c.repo_info.scm_instance()

        if c.repo_info.stats:
            # this is on what revision we ended up so we add +1 for count
            last_rev = c.repo_info.stats.stat_on_revision + 1
        else:
            last_rev = 0
        c.stats_revision = last_rev

        c.repo_last_rev = repo.count()

        if last_rev == 0 or c.repo_last_rev == 0:
            c.stats_percentage = 0
        else:
            c.stats_percentage = '%.2f' % ((float((last_rev)) / c.repo_last_rev) * 100)

        c.active = 'statistics'

        return render('admin/repos/repo_edit.html')

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def repo_issuetracker_test(self, repo_name):
        if request.is_xhr:
            return h.urlify_commit_message(
                request.POST.get('test_text', ''),
                repo_name)
        else:
            raise HTTPBadRequest()

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def repo_issuetracker_delete(self, repo_name):
        uid = request.POST.get('uid')
        repo_settings = IssueTrackerSettingsModel(repo=repo_name)
        try:
            repo_settings.delete_entries(uid)
        except Exception:
            h.flash(_('Error occurred during deleting issue tracker entry'),
                    category='error')
        else:
            h.flash(_('Removed issue tracker entry'), category='success')
        return redirect(url('repo_settings_issuetracker',
                        repo_name=repo_name))

    def _update_patterns(self, form, repo_settings):
        for uid in form['delete_patterns']:
            repo_settings.delete_entries(uid)

        for pattern in form['patterns']:
            for setting, value, type_ in pattern:
                sett = repo_settings.create_or_update_setting(
                    setting, value, type_)
                Session().add(sett)

            Session().commit()

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def repo_issuetracker_save(self, repo_name):
        # Save inheritance
        repo_settings = IssueTrackerSettingsModel(repo=repo_name)
        inherited = (request.POST.get('inherit_global_issuetracker')
                     == "inherited")
        repo_settings.inherit_global_settings = inherited
        Session().commit()

        form = IssueTrackerPatternsForm()().to_python(request.POST)
        if form:
            self._update_patterns(form, repo_settings)

        h.flash(_('Updated issue tracker entries'), category='success')
        return redirect(url('repo_settings_issuetracker',
                        repo_name=repo_name))

    @HasRepoPermissionAllDecorator('repository.admin')
    def repo_issuetracker(self, repo_name):
        """GET /admin/settings/issue-tracker: All items in the collection"""
        c.active = 'issuetracker'
        c.data = 'data'
        c.repo_info = self._load_repo(repo_name)

        repo = Repository.get_by_repo_name(repo_name)
        c.settings_model = IssueTrackerSettingsModel(repo=repo)
        c.global_patterns = c.settings_model.get_global_settings()
        c.repo_patterns = c.settings_model.get_repo_settings()

        return render('admin/repos/repo_edit.html')

    @HasRepoPermissionAllDecorator('repository.admin')
    def repo_settings_vcs(self, repo_name):
        """GET /{repo_name}/settings/vcs/: All items in the collection"""

        model = VcsSettingsModel(repo=repo_name)

        c.active = 'vcs'
        c.global_svn_branch_patterns = model.get_global_svn_branch_patterns()
        c.global_svn_tag_patterns = model.get_global_svn_tag_patterns()
        c.svn_branch_patterns = model.get_repo_svn_branch_patterns()
        c.svn_tag_patterns = model.get_repo_svn_tag_patterns()
        c.repo_info = self._load_repo(repo_name)
        defaults = self._vcs_form_defaults(repo_name)
        c.inherit_global_settings = defaults['inherit_global_settings']

        return htmlfill.render(
            render('admin/repos/repo_edit.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    def repo_settings_vcs_update(self, repo_name):
        """POST /{repo_name}/settings/vcs/: All items in the collection"""
        c.active = 'vcs'

        model = VcsSettingsModel(repo=repo_name)
        c.global_svn_branch_patterns = model.get_global_svn_branch_patterns()
        c.global_svn_tag_patterns = model.get_global_svn_tag_patterns()
        c.svn_branch_patterns = model.get_repo_svn_branch_patterns()
        c.svn_tag_patterns = model.get_repo_svn_tag_patterns()
        c.repo_info = self._load_repo(repo_name)
        defaults = self._vcs_form_defaults(repo_name)
        c.inherit_global_settings = defaults['inherit_global_settings']

        application_form = RepoVcsSettingsForm(repo_name)()
        try:
            form_result = application_form.to_python(dict(request.POST))
        except formencode.Invalid as errors:
            h.flash(
                _("Some form inputs contain invalid data."),
                category='error')
            return htmlfill.render(
                render('admin/repos/repo_edit.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False
            )

        try:
            inherit_global_settings = form_result['inherit_global_settings']
            model.create_or_update_repo_settings(
                form_result, inherit_global_settings=inherit_global_settings)
        except Exception:
            log.exception("Exception while updating settings")
            h.flash(
                _('Error occurred during updating repository VCS settings'),
                category='error')
        else:
            Session().commit()
            h.flash(_('Updated VCS settings'), category='success')
            return redirect(url('repo_vcs_settings', repo_name=repo_name))

        return htmlfill.render(
            render('admin/repos/repo_edit.html'),
            defaults=self._vcs_form_defaults(repo_name),
            encoding="UTF-8",
            force_defaults=False)

    @HasRepoPermissionAllDecorator('repository.admin')
    @auth.CSRFRequired()
    @jsonify
    def repo_delete_svn_pattern(self, repo_name):
        if not request.is_xhr:
            return False

        delete_pattern_id = request.POST.get('delete_svn_pattern')
        model = VcsSettingsModel(repo=repo_name)
        try:
            model.delete_repo_svn_pattern(delete_pattern_id)
        except SettingNotFound:
            raise HTTPBadRequest()

        Session().commit()
        return True

    def _vcs_form_defaults(self, repo_name):
        model = VcsSettingsModel(repo=repo_name)
        global_defaults = model.get_global_settings()

        repo_defaults = {}
        repo_defaults.update(global_defaults)
        repo_defaults.update(model.get_repo_settings())

        global_defaults = {
            '{}_inherited'.format(k): global_defaults[k]
            for k in global_defaults}

        defaults = {
            'inherit_global_settings': model.inherit_global_settings
        }
        defaults.update(global_defaults)
        defaults.update(repo_defaults)
        defaults.update({
            'new_svn_branch': '',
            'new_svn_tag': '',
        })
        return defaults
