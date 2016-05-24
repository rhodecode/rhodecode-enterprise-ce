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
pull requests controller for rhodecode for initializing pull requests
"""

import formencode
import logging

from webob.exc import HTTPNotFound, HTTPForbidden, HTTPBadRequest
from pylons import request, tmpl_context as c, url
from pylons.controllers.util import redirect
from pylons.i18n.translation import _
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import or_

from rhodecode.lib import auth, diffs, helpers as h
from rhodecode.lib.ext_json import json
from rhodecode.lib.base import (
    BaseRepoController, render, vcs_operation_context)
from rhodecode.lib.auth import (
    LoginRequired, HasRepoPermissionAnyDecorator, NotAnonymous,
    HasAcceptedRepoType, XHRRequired)
from rhodecode.lib.utils import jsonify
from rhodecode.lib.utils2 import safe_int, safe_str, str2bool, safe_unicode
from rhodecode.lib.vcs.backends.base import EmptyCommit
from rhodecode.lib.vcs.exceptions import (
    EmptyRepositoryError, CommitDoesNotExistError, RepositoryRequirementError)
from rhodecode.lib.diffs import LimitedDiffContainer
from rhodecode.model.changeset_status import ChangesetStatusModel
from rhodecode.model.comment import ChangesetCommentsModel
from rhodecode.model.db import PullRequest, ChangesetStatus, ChangesetComment, \
    Repository
from rhodecode.model.forms import PullRequestForm
from rhodecode.model.meta import Session
from rhodecode.model.pull_request import PullRequestModel

log = logging.getLogger(__name__)


class PullrequestsController(BaseRepoController):
    def __before__(self):
        super(PullrequestsController, self).__before__()

    def _load_compare_data(self, pull_request, enable_comments=True):
        """
        Load context data needed for generating compare diff

        :param pull_request: object related to the request
        :param enable_comments: flag to determine if comments are included
        """
        source_repo = pull_request.source_repo
        source_ref_id = pull_request.source_ref_parts.commit_id

        target_repo = pull_request.target_repo
        target_ref_id = pull_request.target_ref_parts.commit_id

        # despite opening commits for bookmarks/branches/tags, we always
        # convert this to rev to prevent changes after bookmark or branch change
        c.source_ref_type = 'rev'
        c.source_ref = source_ref_id

        c.target_ref_type = 'rev'
        c.target_ref = target_ref_id

        c.source_repo = source_repo
        c.target_repo = target_repo

        c.fulldiff = bool(request.GET.get('fulldiff'))

        # diff_limit is the old behavior, will cut off the whole diff
        # if the limit is applied  otherwise will just hide the
        # big files from the front-end
        diff_limit = self.cut_off_limit_diff
        file_limit = self.cut_off_limit_file

        pre_load = ["author", "branch", "date", "message"]

        c.commit_ranges = []
        source_commit = EmptyCommit()
        target_commit = EmptyCommit()
        c.missing_requirements = False
        try:
            c.commit_ranges = [
                source_repo.get_commit(commit_id=rev, pre_load=pre_load)
                for rev in pull_request.revisions]

            c.statuses = source_repo.statuses(
                [x.raw_id for x in c.commit_ranges])

            target_commit = source_repo.get_commit(
                commit_id=safe_str(target_ref_id))
            source_commit = source_repo.get_commit(
                commit_id=safe_str(source_ref_id))
        except RepositoryRequirementError:
            c.missing_requirements = True

        c.missing_commits = False
        if (c.missing_requirements or
                isinstance(source_commit, EmptyCommit) or
                    source_commit == target_commit):
            _parsed = []
            c.missing_commits = True
        else:
            vcs_diff = PullRequestModel().get_diff(pull_request)
            diff_processor = diffs.DiffProcessor(
                vcs_diff, format='gitdiff', diff_limit=diff_limit,
                file_limit=file_limit, show_full_diff=c.fulldiff)
            _parsed = diff_processor.prepare()

        c.limited_diff = isinstance(_parsed, LimitedDiffContainer)

        c.files = []
        c.changes = {}
        c.lines_added = 0
        c.lines_deleted = 0
        c.included_files = []
        c.deleted_files = []

        for f in _parsed:
            st = f['stats']
            c.lines_added += st['added']
            c.lines_deleted += st['deleted']

            fid = h.FID('', f['filename'])
            c.files.append([fid, f['operation'], f['filename'], f['stats']])
            c.included_files.append(f['filename'])
            html_diff = diff_processor.as_html(enable_comments=enable_comments,
                                               parsed_lines=[f])
            c.changes[fid] = [f['operation'], f['filename'], html_diff, f]

    def _extract_ordering(self, request):
        column_index = safe_int(request.GET.get('order[0][column]'))
        order_dir = request.GET.get('order[0][dir]', 'desc')
        order_by = request.GET.get(
            'columns[%s][data][sort]' % column_index, 'name_raw')
        return order_by, order_dir

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @HasAcceptedRepoType('git', 'hg')
    def show_all(self, repo_name):
        # filter types
        c.active = 'open'
        c.source = str2bool(request.GET.get('source'))
        c.closed = str2bool(request.GET.get('closed'))
        c.my = str2bool(request.GET.get('my'))
        c.awaiting_review = str2bool(request.GET.get('awaiting_review'))
        c.awaiting_my_review = str2bool(request.GET.get('awaiting_my_review'))
        c.repo_name = repo_name

        opened_by = None
        if c.my:
            c.active = 'my'
            opened_by = [c.rhodecode_user.user_id]

        statuses = [PullRequest.STATUS_NEW, PullRequest.STATUS_OPEN]
        if c.closed:
            c.active = 'closed'
            statuses = [PullRequest.STATUS_CLOSED]

        if c.awaiting_review and not c.source:
            c.active = 'awaiting'
        if c.source and not c.awaiting_review:
            c.active = 'source'
        if c.awaiting_my_review:
            c.active = 'awaiting_my'

        data = self._get_pull_requests_list(
            repo_name=repo_name, opened_by=opened_by, statuses=statuses)
        if not request.is_xhr:
            c.data = json.dumps(data['data'])
            c.records_total = data['recordsTotal']
            return render('/pullrequests/pullrequests.html')
        else:
            return json.dumps(data)

    def _get_pull_requests_list(self, repo_name, opened_by, statuses):
        # pagination
        start = safe_int(request.GET.get('start'), 0)
        length = safe_int(request.GET.get('length'), c.visual.dashboard_items)
        order_by, order_dir = self._extract_ordering(request)

        if c.awaiting_review:
            pull_requests = PullRequestModel().get_awaiting_review(
                repo_name, source=c.source, opened_by=opened_by,
                statuses=statuses, offset=start, length=length,
                order_by=order_by, order_dir=order_dir)
            pull_requests_total_count = PullRequestModel(
            ).count_awaiting_review(
                repo_name, source=c.source, statuses=statuses,
                opened_by=opened_by)
        elif c.awaiting_my_review:
            pull_requests = PullRequestModel().get_awaiting_my_review(
                repo_name, source=c.source, opened_by=opened_by,
                user_id=c.rhodecode_user.user_id, statuses=statuses,
                offset=start, length=length, order_by=order_by,
                order_dir=order_dir)
            pull_requests_total_count = PullRequestModel(
            ).count_awaiting_my_review(
                repo_name, source=c.source, user_id=c.rhodecode_user.user_id,
                statuses=statuses, opened_by=opened_by)
        else:
            pull_requests = PullRequestModel().get_all(
                repo_name, source=c.source, opened_by=opened_by,
                statuses=statuses, offset=start, length=length,
                order_by=order_by, order_dir=order_dir)
            pull_requests_total_count = PullRequestModel().count_all(
                repo_name, source=c.source, statuses=statuses,
                opened_by=opened_by)

        from rhodecode.lib.utils import PartialRenderer
        _render = PartialRenderer('data_table/_dt_elements.html')
        data = []
        for pr in pull_requests:
            comments = ChangesetCommentsModel().get_all_comments(
                c.rhodecode_db_repo.repo_id, pull_request=pr)

            data.append({
                'name': _render('pullrequest_name',
                                pr.pull_request_id, pr.target_repo.repo_name),
                'name_raw': pr.pull_request_id,
                'status': _render('pullrequest_status',
                                  pr.calculated_review_status()),
                'title': _render(
                    'pullrequest_title', pr.title, pr.description),
                'description': h.escape(pr.description),
                'updated_on': _render('pullrequest_updated_on',
                                      h.datetime_to_time(pr.updated_on)),
                'updated_on_raw': h.datetime_to_time(pr.updated_on),
                'created_on': _render('pullrequest_updated_on',
                                      h.datetime_to_time(pr.created_on)),
                'created_on_raw': h.datetime_to_time(pr.created_on),
                'author': _render('pullrequest_author',
                                  pr.author.full_contact, ),
                'author_raw': pr.author.full_name,
                'comments': _render('pullrequest_comments', len(comments)),
                'comments_raw': len(comments),
                'closed': pr.is_closed(),
            })
        # json used to render the grid
        data = ({
            'data': data,
            'recordsTotal': pull_requests_total_count,
            'recordsFiltered': pull_requests_total_count,
        })
        return data

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @HasAcceptedRepoType('git', 'hg')
    def index(self):
        source_repo = c.rhodecode_db_repo

        try:
            source_repo.scm_instance().get_commit()
        except EmptyRepositoryError:
            h.flash(h.literal(_('There are no commits yet')),
                    category='warning')
            redirect(url('summary_home', repo_name=source_repo.repo_name))

        commit_id = request.GET.get('commit')
        branch_ref = request.GET.get('branch')
        bookmark_ref = request.GET.get('bookmark')

        try:
            source_repo_data = PullRequestModel().generate_repo_data(
                source_repo, commit_id=commit_id,
                branch=branch_ref, bookmark=bookmark_ref)
        except CommitDoesNotExistError as e:
            log.exception(e)
            h.flash(_('Commit does not exist'), 'error')
            redirect(url('pullrequest_home', repo_name=source_repo.repo_name))

        default_target_repo = source_repo
        if (source_repo.parent and
                not source_repo.parent.scm_instance().is_empty()):
            # change default if we have a parent repo
            default_target_repo = source_repo.parent

        target_repo_data = PullRequestModel().generate_repo_data(
            default_target_repo)

        selected_source_ref = source_repo_data['refs']['selected_ref']

        title_source_ref = selected_source_ref.split(':', 2)[1]
        c.default_title = PullRequestModel().generate_pullrequest_title(
            source=source_repo.repo_name,
            source_ref=title_source_ref,
            target=default_target_repo.repo_name
        )

        c.default_repo_data = {
            'source_repo_name': source_repo.repo_name,
            'source_refs_json': json.dumps(source_repo_data),
            'target_repo_name': default_target_repo.repo_name,
            'target_refs_json': json.dumps(target_repo_data),
        }
        c.default_source_ref = selected_source_ref

        return render('/pullrequests/pullrequest.html')

    @LoginRequired()
    @NotAnonymous()
    @XHRRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @jsonify
    def get_repo_refs(self, repo_name, target_repo_name):
        repo = Repository.get_by_repo_name(target_repo_name)
        if not repo:
            raise HTTPNotFound
        return PullRequestModel().generate_repo_data(repo)

    @LoginRequired()
    @NotAnonymous()
    @XHRRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @jsonify
    def get_repo_destinations(self, repo_name):
        repo = Repository.get_by_repo_name(repo_name)
        if not repo:
            raise HTTPNotFound
        filter_query = request.GET.get('query')

        query = Repository.query() \
            .order_by(func.length(Repository.repo_name)) \
            .filter(or_(
            Repository.repo_name == repo.repo_name,
            Repository.fork_id == repo.repo_id))

        if filter_query:
            ilike_expression = u'%{}%'.format(safe_unicode(filter_query))
            query = query.filter(
                Repository.repo_name.ilike(ilike_expression))

        add_parent = False
        if repo.parent:
            if filter_query in repo.parent.repo_name:
                if not repo.parent.scm_instance().is_empty():
                    add_parent = True

        limit = 20 - 1 if add_parent else 20
        all_repos = query.limit(limit).all()
        if add_parent:
            all_repos += [repo.parent]

        repos = []
        for obj in self.scm_model.get_repos(all_repos):
            repos.append({
                'id': obj['name'],
                'text': obj['name'],
                'type': 'repo',
                'obj': obj['dbrepo']
            })

        data = {
            'more': False,
            'results': [{
                'text': _('Repositories'),
                'children': repos
            }] if repos else []
        }
        return data

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @HasAcceptedRepoType('git', 'hg')
    @auth.CSRFRequired()
    def create(self, repo_name):
        repo = Repository.get_by_repo_name(repo_name)
        if not repo:
            raise HTTPNotFound

        try:
            _form = PullRequestForm(repo.repo_id)().to_python(request.POST)
        except formencode.Invalid as errors:
            if errors.error_dict.get('revisions'):
                msg = 'Revisions: %s' % errors.error_dict['revisions']
            elif errors.error_dict.get('pullrequest_title'):
                msg = _('Pull request requires a title with min. 3 chars')
            else:
                msg = _('Error creating pull request: {}').format(errors)
            log.exception(msg)
            h.flash(msg, 'error')

            # would rather just go back to form ...
            return redirect(url('pullrequest_home', repo_name=repo_name))

        source_repo = _form['source_repo']
        source_ref = _form['source_ref']
        target_repo = _form['target_repo']
        target_ref = _form['target_ref']
        commit_ids = _form['revisions'][::-1]
        reviewers = _form['review_members']

        # find the ancestor for this pr
        source_db_repo = Repository.get_by_repo_name(_form['source_repo'])
        target_db_repo = Repository.get_by_repo_name(_form['target_repo'])

        source_scm = source_db_repo.scm_instance()
        target_scm = target_db_repo.scm_instance()

        source_commit = source_scm.get_commit(source_ref.split(':')[-1])
        target_commit = target_scm.get_commit(target_ref.split(':')[-1])

        ancestor = source_scm.get_common_ancestor(
            source_commit.raw_id, target_commit.raw_id, target_scm)

        target_ref_type, target_ref_name, __ = _form['target_ref'].split(':')
        target_ref = ':'.join((target_ref_type, target_ref_name, ancestor))

        pullrequest_title = _form['pullrequest_title']
        title_source_ref = source_ref.split(':', 2)[1]
        if not pullrequest_title:
            pullrequest_title = PullRequestModel().generate_pullrequest_title(
                source=source_repo,
                source_ref=title_source_ref,
                target=target_repo
            )

        description = _form['pullrequest_desc']
        try:
            pull_request = PullRequestModel().create(
                c.rhodecode_user.user_id, source_repo, source_ref, target_repo,
                target_ref, commit_ids, reviewers, pullrequest_title,
                description
            )
            Session().commit()
            h.flash(_('Successfully opened new pull request'),
                    category='success')
        except Exception as e:
            msg = _('Error occurred during sending pull request')
            log.exception(msg)
            h.flash(msg, category='error')
            return redirect(url('pullrequest_home', repo_name=repo_name))

        return redirect(url('pullrequest_show', repo_name=target_repo,
                            pull_request_id=pull_request.pull_request_id))

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @auth.CSRFRequired()
    @jsonify
    def update(self, repo_name, pull_request_id):
        pull_request_id = safe_int(pull_request_id)
        pull_request = PullRequest.get_or_404(pull_request_id)
        # only owner or admin can update it
        allowed_to_update = PullRequestModel().check_user_update(
            pull_request, c.rhodecode_user)
        if allowed_to_update:
            if 'reviewers_ids' in request.POST:
                self._update_reviewers(pull_request_id)
            elif str2bool(request.POST.get('update_commits', 'false')):
                self._update_commits(pull_request)
            elif str2bool(request.POST.get('close_pull_request', 'false')):
                self._reject_close(pull_request)
            elif str2bool(request.POST.get('edit_pull_request', 'false')):
                self._edit_pull_request(pull_request)
            else:
                raise HTTPBadRequest()
            return True
        raise HTTPForbidden()

    def _edit_pull_request(self, pull_request):
        try:
            PullRequestModel().edit(
                pull_request, request.POST.get('title'),
                request.POST.get('description'))
        except ValueError:
            msg = _(u'Cannot update closed pull requests.')
            h.flash(msg, category='error')
            return
        else:
            Session().commit()

        msg = _(u'Pull request title & description updated.')
        h.flash(msg, category='success')
        return

    def _update_commits(self, pull_request):
        try:
            if PullRequestModel().has_valid_update_type(pull_request):
                updated_version, changes = PullRequestModel().update_commits(
                    pull_request)
                if updated_version:
                    msg = _(
                        u'Pull request updated to "{source_commit_id}" with '
                        u'{count_added} added, {count_removed} removed '
                        u'commits.'
                    ).format(
                        source_commit_id=pull_request.source_ref_parts.commit_id,
                        count_added=len(changes.added),
                        count_removed=len(changes.removed))
                    h.flash(msg, category='success')
                else:
                    h.flash(_("Nothing changed in pull request."),
                            category='warning')
            else:
                msg = _(
                    u"Skipping update of pull request due to reference "
                    u"type: {reference_type}"
                ).format(reference_type=pull_request.source_ref_parts.type)
                h.flash(msg, category='warning')
        except CommitDoesNotExistError:
            h.flash(
                _(u'Update failed due to missing commits.'), category='error')

    @auth.CSRFRequired()
    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def merge(self, repo_name, pull_request_id):
        """
        POST /{repo_name}/pull-request/{pull_request_id}

        Merge will perform a server-side merge of the specified
        pull request, if the pull request is approved and mergeable.
        After succesfull merging, the pull request is automatically
        closed, with a relevant comment.
        """
        pull_request_id = safe_int(pull_request_id)
        pull_request = PullRequest.get_or_404(pull_request_id)
        user = c.rhodecode_user

        if self._meets_merge_pre_conditions(pull_request, user):
            log.debug("Pre-conditions checked, trying to merge.")
            extras = vcs_operation_context(
                request.environ, repo_name=pull_request.target_repo.repo_name,
                username=user.username, action='push',
                scm=pull_request.target_repo.repo_type)
            self._merge_pull_request(pull_request, user, extras)

        return redirect(url(
            'pullrequest_show',
            repo_name=pull_request.target_repo.repo_name,
            pull_request_id=pull_request.pull_request_id))

    def _meets_merge_pre_conditions(self, pull_request, user):
        if not PullRequestModel().check_user_merge(pull_request, user):
            raise HTTPForbidden()

        merge_status, msg = PullRequestModel().merge_status(pull_request)
        if not merge_status:
            log.debug("Cannot merge, not mergeable.")
            h.flash(msg, category='error')
            return False

        if (pull_request.calculated_review_status()
            is not ChangesetStatus.STATUS_APPROVED):
            log.debug("Cannot merge, approval is pending.")
            msg = _('Pull request reviewer approval is pending.')
            h.flash(msg, category='error')
            return False
        return True

    def _merge_pull_request(self, pull_request, user, extras):
        merge_resp = PullRequestModel().merge(
            pull_request, user, extras=extras)

        if merge_resp.executed:
            log.debug("The merge was successful, closing the pull request.")
            PullRequestModel().close_pull_request(
                pull_request.pull_request_id, user)
            Session().commit()
        else:
            log.debug(
                "The merge was not successful. Merge response: %s",
                merge_resp)
            msg = PullRequestModel().merge_status_message(
                merge_resp.failure_reason)
            h.flash(msg, category='error')

    def _update_reviewers(self, pull_request_id):
        reviewers_ids = map(int, filter(
            lambda v: v not in [None, ''],
            request.POST.get('reviewers_ids', '').split(',')))
        PullRequestModel().update_reviewers(pull_request_id, reviewers_ids)
        Session().commit()

    def _reject_close(self, pull_request):
        if pull_request.is_closed():
            raise HTTPForbidden()

        PullRequestModel().close_pull_request_with_comment(
            pull_request, c.rhodecode_user, c.rhodecode_db_repo)
        Session().commit()

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @auth.CSRFRequired()
    @jsonify
    def delete(self, repo_name, pull_request_id):
        pull_request_id = safe_int(pull_request_id)
        pull_request = PullRequest.get_or_404(pull_request_id)
        # only owner can delete it !
        if pull_request.author.user_id == c.rhodecode_user.user_id:
            PullRequestModel().delete(pull_request)
            Session().commit()
            h.flash(_('Successfully deleted pull request'),
                    category='success')
            return redirect(url('my_account_pullrequests'))
        raise HTTPForbidden()

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def show(self, repo_name, pull_request_id):
        pull_request_id = safe_int(pull_request_id)
        c.pull_request = PullRequest.get_or_404(pull_request_id)

        # pull_requests repo_name we opened it against
        # ie. target_repo must match
        if repo_name != c.pull_request.target_repo.repo_name:
            raise HTTPNotFound

        c.allowed_to_change_status = PullRequestModel(). \
            check_user_change_status(c.pull_request, c.rhodecode_user)
        c.allowed_to_update = PullRequestModel().check_user_update(
            c.pull_request, c.rhodecode_user) and not c.pull_request.is_closed()
        c.allowed_to_merge = PullRequestModel().check_user_merge(
            c.pull_request, c.rhodecode_user) and not c.pull_request.is_closed()

        cc_model = ChangesetCommentsModel()

        c.pull_request_reviewers = c.pull_request.reviewers_statuses()

        c.pull_request_review_status = c.pull_request.calculated_review_status()
        c.pr_merge_status, c.pr_merge_msg = PullRequestModel().merge_status(
            c.pull_request)
        c.approval_msg = None
        if c.pull_request_review_status != ChangesetStatus.STATUS_APPROVED:
            c.approval_msg = _('Reviewer approval is pending.')
            c.pr_merge_status = False
        # load compare data into template context
        enable_comments = not c.pull_request.is_closed()
        self._load_compare_data(c.pull_request, enable_comments=enable_comments)

        # this is a hack to properly display links, when creating PR, the
        # compare view and others uses different notation, and
        # compare_commits.html renders links based on the target_repo.
        # We need to swap that here to generate it properly on the html side
        c.target_repo = c.source_repo

        # inline comments
        c.inline_cnt = 0
        c.inline_comments = cc_model.get_inline_comments(
            c.rhodecode_db_repo.repo_id,
            pull_request=pull_request_id).items()
        # count inline comments
        for __, lines in c.inline_comments:
            for comments in lines.values():
                c.inline_cnt += len(comments)

        # outdated comments
        c.outdated_cnt = 0
        if ChangesetCommentsModel.use_outdated_comments(c.pull_request):
            c.outdated_comments = cc_model.get_outdated_comments(
                c.rhodecode_db_repo.repo_id,
                pull_request=c.pull_request)
            # Count outdated comments and check for deleted files
            for file_name, lines in c.outdated_comments.iteritems():
                for comments in lines.values():
                    c.outdated_cnt += len(comments)
                if file_name not in c.included_files:
                    c.deleted_files.append(file_name)
        else:
            c.outdated_comments = {}

        # comments
        c.comments = cc_model.get_comments(c.rhodecode_db_repo.repo_id,
                                           pull_request=pull_request_id)

        if c.allowed_to_update:
            force_close = ('forced_closed', _('Close Pull Request'))
            statuses = ChangesetStatus.STATUSES + [force_close]
        else:
            statuses = ChangesetStatus.STATUSES
        c.commit_statuses = statuses

        c.ancestor = None # TODO: add ancestor here

        return render('/pullrequests/pullrequest_show.html')

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @auth.CSRFRequired()
    @jsonify
    def comment(self, repo_name, pull_request_id):
        pull_request_id = safe_int(pull_request_id)
        pull_request = PullRequest.get_or_404(pull_request_id)
        if pull_request.is_closed():
            raise HTTPForbidden()

        # TODO: johbo: Re-think this bit, "approved_closed" does not exist
        # as a changeset status, still we want to send it in one value.
        status = request.POST.get('changeset_status', None)
        text = request.POST.get('text')
        if status and '_closed' in status:
            close_pr = True
            status = status.replace('_closed', '')
        else:
            close_pr = False

        forced = (status == 'forced')
        if forced:
            status = 'rejected'

        allowed_to_change_status = PullRequestModel().check_user_change_status(
            pull_request, c.rhodecode_user)

        if status and allowed_to_change_status:
            message = (_('Status change %(transition_icon)s %(status)s')
                       % {'transition_icon': '>',
                          'status': ChangesetStatus.get_status_lbl(status)})
            if close_pr:
                message = _('Closing with') + ' ' + message
            text = text or message
        comm = ChangesetCommentsModel().create(
            text=text,
            repo=c.rhodecode_db_repo.repo_id,
            user=c.rhodecode_user.user_id,
            pull_request=pull_request_id,
            f_path=request.POST.get('f_path'),
            line_no=request.POST.get('line'),
            status_change=(ChangesetStatus.get_status_lbl(status)
                           if status and allowed_to_change_status else None),
            closing_pr=close_pr
        )

        if allowed_to_change_status:
            old_calculated_status = pull_request.calculated_review_status()
            # get status if set !
            if status:
                ChangesetStatusModel().set_status(
                    c.rhodecode_db_repo.repo_id,
                    status,
                    c.rhodecode_user.user_id,
                    comm,
                    pull_request=pull_request_id
                )

            Session().flush()
            # we now calculate the status of pull request, and based on that
            # calculation we set the commits status
            calculated_status = pull_request.calculated_review_status()
            if old_calculated_status != calculated_status:
                PullRequestModel()._trigger_pull_request_hook(
                    pull_request, c.rhodecode_user, 'review_status_change')

            calculated_status_lbl = ChangesetStatus.get_status_lbl(
                calculated_status)

            if close_pr:
                status_completed = (
                    calculated_status in [ChangesetStatus.STATUS_APPROVED,
                                          ChangesetStatus.STATUS_REJECTED])
                if forced or status_completed:
                    PullRequestModel().close_pull_request(
                        pull_request_id, c.rhodecode_user)
                else:
                    h.flash(_('Closing pull request on other statuses than '
                              'rejected or approved is forbidden. '
                              'Calculated status from all reviewers '
                              'is currently: %s') % calculated_status_lbl,
                            category='warning')

        Session().commit()

        if not request.is_xhr:
            return redirect(h.url('pullrequest_show', repo_name=repo_name,
                                  pull_request_id=pull_request_id))

        data = {
            'target_id': h.safeid(h.safe_unicode(request.POST.get('f_path'))),
        }
        if comm:
            c.co = comm
            data.update(comm.get_dict())
            data.update({'rendered_text':
                             render('changeset/changeset_comment_block.html')})

        return data

    @LoginRequired()
    @NotAnonymous()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @auth.CSRFRequired()
    @jsonify
    def delete_comment(self, repo_name, comment_id):
        return self._delete_comment(comment_id)

    def _delete_comment(self, comment_id):
        comment_id = safe_int(comment_id)
        co = ChangesetComment.get_or_404(comment_id)
        if co.pull_request.is_closed():
            # don't allow deleting comments on closed pull request
            raise HTTPForbidden()

        is_owner = co.author.user_id == c.rhodecode_user.user_id
        is_repo_admin = h.HasRepoPermissionAny('repository.admin')(c.repo_name)
        if h.HasPermissionAny('hg.admin')() or is_repo_admin or is_owner:
            old_calculated_status = co.pull_request.calculated_review_status()
            ChangesetCommentsModel().delete(comment=co)
            Session().commit()
            calculated_status = co.pull_request.calculated_review_status()
            if old_calculated_status != calculated_status:
                PullRequestModel()._trigger_pull_request_hook(
                    co.pull_request, c.rhodecode_user, 'review_status_change')
            return True
        else:
            raise HTTPForbidden()
