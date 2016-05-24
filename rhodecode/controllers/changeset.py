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
commit controller for RhodeCode showing changes between commits
"""

import logging

from collections import defaultdict
from webob.exc import HTTPForbidden, HTTPBadRequest, HTTPNotFound

from pylons import tmpl_context as c, request, response
from pylons.i18n.translation import _
from pylons.controllers.util import redirect

from rhodecode.lib import auth
from rhodecode.lib import diffs
from rhodecode.lib.auth import (
    LoginRequired, HasRepoPermissionAnyDecorator, NotAnonymous)
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.exceptions import StatusChangeOnClosedPullRequestError
import rhodecode.lib.helpers as h
from rhodecode.lib.utils import action_logger, jsonify
from rhodecode.lib.utils2 import safe_unicode
from rhodecode.lib.vcs.backends.base import EmptyCommit
from rhodecode.lib.vcs.exceptions import (
    RepositoryError, CommitDoesNotExistError)
from rhodecode.model.db import ChangesetComment, ChangesetStatus
from rhodecode.model.changeset_status import ChangesetStatusModel
from rhodecode.model.comment import ChangesetCommentsModel
from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel


log = logging.getLogger(__name__)


def _update_with_GET(params, GET):
    for k in ['diff1', 'diff2', 'diff']:
        params[k] += GET.getall(k)


def get_ignore_ws(fid, GET):
    ig_ws_global = GET.get('ignorews')
    ig_ws = filter(lambda k: k.startswith('WS'), GET.getall(fid))
    if ig_ws:
        try:
            return int(ig_ws[0].split(':')[-1])
        except Exception:
            pass
    return ig_ws_global


def _ignorews_url(GET, fileid=None):
    fileid = str(fileid) if fileid else None
    params = defaultdict(list)
    _update_with_GET(params, GET)
    label = _('Show whitespace')
    tooltiplbl = _('Show whitespace for all diffs')
    ig_ws = get_ignore_ws(fileid, GET)
    ln_ctx = get_line_ctx(fileid, GET)

    if ig_ws is None:
        params['ignorews'] += [1]
        label = _('Ignore whitespace')
        tooltiplbl = _('Ignore whitespace for all diffs')
    ctx_key = 'context'
    ctx_val = ln_ctx

    # if we have passed in ln_ctx pass it along to our params
    if ln_ctx:
        params[ctx_key] += [ctx_val]

    if fileid:
        params['anchor'] = 'a_' + fileid
    return h.link_to(label, h.url.current(**params), title=tooltiplbl, class_='tooltip')


def get_line_ctx(fid, GET):
    ln_ctx_global = GET.get('context')
    if fid:
        ln_ctx = filter(lambda k: k.startswith('C'), GET.getall(fid))
    else:
        _ln_ctx = filter(lambda k: k.startswith('C'), GET)
        ln_ctx = GET.get(_ln_ctx[0]) if _ln_ctx  else ln_ctx_global
        if ln_ctx:
            ln_ctx = [ln_ctx]

    if ln_ctx:
        retval = ln_ctx[0].split(':')[-1]
    else:
        retval = ln_ctx_global

    try:
        return int(retval)
    except Exception:
        return 3


def _context_url(GET, fileid=None):
    """
    Generates a url for context lines.

    :param fileid:
    """

    fileid = str(fileid) if fileid else None
    ig_ws = get_ignore_ws(fileid, GET)
    ln_ctx = (get_line_ctx(fileid, GET) or 3) * 2

    params = defaultdict(list)
    _update_with_GET(params, GET)

    if ln_ctx > 0:
        params['context'] += [ln_ctx]

    if ig_ws:
        ig_ws_key = 'ignorews'
        ig_ws_val = 1
        params[ig_ws_key] += [ig_ws_val]

    lbl = _('Increase context')
    tooltiplbl = _('Increase context for all diffs')

    if fileid:
        params['anchor'] = 'a_' + fileid
    return h.link_to(lbl, h.url.current(**params), title=tooltiplbl, class_='tooltip')


class ChangesetController(BaseRepoController):

    def __before__(self):
        super(ChangesetController, self).__before__()
        c.affected_files_cut_off = 60

    def _index(self, commit_id_range, method):
        c.ignorews_url = _ignorews_url
        c.context_url = _context_url
        c.fulldiff = fulldiff = request.GET.get('fulldiff')
        # get ranges of commit ids if preset
        commit_range = commit_id_range.split('...')[:2]
        enable_comments = True
        try:
            pre_load = ['affected_files', 'author', 'branch', 'date',
                        'message', 'parents']

            if len(commit_range) == 2:
                enable_comments = False
                commits = c.rhodecode_repo.get_commits(
                    start_id=commit_range[0], end_id=commit_range[1],
                    pre_load=pre_load)
                commits = list(commits)
            else:
                commits = [c.rhodecode_repo.get_commit(
                    commit_id=commit_id_range, pre_load=pre_load)]

            c.commit_ranges = commits
            if not c.commit_ranges:
                raise RepositoryError(
                    'The commit range returned an empty result')
        except CommitDoesNotExistError:
            msg = _('No such commit exists for this repository')
            h.flash(msg, category='error')
            raise HTTPNotFound()
        except Exception:
            log.exception("General failure")
            raise HTTPNotFound()

        c.changes = OrderedDict()
        c.lines_added = 0
        c.lines_deleted = 0

        c.commit_statuses = ChangesetStatus.STATUSES
        c.comments = []
        c.statuses = []
        c.inline_comments = []
        c.inline_cnt = 0
        c.files = []

        # Iterate over ranges (default commit view is always one commit)
        for commit in c.commit_ranges:
            if method == 'show':
                c.statuses.extend([ChangesetStatusModel().get_status(
                    c.rhodecode_db_repo.repo_id, commit.raw_id)])

                c.comments.extend(ChangesetCommentsModel().get_comments(
                    c.rhodecode_db_repo.repo_id,
                    revision=commit.raw_id))

                # comments from PR
                st = ChangesetStatusModel().get_statuses(
                    c.rhodecode_db_repo.repo_id, commit.raw_id,
                    with_revisions=True)

                # from associated statuses, check the pull requests, and
                # show comments from them

                prs = set(x.pull_request for x in
                          filter(lambda x: x.pull_request is not None, st))
                for pr in prs:
                    c.comments.extend(pr.comments)

                inlines = ChangesetCommentsModel().get_inline_comments(
                    c.rhodecode_db_repo.repo_id, revision=commit.raw_id)
                c.inline_comments.extend(inlines.iteritems())

            c.changes[commit.raw_id] = []

            commit2 = commit
            commit1 = commit.parents[0] if commit.parents else EmptyCommit()

            # fetch global flags of ignore ws or context lines
            context_lcl = get_line_ctx('', request.GET)
            ign_whitespace_lcl = get_ignore_ws('', request.GET)

            _diff = c.rhodecode_repo.get_diff(
                commit1, commit2,
                ignore_whitespace=ign_whitespace_lcl, context=context_lcl)

            # diff_limit will cut off the whole diff if the limit is applied
            # otherwise it will just hide the big files from the front-end
            diff_limit = self.cut_off_limit_diff
            file_limit = self.cut_off_limit_file

            diff_processor = diffs.DiffProcessor(
                _diff, format='gitdiff', diff_limit=diff_limit,
                file_limit=file_limit, show_full_diff=fulldiff)
            commit_changes = OrderedDict()
            if method == 'show':
                _parsed = diff_processor.prepare()
                c.limited_diff = isinstance(_parsed, diffs.LimitedDiffContainer)
                for f in _parsed:
                    c.files.append(f)
                    st = f['stats']
                    c.lines_added += st['added']
                    c.lines_deleted += st['deleted']
                    fid = h.FID(commit.raw_id, f['filename'])
                    diff = diff_processor.as_html(enable_comments=enable_comments,
                                                  parsed_lines=[f])
                    commit_changes[fid] = [
                        commit1.raw_id, commit2.raw_id,
                        f['operation'], f['filename'], diff, st, f]
            else:
                # downloads/raw we only need RAW diff nothing else
                diff = diff_processor.as_raw()
                commit_changes[''] = [None, None, None, None, diff, None, None]
            c.changes[commit.raw_id] = commit_changes

        # sort comments by how they were generated
        c.comments = sorted(c.comments, key=lambda x: x.comment_id)

        # count inline comments
        for __, lines in c.inline_comments:
            for comments in lines.values():
                c.inline_cnt += len(comments)

        if len(c.commit_ranges) == 1:
            c.commit = c.commit_ranges[0]
            c.parent_tmpl = ''.join(
                '# Parent  %s\n' % x.raw_id for x in c.commit.parents)
        if method == 'download':
            response.content_type = 'text/plain'
            response.content_disposition = (
                'attachment; filename=%s.diff' % commit_id_range[:12])
            return diff
        elif method == 'patch':
            response.content_type = 'text/plain'
            c.diff = safe_unicode(diff)
            return render('changeset/patch_changeset.html')
        elif method == 'raw':
            response.content_type = 'text/plain'
            return diff
        elif method == 'show':
            if len(c.commit_ranges) == 1:
                return render('changeset/changeset.html')
            else:
                c.ancestor = None
                c.target_repo = c.rhodecode_db_repo
                return render('changeset/changeset_range.html')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def index(self, revision, method='show'):
        return self._index(revision, method=method)

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def changeset_raw(self, revision):
        return self._index(revision, method='raw')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def changeset_patch(self, revision):
        return self._index(revision, method='patch')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def changeset_download(self, revision):
        return self._index(revision, method='download')

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @auth.CSRFRequired()
    @jsonify
    def comment(self, repo_name, revision):
        commit_id = revision
        status = request.POST.get('changeset_status', None)
        text = request.POST.get('text')
        if status:
            text = text or (_('Status change %(transition_icon)s %(status)s')
                            % {'transition_icon': '>',
                               'status': ChangesetStatus.get_status_lbl(status)})

        multi_commit_ids = filter(
            lambda s: s not in ['', None],
            request.POST.get('commit_ids', '').split(','),)

        commit_ids = multi_commit_ids or [commit_id]
        comment = None
        for current_id in filter(None, commit_ids):
            c.co = comment = ChangesetCommentsModel().create(
                text=text,
                repo=c.rhodecode_db_repo.repo_id,
                user=c.rhodecode_user.user_id,
                revision=current_id,
                f_path=request.POST.get('f_path'),
                line_no=request.POST.get('line'),
                status_change=(ChangesetStatus.get_status_lbl(status)
                               if status else None)
            )
            # get status if set !
            if status:
                # if latest status was from pull request and it's closed
                # disallow changing status !
                # dont_allow_on_closed_pull_request = True !

                try:
                    ChangesetStatusModel().set_status(
                        c.rhodecode_db_repo.repo_id,
                        status,
                        c.rhodecode_user.user_id,
                        comment,
                        revision=current_id,
                        dont_allow_on_closed_pull_request=True
                    )
                except StatusChangeOnClosedPullRequestError:
                    msg = _('Changing the status of a commit associated with '
                            'a closed pull request is not allowed')
                    log.exception(msg)
                    h.flash(msg, category='warning')
                    return redirect(h.url(
                        'changeset_home', repo_name=repo_name,
                        revision=current_id))

        # finalize, commit and redirect
        Session().commit()

        data = {
            'target_id': h.safeid(h.safe_unicode(request.POST.get('f_path'))),
        }
        if comment:
            data.update(comment.get_dict())
            data.update({'rendered_text':
                         render('changeset/changeset_comment_block.html')})

        return data

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @auth.CSRFRequired()
    def preview_comment(self):
        # Technically a CSRF token is not needed as no state changes with this
        # call. However, as this is a POST is better to have it, so automated
        # tools don't flag it as potential CSRF.
        # Post is required because the payload could be bigger than the maximum
        # allowed by GET.
        if not request.environ.get('HTTP_X_PARTIAL_XHR'):
            raise HTTPBadRequest()
        text = request.POST.get('text')
        renderer = request.POST.get('renderer') or 'rst'
        if text:
            return h.render(text, renderer=renderer, mentions=True)
        return ''

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @auth.CSRFRequired()
    @jsonify
    def delete_comment(self, repo_name, comment_id):
        comment = ChangesetComment.get(comment_id)
        owner = (comment.author.user_id == c.rhodecode_user.user_id)
        is_repo_admin = h.HasRepoPermissionAny('repository.admin')(c.repo_name)
        if h.HasPermissionAny('hg.admin')() or is_repo_admin or owner:
            ChangesetCommentsModel().delete(comment=comment)
            Session().commit()
            return True
        else:
            raise HTTPForbidden()

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @jsonify
    def changeset_info(self, repo_name, revision):
        if request.is_xhr:
            try:
                return c.rhodecode_repo.get_commit(commit_id=revision)
            except CommitDoesNotExistError as e:
                return EmptyCommit(message=str(e))
        else:
            raise HTTPBadRequest()

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @jsonify
    def changeset_children(self, repo_name, revision):
        if request.is_xhr:
            commit = c.rhodecode_repo.get_commit(commit_id=revision)
            result = {"results": commit.children}
            return result
        else:
            raise HTTPBadRequest()

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @jsonify
    def changeset_parents(self, repo_name, revision):
        if request.is_xhr:
            commit = c.rhodecode_repo.get_commit(commit_id=revision)
            result = {"results": commit.parents}
            return result
        else:
            raise HTTPBadRequest()
