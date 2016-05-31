# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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
Compare controller for showing differences between two commits/refs/tags etc.
"""

import logging

from webob.exc import HTTPBadRequest
from pylons import request, tmpl_context as c, url
from pylons.controllers.util import redirect
from pylons.i18n.translation import _

from rhodecode.controllers.utils import parse_path_ref, get_commit_from_ref_name
from rhodecode.lib import helpers as h
from rhodecode.lib import diffs
from rhodecode.lib.auth import LoginRequired, HasRepoPermissionAnyDecorator
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.utils import safe_str
from rhodecode.lib.utils2 import safe_unicode, str2bool
from rhodecode.lib.vcs.exceptions import (
    EmptyRepositoryError, RepositoryError, RepositoryRequirementError)
from rhodecode.model.db import Repository, ChangesetStatus

log = logging.getLogger(__name__)


class CompareController(BaseRepoController):

    def __before__(self):
        super(CompareController, self).__before__()

    def _get_commit_or_redirect(
            self, ref, ref_type, repo, redirect_after=True, partial=False):
        """
        This is a safe way to get a commit. If an error occurs it
        redirects to a commit with a proper message. If partial is set
        then it does not do redirect raise and throws an exception instead.
        """
        try:
            return get_commit_from_ref_name(repo, safe_str(ref), ref_type)
        except EmptyRepositoryError:
            if not redirect_after:
                return repo.scm_instance().EMPTY_COMMIT
            h.flash(h.literal(_('There are no commits yet')),
                    category='warning')
            redirect(url('summary_home', repo_name=repo.repo_name))

        except RepositoryError as e:
            msg = safe_str(e)
            log.exception(msg)
            h.flash(msg, category='warning')
            if not partial:
                redirect(h.url('summary_home', repo_name=repo.repo_name))
            raise HTTPBadRequest()

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def index(self, repo_name):
        c.compare_home = True
        c.commit_ranges = []
        c.files = []
        c.limited_diff = False
        source_repo = c.rhodecode_db_repo.repo_name
        target_repo = request.GET.get('target_repo', source_repo)
        c.source_repo = Repository.get_by_repo_name(source_repo)
        c.target_repo = Repository.get_by_repo_name(target_repo)
        c.source_ref = c.target_ref = _('Select commit')
        c.source_ref_type = ""
        c.target_ref_type = ""
        c.commit_statuses = ChangesetStatus.STATUSES
        c.preview_mode = False
        return render('compare/compare_diff.html')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def compare(self, repo_name, source_ref_type, source_ref,
                                 target_ref_type, target_ref):
        # source_ref will be evaluated in source_repo
        source_repo_name = c.rhodecode_db_repo.repo_name
        source_path, source_id = parse_path_ref(source_ref)

        # target_ref will be evaluated in target_repo
        target_repo_name = request.GET.get('target_repo', source_repo_name)
        target_path, target_id = parse_path_ref(target_ref)

        c.commit_statuses = ChangesetStatus.STATUSES

        # if merge is True
        #   Show what changes since the shared ancestor commit of target/source
        #   the source would get if it was merged with target. Only commits
        #   which are in target but not in source will be shown.
        merge = str2bool(request.GET.get('merge'))
        # if merge is False
        #   Show a raw diff of source/target refs even if no ancestor exists


        # c.fulldiff disables cut_off_limit
        c.fulldiff = str2bool(request.GET.get('fulldiff'))

        # if partial, returns just compare_commits.html (commits log)
        partial = request.is_xhr

        # swap url for compare_diff page
        c.swap_url = h.url(
            'compare_url',
            repo_name=target_repo_name,
            source_ref_type=target_ref_type,
            source_ref=target_ref,
            target_repo=source_repo_name,
            target_ref_type=source_ref_type,
            target_ref=source_ref,
            merge=merge and '1' or '')

        source_repo = Repository.get_by_repo_name(source_repo_name)
        target_repo = Repository.get_by_repo_name(target_repo_name)

        if source_repo is None:
            msg = _('Could not find the original repo: %(repo)s') % {
                'repo': source_repo}

            log.error(msg)
            h.flash(msg, category='error')
            return redirect(url('compare_home', repo_name=c.repo_name))

        if target_repo is None:
            msg = _('Could not find the other repo: %(repo)s') % {
                'repo': target_repo_name}
            log.error(msg)
            h.flash(msg, category='error')
            return redirect(url('compare_home', repo_name=c.repo_name))

        source_alias = source_repo.scm_instance().alias
        target_alias = target_repo.scm_instance().alias
        if source_alias != target_alias:
            msg = _('The comparison of two different kinds of remote repos '
                    'is not available')
            log.error(msg)
            h.flash(msg, category='error')
            return redirect(url('compare_home', repo_name=c.repo_name))

        source_commit = self._get_commit_or_redirect(
            ref=source_id, ref_type=source_ref_type, repo=source_repo,
            partial=partial)
        target_commit = self._get_commit_or_redirect(
            ref=target_id, ref_type=target_ref_type, repo=target_repo,
            partial=partial)

        c.compare_home = False
        c.source_repo = source_repo
        c.target_repo = target_repo
        c.source_ref = source_ref
        c.target_ref = target_ref
        c.source_ref_type = source_ref_type
        c.target_ref_type = target_ref_type

        source_scm = source_repo.scm_instance()
        target_scm = target_repo.scm_instance()

        pre_load = ["author", "branch", "date", "message"]
        c.ancestor = None
        try:
            c.commit_ranges = source_scm.compare(
                source_commit.raw_id, target_commit.raw_id,
                target_scm, merge, pre_load=pre_load)
            if merge:
                c.ancestor = source_scm.get_common_ancestor(
                    source_commit.raw_id, target_commit.raw_id, target_scm)
        except RepositoryRequirementError:
            msg = _('Could not compare repos with different '
                    'large file settings')
            log.error(msg)
            if partial:
                return msg
            h.flash(msg, category='error')
            return redirect(url('compare_home', repo_name=c.repo_name))

        c.statuses = c.rhodecode_db_repo.statuses(
            [x.raw_id for x in c.commit_ranges])

        if partial: # for PR ajax commits loader
            if not c.ancestor:
                return '' # cannot merge if there is no ancestor
            return render('compare/compare_commits.html')

        if c.ancestor:
            # case we want a simple diff without incoming commits,
            # previewing what will be merged.
            # Make the diff on target repo (which is known to have target_ref)
            log.debug('Using ancestor %s as source_ref instead of %s'
                      % (c.ancestor, source_ref))
            source_repo = target_repo
            source_commit = target_repo.get_commit(commit_id=c.ancestor)

        # diff_limit will cut off the whole diff if the limit is applied
        # otherwise it will just hide the big files from the front-end
        diff_limit = self.cut_off_limit_diff
        file_limit = self.cut_off_limit_file

        log.debug('calculating diff between '
                  'source_ref:%s and target_ref:%s for repo `%s`',
                  source_commit, target_commit,
                  safe_unicode(source_repo.scm_instance().path))

        if source_commit.repository != target_commit.repository:
            msg = _(
                "Repositories unrelated. "
                "Cannot compare commit %(commit1)s from repository %(repo1)s "
                "with commit %(commit2)s from repository %(repo2)s.") % {
                    'commit1': h.show_id(source_commit),
                    'repo1': source_repo.repo_name,
                    'commit2': h.show_id(target_commit),
                    'repo2': target_repo.repo_name,
                }
            h.flash(msg, category='error')
            raise HTTPBadRequest()

        txtdiff = source_repo.scm_instance().get_diff(
            commit1=source_commit, commit2=target_commit,
            path1=source_path, path=target_path)
        diff_processor = diffs.DiffProcessor(
            txtdiff, format='gitdiff', diff_limit=diff_limit,
            file_limit=file_limit, show_full_diff=c.fulldiff)
        _parsed = diff_processor.prepare()

        c.limited_diff = False
        if isinstance(_parsed, diffs.LimitedDiffContainer):
            c.limited_diff = True

        c.files = []
        c.changes = {}
        c.lines_added = 0
        c.lines_deleted = 0
        for f in _parsed:
            st = f['stats']
            if not st['binary']:
                c.lines_added += st['added']
                c.lines_deleted += st['deleted']
            fid = h.FID('', f['filename'])
            c.files.append([fid, f['operation'], f['filename'], f['stats'], f])
            htmldiff = diff_processor.as_html(
                enable_comments=False, parsed_lines=[f])
            c.changes[fid] = [f['operation'], f['filename'], htmldiff, f]

        c.preview_mode = merge

        return render('compare/compare_diff.html')
