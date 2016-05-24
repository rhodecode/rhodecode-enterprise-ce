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
changelog controller for rhodecode
"""

import logging

from pylons import request, url, session, tmpl_context as c
from pylons.controllers.util import redirect
from pylons.i18n.translation import _
from webob.exc import HTTPNotFound, HTTPBadRequest

import rhodecode.lib.helpers as h
from rhodecode.lib.auth import LoginRequired, HasRepoPermissionAnyDecorator
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.ext_json import json
from rhodecode.lib.graphmod import _colored, _dagwalker
from rhodecode.lib.helpers import RepoPage
from rhodecode.lib.utils2 import safe_int, safe_str
from rhodecode.lib.vcs.exceptions import (
    RepositoryError, CommitDoesNotExistError,
    CommitError, NodeDoesNotExistError, EmptyRepositoryError)

log = logging.getLogger(__name__)

DEFAULT_CHANGELOG_SIZE = 20


def _load_changelog_summary():
    p = safe_int(request.GET.get('page'), 1)
    size = safe_int(request.GET.get('size'), 10)

    def url_generator(**kw):
        return url('summary_home',
                   repo_name=c.rhodecode_db_repo.repo_name, size=size, **kw)

    pre_load = ['author', 'branch', 'date', 'message']
    try:
        collection = c.rhodecode_repo.get_commits(pre_load=pre_load)
    except EmptyRepositoryError:
        collection = c.rhodecode_repo

    c.repo_commits = RepoPage(
        collection, page=p, items_per_page=size, url=url_generator)
    page_ids = [x.raw_id for x in c.repo_commits]
    c.comments = c.rhodecode_db_repo.get_comments(page_ids)
    c.statuses = c.rhodecode_db_repo.statuses(page_ids)


class ChangelogController(BaseRepoController):

    def __before__(self):
        super(ChangelogController, self).__before__()
        c.affected_files_cut_off = 60

    def __get_commit_or_redirect(
            self, commit_id, repo, redirect_after=True, partial=False):
        """
        This is a safe way to get a commit. If an error occurs it
        redirects to a commit with a proper message. If partial is set
        then it does not do redirect raise and throws an exception instead.

        :param commit_id: commit to fetch
        :param repo: repo instance
        """
        try:
            return c.rhodecode_repo.get_commit(commit_id)
        except EmptyRepositoryError:
            if not redirect_after:
                return None
            h.flash(h.literal(_('There are no commits yet')),
                    category='warning')
            redirect(url('changelog_home', repo_name=repo.repo_name))
        except RepositoryError as e:
            msg = safe_str(e)
            log.exception(msg)
            h.flash(msg, category='warning')
            if not partial:
                redirect(h.url('changelog_home', repo_name=repo.repo_name))
            raise HTTPBadRequest()

    def _graph(self, repo, commits):
        """
        Generates a DAG graph for repo

        :param repo: repo instance
        :param commits: list of commits
        """
        if not commits:
            c.jsdata = json.dumps([])
            return

        dag = _dagwalker(repo, commits)
        data = [['', vtx, edges] for vtx, edges in _colored(dag)]
        c.jsdata = json.dumps(data)

    def _check_if_valid_branch(self, branch_name, repo_name, f_path):
        if branch_name not in c.rhodecode_repo.branches_all:
            h.flash('Branch {} is not found.'.format(branch_name),
                    category='warning')
            redirect(url('changelog_file_home', repo_name=repo_name,
                         revision=branch_name, f_path=f_path or ''))

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def index(self, repo_name, revision=None, f_path=None):
        commit_id = revision
        limit = 100
        hist_limit = safe_int(request.GET.get('limit')) or None
        if request.GET.get('size'):
            c.size = safe_int(request.GET.get('size'), 1)
            session['changelog_size'] = c.size
            session.save()
        else:
            c.size = int(session.get('changelog_size', DEFAULT_CHANGELOG_SIZE))

        # min size must be 1 and less than limit
        c.size = max(c.size, 1) if c.size <= limit else limit

        p = safe_int(request.GET.get('page', 1), 1)
        c.branch_name = branch_name = request.GET.get('branch', None)
        c.book_name = book_name = request.GET.get('bookmark', None)

        c.selected_name = branch_name or book_name
        if not commit_id and branch_name:
            self._check_if_valid_branch(branch_name, repo_name, f_path)

        c.changelog_for_path = f_path
        pre_load = ['author', 'branch', 'date', 'message', 'parents']
        try:
            if f_path:
                log.debug('generating changelog for path %s', f_path)
                # get the history for the file !
                base_commit = c.rhodecode_repo.get_commit(revision)
                try:
                    collection = base_commit.get_file_history(
                        f_path, limit=hist_limit, pre_load=pre_load)
                    if (collection
                            and request.environ.get('HTTP_X_PARTIAL_XHR')):
                        # for ajax call we remove first one since we're looking
                        # at it right now in the context of a file commit
                        collection.pop(0)
                except (NodeDoesNotExistError, CommitError):
                    # this node is not present at tip!
                    try:
                        commit = self.__get_commit_or_redirect(
                            commit_id, repo_name)
                        collection = commit.get_file_history(f_path)
                    except RepositoryError as e:
                        h.flash(safe_str(e), category='warning')
                        redirect(h.url('changelog_home', repo_name=repo_name))
                collection = list(reversed(collection))
            else:
                collection = c.rhodecode_repo.get_commits(
                    branch_name=branch_name, pre_load=pre_load)

            c.total_cs = len(collection)
            c.showing_commits = min(c.size, c.total_cs)
            c.pagination = RepoPage(collection, page=p, item_count=c.total_cs,
                                    items_per_page=c.size, branch=branch_name)
            page_commit_ids = [x.raw_id for x in c.pagination]
            c.comments = c.rhodecode_db_repo.get_comments(page_commit_ids)
            c.statuses = c.rhodecode_db_repo.statuses(page_commit_ids)
        except EmptyRepositoryError as e:
            h.flash(safe_str(e), category='warning')
            return redirect(url('summary_home', repo_name=repo_name))
        except (RepositoryError, CommitDoesNotExistError, Exception) as e:
            msg = safe_str(e)
            log.exception(msg)
            h.flash(msg, category='error')
            return redirect(url('changelog_home', repo_name=repo_name))

        if (request.environ.get('HTTP_X_PARTIAL_XHR')
                or request.environ.get('HTTP_X_PJAX')):
            # loading from ajax, we don't want the first result, it's popped
            return render('changelog/changelog_file_history.html')

        if f_path:
            revs = []
        else:
            revs = c.pagination
        self._graph(c.rhodecode_repo, revs)

        return render('changelog/changelog.html')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def changelog_details(self, commit_id):
        if request.environ.get('HTTP_X_PARTIAL_XHR'):
            c.commit = c.rhodecode_repo.get_commit(commit_id=commit_id)
            return render('changelog/changelog_details.html')
        raise HTTPNotFound()

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def changelog_summary(self, repo_name):
        if request.environ.get('HTTP_X_PJAX'):
            _load_changelog_summary()
            return render('changelog/changelog_summary_data.html')
        raise HTTPNotFound()
