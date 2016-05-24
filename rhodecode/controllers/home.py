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
Home controller for RhodeCode Enterprise
"""

import logging
import time


from pylons import tmpl_context as c, request
from pylons.i18n.translation import _
from sqlalchemy.sql import func

from rhodecode.lib.auth import (
    LoginRequired, HasPermissionAllDecorator,
    HasRepoGroupPermissionAnyDecorator, XHRRequired)
from rhodecode.lib.base import BaseController, render
from rhodecode.lib.ext_json import json
from rhodecode.lib.utils import jsonify
from rhodecode.lib.utils2 import safe_unicode
from rhodecode.model.db import Repository, RepoGroup
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.scm import RepoList, RepoGroupList


log = logging.getLogger(__name__)


class HomeController(BaseController):
    def __before__(self):
        super(HomeController, self).__before__()

    def ping(self):
        """
        Ping, doesn't require login, good for checking out the platform
        """
        instance_id = getattr(c, 'rhodecode_instanceid', '')
        return 'pong[%s] => %s' % (instance_id, self.ip_addr,)

    @LoginRequired()
    @HasPermissionAllDecorator('hg.admin')
    def error_test(self):
        """
        Test exception handling and emails on errors
        """
        class TestException(Exception):
            pass

        msg = ('RhodeCode Enterprise %s test exception. Generation time: %s'
               % (c.rhodecode_name, time.time()))
        raise TestException(msg)

    def _get_groups_and_repos(self, repo_group_id=None):
        # repo groups groups
        repo_group_list = RepoGroup.get_all_repo_groups(group_id=repo_group_id)
        _perms = ['group.read', 'group.write', 'group.admin']
        repo_group_list_acl = RepoGroupList(repo_group_list, perm_set=_perms)
        repo_group_data = RepoGroupModel().get_repo_groups_as_dict(
            repo_group_list=repo_group_list_acl, admin=False)

        # repositories
        repo_list = Repository.get_all_repos(group_id=repo_group_id)
        _perms = ['repository.read', 'repository.write', 'repository.admin']
        repo_list_acl = RepoList(repo_list, perm_set=_perms)
        repo_data = RepoModel().get_repos_as_dict(
            repo_list=repo_list_acl, admin=False)

        return repo_data, repo_group_data

    @LoginRequired()
    def index(self):
        c.repo_group = None

        repo_data, repo_group_data = self._get_groups_and_repos()
        # json used to render the grids
        c.repos_data = json.dumps(repo_data)
        c.repo_groups_data = json.dumps(repo_group_data)

        return render('/index.html')

    @LoginRequired()
    @HasRepoGroupPermissionAnyDecorator('group.read', 'group.write',
                                        'group.admin')
    def index_repo_group(self, group_name):
        """GET /repo_group_name: Show a specific item"""
        c.repo_group = RepoGroupModel()._get_repo_group(group_name)
        repo_data, repo_group_data = self._get_groups_and_repos(
            c.repo_group.group_id)

        # json used to render the grids
        c.repos_data = json.dumps(repo_data)
        c.repo_groups_data = json.dumps(repo_group_data)

        return render('index_repo_group.html')

    def _get_repo_list(self, name_contains=None, repo_type=None, limit=20):
        query = Repository.query()\
            .order_by(func.length(Repository.repo_name))\
            .order_by(Repository.repo_name)

        if repo_type:
            query = query.filter(Repository.repo_type == repo_type)

        if name_contains:
            ilike_expression = u'%{}%'.format(safe_unicode(name_contains))
            query = query.filter(
                Repository.repo_name.ilike(ilike_expression))
            query = query.limit(limit)

        all_repos = query.all()
        repo_iter = self.scm_model.get_repos(all_repos)
        return [
            {
                'id': obj['name'],
                'text': obj['name'],
                'type': 'repo',
                'obj': obj['dbrepo']
            }
            for obj in repo_iter]

    def _get_repo_group_list(self, name_contains=None, limit=20):
        query = RepoGroup.query()\
            .order_by(func.length(RepoGroup.group_name))\
            .order_by(RepoGroup.group_name)

        if name_contains:
            ilike_expression = u'%{}%'.format(safe_unicode(name_contains))
            query = query.filter(
                RepoGroup.group_name.ilike(ilike_expression))
            query = query.limit(limit)

        all_groups = query.all()
        repo_groups_iter = self.scm_model.get_repo_groups(all_groups)
        return [
            {
                'id': obj.group_name,
                'text': obj.group_name,
                'type': 'group',
                'obj': {}
            }
            for obj in repo_groups_iter]

    @LoginRequired()
    @XHRRequired()
    @jsonify
    def repo_switcher_data(self):
        query = request.GET.get('query')
        log.debug('generating switcher repo/groups list, query %s', query)

        res = []
        repo_groups = self._get_repo_group_list(query)
        if repo_groups:
            res.append({
                'text': _('Groups'),
                'children': repo_groups
            })

        repos = self._get_repo_list(query)
        if repos:
            res.append({
                'text': _('Repositories'),
                'children': repos
            })

        data = {
            'more': False,
            'results': res
        }
        return data

    @LoginRequired()
    @XHRRequired()
    @jsonify
    def repo_list_data(self):
        query = request.GET.get('query')
        repo_type = request.GET.get('repo_type')
        log.debug('generating repo list, query:%s', query)

        res = []
        repos = self._get_repo_list(query, repo_type=repo_type)
        if repos:
            res.append({
                'text': _('Repositories'),
                'children': repos
            })
        data = {
            'more': False,
            'results': res
        }
        return data

    @LoginRequired()
    @XHRRequired()
    @jsonify
    def user_autocomplete_data(self):
        query = request.GET.get('query')

        repo_model = RepoModel()
        _users = repo_model.get_users(name_contains=query)

        if request.GET.get('user_groups'):
            # extend with user groups
            _user_groups = repo_model.get_user_groups(name_contains=query)
            _users = _users + _user_groups

        return {'suggestions': _users}

    @LoginRequired()
    @XHRRequired()
    @jsonify
    def user_group_autocomplete_data(self):
        return {'suggestions': []}
