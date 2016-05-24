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
forks controller for rhodecode
"""

import formencode
import logging
from formencode import htmlfill

from pylons import tmpl_context as c, request, url
from pylons.controllers.util import redirect
from pylons.i18n.translation import _

import rhodecode.lib.helpers as h

from rhodecode.lib import auth
from rhodecode.lib.helpers import Page
from rhodecode.lib.auth import (
    LoginRequired, HasRepoPermissionAnyDecorator, NotAnonymous,
    HasRepoPermissionAny, HasPermissionAnyDecorator, HasAcceptedRepoType)
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.model.db import Repository, RepoGroup, UserFollowing, User
from rhodecode.model.repo import RepoModel
from rhodecode.model.forms import RepoForkForm
from rhodecode.model.scm import ScmModel, RepoGroupList
from rhodecode.lib.utils2 import safe_int

log = logging.getLogger(__name__)


class ForksController(BaseRepoController):

    def __before__(self):
        super(ForksController, self).__before__()

    def __load_defaults(self):
        acl_groups = RepoGroupList(
            RepoGroup.query().all(),
            perm_set=['group.write', 'group.admin'])
        c.repo_groups = RepoGroup.groups_choices(groups=acl_groups)
        c.repo_groups_choices = map(lambda k: unicode(k[0]), c.repo_groups)
        choices, c.landing_revs = ScmModel().get_repo_landing_revs()
        c.landing_revs_choices = choices
        c.personal_repo_group = RepoGroup.get_by_group_name(
            c.rhodecode_user.username)

    def __load_data(self, repo_name=None):
        """
        Load defaults settings for edit, and update

        :param repo_name:
        """
        self.__load_defaults()

        c.repo_info = Repository.get_by_repo_name(repo_name)
        repo = c.repo_info.scm_instance()

        if c.repo_info is None:
            h.not_mapped_error(repo_name)
            return redirect(url('repos'))

        c.default_user_id = User.get_default_user().user_id
        c.in_public_journal = UserFollowing.query()\
            .filter(UserFollowing.user_id == c.default_user_id)\
            .filter(UserFollowing.follows_repository == c.repo_info).scalar()

        if c.repo_info.stats:
            last_rev = c.repo_info.stats.stat_on_revision+1
        else:
            last_rev = 0
        c.stats_revision = last_rev

        c.repo_last_rev = repo.count()

        if last_rev == 0 or c.repo_last_rev == 0:
            c.stats_percentage = 0
        else:
            c.stats_percentage = '%.2f' % ((float((last_rev)) /
                                            c.repo_last_rev) * 100)

        defaults = RepoModel()._get_defaults(repo_name)
        # alter the description to indicate a fork
        defaults['description'] = ('fork of repository: %s \n%s'
                                   % (defaults['repo_name'],
                                      defaults['description']))
        # add suffix to fork
        defaults['repo_name'] = '%s-fork' % defaults['repo_name']

        return defaults

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @HasAcceptedRepoType('git', 'hg')
    def forks(self, repo_name):
        p = safe_int(request.GET.get('page', 1), 1)
        repo_id = c.rhodecode_db_repo.repo_id
        d = []
        for r in Repository.get_repo_forks(repo_id):
            if not HasRepoPermissionAny(
                'repository.read', 'repository.write', 'repository.admin'
            )(r.repo_name, 'get forks check'):
                continue
            d.append(r)
        c.forks_pager = Page(d, page=p, items_per_page=20)

        c.forks_data = render('/forks/forks_data.html')

        if request.environ.get('HTTP_X_PJAX'):
            return c.forks_data

        return render('/forks/forks.html')

    @LoginRequired()
    @NotAnonymous()
    @HasPermissionAnyDecorator('hg.admin', 'hg.fork.repository')
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @HasAcceptedRepoType('git', 'hg')
    def fork(self, repo_name):
        c.repo_info = Repository.get_by_repo_name(repo_name)
        if not c.repo_info:
            h.not_mapped_error(repo_name)
            return redirect(url('home'))

        defaults = self.__load_data(repo_name)

        return htmlfill.render(
            render('forks/fork.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @LoginRequired()
    @NotAnonymous()
    @HasPermissionAnyDecorator('hg.admin', 'hg.fork.repository')
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @HasAcceptedRepoType('git', 'hg')
    @auth.CSRFRequired()
    def fork_create(self, repo_name):
        self.__load_defaults()
        c.repo_info = Repository.get_by_repo_name(repo_name)
        _form = RepoForkForm(old_data={'repo_type': c.repo_info.repo_type},
                             repo_groups=c.repo_groups_choices,
                             landing_revs=c.landing_revs_choices)()
        form_result = {}
        task_id = None
        try:
            form_result = _form.to_python(dict(request.POST))
            # create fork is done sometimes async on celery, db transaction
            # management is handled there.
            task = RepoModel().create_fork(
                form_result, c.rhodecode_user.user_id)
            from celery.result import BaseAsyncResult
            if isinstance(task, BaseAsyncResult):
                task_id = task.task_id
        except formencode.Invalid as errors:
            c.new_repo = errors.value['repo_name']
            return htmlfill.render(
                render('forks/fork.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception(
                u'Exception while trying to fork the repository %s', repo_name)
            msg = (
                _('An error occurred during repository forking %s') %
                (repo_name, ))
            h.flash(msg, category='error')

        return redirect(h.url('repo_creating_home',
                              repo_name=form_result['repo_name_full'],
                              task_id=task_id))
