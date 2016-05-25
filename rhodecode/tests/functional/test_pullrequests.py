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

import mock
import pytest
from webob.exc import HTTPNotFound

import rhodecode
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.model.changeset_status import ChangesetStatusModel
from rhodecode.model.db import (
    PullRequest, ChangesetStatus, UserLog, Notification)
from rhodecode.model.meta import Session
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.model.user import UserModel
from rhodecode.tests import assert_session_flash, url, TEST_USER_ADMIN_LOGIN
from rhodecode.tests.utils import AssertResponse


@pytest.mark.usefixtures('app', 'autologin_user')
@pytest.mark.backends("git", "hg")
class TestPullrequestsController:

    def test_index(self, backend):
        self.app.get(url(
            controller='pullrequests', action='index',
            repo_name=backend.repo_name))

    def test_option_menu_create_pull_request_exists(self, backend):
        repo_name = backend.repo_name
        response = self.app.get(url('summary_home', repo_name=repo_name))

        create_pr_link = '<a href="%s">Create Pull Request</a>' % url(
            'pullrequest', repo_name=repo_name)
        response.mustcontain(create_pr_link)

    def test_global_redirect_of_pr(self, backend, pr_util):
        pull_request = pr_util.create_pull_request()

        response = self.app.get(
            url('pull_requests_global',
                pull_request_id=pull_request.pull_request_id))

        repo_name = pull_request.target_repo.repo_name
        redirect_url = url('pullrequest_show', repo_name=repo_name,
                           pull_request_id=pull_request.pull_request_id)
        assert response.status == '302 Found'
        assert redirect_url in response.location

    @pytest.mark.xfail_backends(
        "git", reason="Pending bugfix/feature, issue #6")
    def test_create_pr_form_with_raw_commit_id(self, backend):
        repo = backend.repo

        self.app.get(
            url(controller='pullrequests', action='index',
                repo_name=repo.repo_name,
                commit=repo.get_commit().raw_id),
            status=200)

    @pytest.mark.parametrize('pr_merge_enabled', [True, False])
    def test_show(self, pr_util, pr_merge_enabled):
        pull_request = pr_util.create_pull_request(
            mergeable=pr_merge_enabled, enable_notifications=False)

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pull_request.target_repo.scm_instance().name,
            pull_request_id=str(pull_request.pull_request_id)))

        for commit_id in pull_request.revisions:
            response.mustcontain(commit_id)

        assert pull_request.target_ref_parts.type in response
        assert pull_request.target_ref_parts.name in response
        target_clone_url = pull_request.target_repo.clone_url()
        assert target_clone_url in response

        assert 'class="pull-request-merge"' in response
        assert (
            'Server-side pull request merging is disabled.'
            in response) != pr_merge_enabled

    def test_close_status_visibility(self, pr_util, csrf_token):
        from rhodecode.tests.functional.test_login import login_url, logut_url
        # Logout
        response = self.app.post(
            logut_url,
            params={'csrf_token': csrf_token})
        # Login as regular user
        response = self.app.post(login_url,
                                 {'username': 'test_regular',
                                  'password': 'test12'})

        pull_request = pr_util.create_pull_request(author='test_regular')

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pull_request.target_repo.scm_instance().name,
            pull_request_id=str(pull_request.pull_request_id)))

        assert 'Server-side pull request merging is disabled.' in response
        assert 'value="forced_closed"' in response

    def test_show_invalid_commit_id(self, pr_util):
        # Simulating invalid revisions which will cause a lookup error
        pull_request = pr_util.create_pull_request()
        pull_request.revisions = ['invalid']
        Session().add(pull_request)
        Session().commit()

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pull_request.target_repo.scm_instance().name,
            pull_request_id=str(pull_request.pull_request_id)))

        for commit_id in pull_request.revisions:
            response.mustcontain(commit_id)

    def test_show_invalid_source_reference(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request.source_ref = 'branch:b:invalid'
        Session().add(pull_request)
        Session().commit()

        self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pull_request.target_repo.scm_instance().name,
            pull_request_id=str(pull_request.pull_request_id)))

    def test_edit_title_description(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id

        response = self.app.post(
            url(controller='pullrequests', action='update',
                repo_name=pull_request.target_repo.repo_name,
                pull_request_id=str(pull_request_id)),
            params={
                'edit_pull_request': 'true',
                '_method': 'put',
                'title': 'New title',
                'description': 'New description',
                'csrf_token': csrf_token})

        assert_session_flash(
            response, u'Pull request title & description updated.',
            category='success')

        pull_request = PullRequest.get(pull_request_id)
        assert pull_request.title == 'New title'
        assert pull_request.description == 'New description'

    def test_edit_title_description_closed(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        pr_util.close()

        response = self.app.post(
            url(controller='pullrequests', action='update',
                repo_name=pull_request.target_repo.repo_name,
                pull_request_id=str(pull_request_id)),
            params={
                'edit_pull_request': 'true',
                '_method': 'put',
                'title': 'New title',
                'description': 'New description',
                'csrf_token': csrf_token})

        assert_session_flash(
            response, u'Cannot update closed pull requests.',
            category='error')

    def test_update_invalid_source_reference(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request()
        pull_request.source_ref = 'branch:invalid-branch:invalid-commit-id'
        Session().add(pull_request)
        Session().commit()

        pull_request_id = pull_request.pull_request_id

        response = self.app.post(
            url(controller='pullrequests', action='update',
                repo_name=pull_request.target_repo.repo_name,
                pull_request_id=str(pull_request_id)),
            params={'update_commits': 'true', '_method': 'put',
                    'csrf_token': csrf_token})

        assert_session_flash(
            response, u'Update failed due to missing commits.',
            category='error')

    def test_comment_and_close_pull_request(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request(approved=True)
        pull_request_id = pull_request.pull_request_id
        author = pull_request.user_id
        repo = pull_request.target_repo.repo_id

        self.app.post(
            url(controller='pullrequests',
                action='comment',
                repo_name=pull_request.target_repo.scm_instance().name,
                pull_request_id=str(pull_request_id)),
            params={
                'changeset_status':
                    ChangesetStatus.STATUS_APPROVED + '_closed',
                'change_changeset_status': 'on',
                'text': '',
                'csrf_token': csrf_token},
            status=302)

        action = 'user_closed_pull_request:%d' % pull_request_id
        journal = UserLog.query()\
            .filter(UserLog.user_id == author)\
            .filter(UserLog.repository_id == repo)\
            .filter(UserLog.action == action)\
            .all()
        assert len(journal) == 1

    def test_reject_and_close_pull_request(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        response = self.app.post(
            url(controller='pullrequests',
                action='update',
                repo_name=pull_request.target_repo.scm_instance().name,
                pull_request_id=str(pull_request.pull_request_id)),
            params={'close_pull_request': 'true', '_method': 'put',
                    'csrf_token': csrf_token})

        pull_request = PullRequest.get(pull_request_id)

        assert response.json is True
        assert pull_request.is_closed()

        # check only the latest status, not the review status
        status = ChangesetStatusModel().get_status(
            pull_request.source_repo, pull_request=pull_request)
        assert status == ChangesetStatus.STATUS_REJECTED

    def test_comment_force_close_pull_request(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        reviewers_ids = [1, 2]
        PullRequestModel().update_reviewers(pull_request_id, reviewers_ids)
        author = pull_request.user_id
        repo = pull_request.target_repo.repo_id
        self.app.post(
            url(controller='pullrequests',
                action='comment',
                repo_name=pull_request.target_repo.scm_instance().name,
                pull_request_id=str(pull_request_id)),
            params={
                'changeset_status': 'forced_closed',
                'csrf_token': csrf_token},
            status=302)

        pull_request = PullRequest.get(pull_request_id)

        action = 'user_closed_pull_request:%d' % pull_request_id
        journal = UserLog.query().filter(
            UserLog.user_id == author,
            UserLog.repository_id == repo,
            UserLog.action == action).all()
        assert len(journal) == 1

        # check only the latest status, not the review status
        status = ChangesetStatusModel().get_status(
            pull_request.source_repo, pull_request=pull_request)
        assert status == ChangesetStatus.STATUS_REJECTED

    def test_create_pull_request(self, backend, csrf_token):
        commits = [
            {'message': 'ancestor'},
            {'message': 'change'},
        ]
        commit_ids = backend.create_master_repo(commits)
        target = backend.create_repo(heads=['ancestor'])
        source = backend.create_repo(heads=['change'])

        response = self.app.post(
            url(
                controller='pullrequests',
                action='create',
                repo_name=source.repo_name),
            params={
                'source_repo': source.repo_name,
                'source_ref': 'branch:default:' + commit_ids['change'],
                'target_repo': target.repo_name,
                'target_ref': 'branch:default:' + commit_ids['ancestor'],
                'pullrequest_desc': 'Description',
                'pullrequest_title': 'Title',
                'review_members': '1',
                'revisions': commit_ids['change'],
                'user': '',
                'csrf_token': csrf_token,
            },
            status=302)

        location = response.headers['Location']
        pull_request_id = int(location.rsplit('/', 1)[1])
        pull_request = PullRequest.get(pull_request_id)

        # check that we have now both revisions
        assert pull_request.revisions == [commit_ids['change']]
        assert pull_request.source_ref == 'branch:default:' + commit_ids['change']
        expected_target_ref = 'branch:default:' + commit_ids['ancestor']
        assert pull_request.target_ref == expected_target_ref

    def test_reviewer_notifications(self, backend, csrf_token):
        # We have to use the app.post for this test so it will create the
        # notifications properly with the new PR
        commits = [
            {'message': 'ancestor',
             'added': [FileNode('file_A', content='content_of_ancestor')]},
            {'message': 'change',
             'added': [FileNode('file_a', content='content_of_change')]},
            {'message': 'change-child'},
            {'message': 'ancestor-child', 'parents': ['ancestor'],
             'added': [
                FileNode('file_B', content='content_of_ancestor_child')]},
            {'message': 'ancestor-child-2'},
        ]
        commit_ids = backend.create_master_repo(commits)
        target = backend.create_repo(heads=['ancestor-child'])
        source = backend.create_repo(heads=['change'])

        response = self.app.post(
            url(
                controller='pullrequests',
                action='create',
                repo_name=source.repo_name),
            params={
                'source_repo': source.repo_name,
                'source_ref': 'branch:default:' + commit_ids['change'],
                'target_repo': target.repo_name,
                'target_ref': 'branch:default:' + commit_ids['ancestor-child'],
                'pullrequest_desc': 'Description',
                'pullrequest_title': 'Title',
                'review_members': '2',
                'revisions': commit_ids['change'],
                'user': '',
                'csrf_token': csrf_token,
            },
            status=302)

        location = response.headers['Location']
        pull_request_id = int(location.rsplit('/', 1)[1])
        pull_request = PullRequest.get(pull_request_id)

        # Check that a notification was made
        notifications = Notification.query()\
            .filter(Notification.created_by == pull_request.author.user_id,
                    Notification.type_ == Notification.TYPE_PULL_REQUEST,
                    Notification.subject.contains("wants you to review "
                                                  "pull request #%d"
                                                  % pull_request_id))
        assert len(notifications.all()) == 1

        # Change reviewers and check that a notification was made
        PullRequestModel().update_reviewers(pull_request.pull_request_id, [1])
        assert len(notifications.all()) == 2

    def test_create_pull_request_stores_ancestor_commit_id(self, backend,
                                                           csrf_token):
        commits = [
            {'message': 'ancestor',
             'added': [FileNode('file_A', content='content_of_ancestor')]},
            {'message': 'change',
             'added': [FileNode('file_a', content='content_of_change')]},
            {'message': 'change-child'},
            {'message': 'ancestor-child', 'parents': ['ancestor'],
             'added': [
                FileNode('file_B', content='content_of_ancestor_child')]},
            {'message': 'ancestor-child-2'},
        ]
        commit_ids = backend.create_master_repo(commits)
        target = backend.create_repo(heads=['ancestor-child'])
        source = backend.create_repo(heads=['change'])

        response = self.app.post(
            url(
                controller='pullrequests',
                action='create',
                repo_name=source.repo_name),
            params={
                'source_repo': source.repo_name,
                'source_ref': 'branch:default:' + commit_ids['change'],
                'target_repo': target.repo_name,
                'target_ref': 'branch:default:' + commit_ids['ancestor-child'],
                'pullrequest_desc': 'Description',
                'pullrequest_title': 'Title',
                'review_members': '1',
                'revisions': commit_ids['change'],
                'user': '',
                'csrf_token': csrf_token,
            },
            status=302)

        location = response.headers['Location']
        pull_request_id = int(location.rsplit('/', 1)[1])
        pull_request = PullRequest.get(pull_request_id)

        # target_ref has to point to the ancestor's commit_id in order to
        # show the correct diff
        expected_target_ref = 'branch:default:' + commit_ids['ancestor']
        assert pull_request.target_ref == expected_target_ref

        # Check generated diff contents
        response = response.follow()
        assert 'content_of_ancestor' not in response.body
        assert 'content_of_ancestor-child' not in response.body
        assert 'content_of_change' in response.body

    def test_merge_pull_request_enabled(self, pr_util, csrf_token):
        # Clear any previous calls to rcextensions
        rhodecode.EXTENSIONS.calls.clear()

        pull_request = pr_util.create_pull_request(
            approved=True, mergeable=True)
        pull_request_id = pull_request.pull_request_id
        repo_name = pull_request.target_repo.scm_instance().name,

        response = self.app.post(
            url(controller='pullrequests',
                action='merge',
                repo_name=str(repo_name[0]),
                pull_request_id=str(pull_request_id)),
            params={'csrf_token': csrf_token}).follow()

        pull_request = PullRequest.get(pull_request_id)

        assert response.status_int == 200
        assert pull_request.is_closed()
        assert_pull_request_status(
            pull_request, ChangesetStatus.STATUS_APPROVED)

        # Check the relevant log entries were added
        user_logs = UserLog.query().order_by('-user_log_id').limit(4)
        actions = [log.action for log in user_logs]
        pr_commit_ids = PullRequestModel()._get_commit_ids(pull_request)
        expected_actions = [
            u'user_closed_pull_request:%d' % pull_request_id,
            u'user_merged_pull_request:%d' % pull_request_id,
            # The action below reflect that the post push actions were executed
            u'user_commented_pull_request:%d' % pull_request_id,
            u'push:%s' % ','.join(pr_commit_ids),
        ]
        assert actions == expected_actions

        # Check post_push rcextension was really executed
        push_calls = rhodecode.EXTENSIONS.calls['post_push']
        assert len(push_calls) == 1
        unused_last_call_args, last_call_kwargs = push_calls[0]
        assert last_call_kwargs['action'] == 'push'
        assert last_call_kwargs['pushed_revs'] == pr_commit_ids

    def test_merge_pull_request_disabled(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request(mergeable=False)
        pull_request_id = pull_request.pull_request_id
        pull_request = PullRequest.get(pull_request_id)

        response = self.app.post(
            url(controller='pullrequests',
                action='merge',
                repo_name=pull_request.target_repo.scm_instance().name,
                pull_request_id=str(pull_request.pull_request_id)),
            params={'csrf_token': csrf_token}).follow()

        assert response.status_int == 200
        assert 'Server-side pull request merging is disabled.' in response.body

    @pytest.mark.skip_backends('svn')
    def test_merge_pull_request_not_approved(self, pr_util, csrf_token):
        pull_request = pr_util.create_pull_request(mergeable=True)
        pull_request_id = pull_request.pull_request_id
        repo_name = pull_request.target_repo.scm_instance().name,

        response = self.app.post(
            url(controller='pullrequests',
                action='merge',
                repo_name=str(repo_name[0]),
                pull_request_id=str(pull_request_id)),
            params={'csrf_token': csrf_token}).follow()

        pull_request = PullRequest.get(pull_request_id)

        assert response.status_int == 200
        assert ' Reviewer approval is pending.' in response.body

    def test_update_source_revision(self, backend, csrf_token):
        commits = [
            {'message': 'ancestor'},
            {'message': 'change'},
            {'message': 'change-2'},
        ]
        commit_ids = backend.create_master_repo(commits)
        target = backend.create_repo(heads=['ancestor'])
        source = backend.create_repo(heads=['change'])

        # create pr from a in source to A in target
        pull_request = PullRequest()
        pull_request.source_repo = source
        # TODO: johbo: Make sure that we write the source ref this way!
        pull_request.source_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name, commit_id=commit_ids['change'])
        pull_request.target_repo = target

        pull_request.target_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name,
            commit_id=commit_ids['ancestor'])
        pull_request.revisions = [commit_ids['change']]
        pull_request.title = u"Test"
        pull_request.description = u"Description"
        pull_request.author = UserModel().get_by_username(
            TEST_USER_ADMIN_LOGIN)
        Session().add(pull_request)
        Session().commit()
        pull_request_id = pull_request.pull_request_id

        # source has ancestor - change - change-2
        backend.pull_heads(source, heads=['change-2'])

        # update PR
        self.app.post(
            url(controller='pullrequests', action='update',
                repo_name=target.repo_name,
                pull_request_id=str(pull_request_id)),
            params={'update_commits': 'true', '_method': 'put',
                    'csrf_token': csrf_token})

        # check that we have now both revisions
        pull_request = PullRequest.get(pull_request_id)
        assert pull_request.revisions == [
            commit_ids['change-2'], commit_ids['change']]

        # TODO: johbo: this should be a test on its own
        response = self.app.get(url(
            controller='pullrequests', action='index',
            repo_name=target.repo_name))
        assert response.status_int == 200
        assert 'Pull request updated to' in response.body
        assert 'with 1 added, 0 removed commits.' in response.body

    def test_update_target_revision(self, backend, csrf_token):
        commits = [
            {'message': 'ancestor'},
            {'message': 'change'},
            {'message': 'ancestor-new', 'parents': ['ancestor']},
            {'message': 'change-rebased'},
        ]
        commit_ids = backend.create_master_repo(commits)
        target = backend.create_repo(heads=['ancestor'])
        source = backend.create_repo(heads=['change'])

        # create pr from a in source to A in target
        pull_request = PullRequest()
        pull_request.source_repo = source
        # TODO: johbo: Make sure that we write the source ref this way!
        pull_request.source_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name, commit_id=commit_ids['change'])
        pull_request.target_repo = target
        # TODO: johbo: Target ref should be branch based, since tip can jump
        # from branch to branch
        pull_request.target_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name,
            commit_id=commit_ids['ancestor'])
        pull_request.revisions = [commit_ids['change']]
        pull_request.title = u"Test"
        pull_request.description = u"Description"
        pull_request.author = UserModel().get_by_username(
            TEST_USER_ADMIN_LOGIN)
        Session().add(pull_request)
        Session().commit()
        pull_request_id = pull_request.pull_request_id

        # target has ancestor - ancestor-new
        # source has ancestor - ancestor-new - change-rebased
        backend.pull_heads(target, heads=['ancestor-new'])
        backend.pull_heads(source, heads=['change-rebased'])

        # update PR
        self.app.post(
            url(controller='pullrequests', action='update',
                repo_name=target.repo_name,
                pull_request_id=str(pull_request_id)),
            params={'update_commits': 'true', '_method': 'put',
                    'csrf_token': csrf_token},
            status=200)

        # check that we have now both revisions
        pull_request = PullRequest.get(pull_request_id)
        assert pull_request.revisions == [commit_ids['change-rebased']]
        assert pull_request.target_ref == 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name,
            commit_id=commit_ids['ancestor-new'])

        # TODO: johbo: This should be a test on its own
        response = self.app.get(url(
            controller='pullrequests', action='index',
            repo_name=target.repo_name))
        assert response.status_int == 200
        assert 'Pull request updated to' in response.body
        assert 'with 1 added, 1 removed commits.' in response.body

    def test_update_of_ancestor_reference(self, backend, csrf_token):
        commits = [
            {'message': 'ancestor'},
            {'message': 'change'},
            {'message': 'change-2'},
            {'message': 'ancestor-new', 'parents': ['ancestor']},
            {'message': 'change-rebased'},
        ]
        commit_ids = backend.create_master_repo(commits)
        target = backend.create_repo(heads=['ancestor'])
        source = backend.create_repo(heads=['change'])

        # create pr from a in source to A in target
        pull_request = PullRequest()
        pull_request.source_repo = source
        # TODO: johbo: Make sure that we write the source ref this way!
        pull_request.source_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name,
            commit_id=commit_ids['change'])
        pull_request.target_repo = target
        # TODO: johbo: Target ref should be branch based, since tip can jump
        # from branch to branch
        pull_request.target_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name,
            commit_id=commit_ids['ancestor'])
        pull_request.revisions = [commit_ids['change']]
        pull_request.title = u"Test"
        pull_request.description = u"Description"
        pull_request.author = UserModel().get_by_username(
            TEST_USER_ADMIN_LOGIN)
        Session().add(pull_request)
        Session().commit()
        pull_request_id = pull_request.pull_request_id

        # target has ancestor - ancestor-new
        # source has ancestor - ancestor-new - change-rebased
        backend.pull_heads(target, heads=['ancestor-new'])
        backend.pull_heads(source, heads=['change-rebased'])

        # update PR
        self.app.post(
            url(controller='pullrequests', action='update',
                repo_name=target.repo_name,
                pull_request_id=str(pull_request_id)),
            params={'update_commits': 'true', '_method': 'put',
                    'csrf_token': csrf_token},
            status=200)

        # Expect the target reference to be updated correctly
        pull_request = PullRequest.get(pull_request_id)
        assert pull_request.revisions == [commit_ids['change-rebased']]
        expected_target_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name,
            commit_id=commit_ids['ancestor-new'])
        assert pull_request.target_ref == expected_target_ref

    def test_remove_pull_request_branch(self, backend_git, csrf_token):
        branch_name = 'development'
        commits = [
            {'message': 'initial-commit'},
            {'message': 'old-feature'},
            {'message': 'new-feature', 'branch': branch_name},
        ]
        repo = backend_git.create_repo(commits)
        commit_ids = backend_git.commit_ids

        pull_request = PullRequest()
        pull_request.source_repo = repo
        pull_request.target_repo = repo
        pull_request.source_ref = 'branch:{branch}:{commit_id}'.format(
            branch=branch_name, commit_id=commit_ids['new-feature'])
        pull_request.target_ref = 'branch:{branch}:{commit_id}'.format(
            branch=backend_git.default_branch_name,
            commit_id=commit_ids['old-feature'])
        pull_request.revisions = [commit_ids['new-feature']]
        pull_request.title = u"Test"
        pull_request.description = u"Description"
        pull_request.author = UserModel().get_by_username(
            TEST_USER_ADMIN_LOGIN)
        Session().add(pull_request)
        Session().commit()

        vcs = repo.scm_instance()
        vcs.remove_ref('refs/heads/{}'.format(branch_name))

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=repo.repo_name,
            pull_request_id=str(pull_request.pull_request_id)))

        assert response.status_int == 200
        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '#changeset_compare_view_content .alert strong',
            'Missing commits')
        assert_response.element_contains(
            '#changeset_compare_view_content .alert',
            'This pull request cannot be displayed, because one or more'
            ' commits no longer exist in the source repository.')

    def test_strip_commits_from_pull_request(
            self, backend, pr_util, csrf_token):
        commits = [
            {'message': 'initial-commit'},
            {'message': 'old-feature'},
            {'message': 'new-feature', 'parents': ['initial-commit']},
        ]
        pull_request = pr_util.create_pull_request(
            commits, target_head='initial-commit', source_head='new-feature',
            revisions=['new-feature'])

        vcs = pr_util.source_repository.scm_instance()
        if backend.alias == 'git':
            vcs.strip(pr_util.commit_ids['new-feature'], branch_name='master')
        else:
            vcs.strip(pr_util.commit_ids['new-feature'])

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pr_util.target_repository.repo_name,
            pull_request_id=str(pull_request.pull_request_id)))

        assert response.status_int == 200
        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '#changeset_compare_view_content .alert strong',
            'Missing commits')
        assert_response.element_contains(
            '#changeset_compare_view_content .alert',
            'This pull request cannot be displayed, because one or more'
            ' commits no longer exist in the source repository.')
        assert_response.element_contains(
            '#update_commits',
            'Update commits')

    def test_strip_commits_and_update(
            self, backend, pr_util, csrf_token):
        commits = [
            {'message': 'initial-commit'},
            {'message': 'old-feature'},
            {'message': 'new-feature', 'parents': ['old-feature']},
        ]
        pull_request = pr_util.create_pull_request(
            commits, target_head='old-feature', source_head='new-feature',
            revisions=['new-feature'], mergeable=True)

        vcs = pr_util.source_repository.scm_instance()
        if backend.alias == 'git':
            vcs.strip(pr_util.commit_ids['new-feature'], branch_name='master')
        else:
            vcs.strip(pr_util.commit_ids['new-feature'])

        response = self.app.post(
            url(controller='pullrequests', action='update',
                repo_name=pull_request.target_repo.repo_name,
                pull_request_id=str(pull_request.pull_request_id)),
            params={'update_commits': 'true', '_method': 'put',
                    'csrf_token': csrf_token})

        assert response.status_int == 200
        assert response.body == 'true'

        # Make sure that after update, it won't raise 500 errors
        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pr_util.target_repository.repo_name,
            pull_request_id=str(pull_request.pull_request_id)))

        assert response.status_int == 200
        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '#changeset_compare_view_content .alert strong',
            'Missing commits')

    def test_branch_is_a_link(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request.source_ref = 'branch:origin:1234567890abcdef'
        pull_request.target_ref = 'branch:target:abcdef1234567890'
        Session().add(pull_request)
        Session().commit()

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pull_request.target_repo.scm_instance().name,
            pull_request_id=str(pull_request.pull_request_id)))
        assert response.status_int == 200
        assert_response = AssertResponse(response)

        origin = assert_response.get_element('.pr-origininfo .tag')
        origin_children = origin.getchildren()
        assert len(origin_children) == 1
        target = assert_response.get_element('.pr-targetinfo .tag')
        target_children = target.getchildren()
        assert len(target_children) == 1

        expected_origin_link = url(
            'changelog_home',
            repo_name=pull_request.source_repo.scm_instance().name,
            branch='origin')
        expected_target_link = url(
            'changelog_home',
            repo_name=pull_request.target_repo.scm_instance().name,
            branch='target')
        assert origin_children[0].attrib['href'] == expected_origin_link
        assert origin_children[0].text == 'branch: origin'
        assert target_children[0].attrib['href'] == expected_target_link
        assert target_children[0].text == 'branch: target'

    def test_bookmark_is_not_a_link(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request.source_ref = 'bookmark:origin:1234567890abcdef'
        pull_request.target_ref = 'bookmark:target:abcdef1234567890'
        Session().add(pull_request)
        Session().commit()

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pull_request.target_repo.scm_instance().name,
            pull_request_id=str(pull_request.pull_request_id)))
        assert response.status_int == 200
        assert_response = AssertResponse(response)

        origin = assert_response.get_element('.pr-origininfo .tag')
        assert origin.text.strip() == 'bookmark: origin'
        assert origin.getchildren() == []

        target = assert_response.get_element('.pr-targetinfo .tag')
        assert target.text.strip() == 'bookmark: target'
        assert target.getchildren() == []

    def test_tag_is_not_a_link(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request.source_ref = 'tag:origin:1234567890abcdef'
        pull_request.target_ref = 'tag:target:abcdef1234567890'
        Session().add(pull_request)
        Session().commit()

        response = self.app.get(url(
            controller='pullrequests', action='show',
            repo_name=pull_request.target_repo.scm_instance().name,
            pull_request_id=str(pull_request.pull_request_id)))
        assert response.status_int == 200
        assert_response = AssertResponse(response)

        origin = assert_response.get_element('.pr-origininfo .tag')
        assert origin.text.strip() == 'tag: origin'
        assert origin.getchildren() == []

        target = assert_response.get_element('.pr-targetinfo .tag')
        assert target.text.strip() == 'tag: target'
        assert target.getchildren() == []

    def test_description_is_escaped_on_index_page(self, backend, pr_util):
        xss_description = "<script>alert('Hi!')</script>"
        pull_request = pr_util.create_pull_request(description=xss_description)
        response = self.app.get(url(
            controller='pullrequests', action='show_all',
            repo_name=pull_request.target_repo.repo_name))
        response.mustcontain(
            "&lt;script&gt;alert(&#39;Hi!&#39;)&lt;/script&gt;")


def assert_pull_request_status(pull_request, expected_status):
    status = ChangesetStatusModel().calculated_review_status(
        pull_request=pull_request)
    assert status == expected_status


@pytest.mark.parametrize('action', ['show_all', 'index', 'create'])
@pytest.mark.usefixtures("autologin_user")
def test_redirects_to_repo_summary_for_svn_repositories(
        backend_svn, app, action):
    denied_actions = ['show_all', 'index', 'create']
    for action in denied_actions:
        response = app.get(url(
            controller='pullrequests', action=action,
            repo_name=backend_svn.repo_name))
        assert response.status_int == 302

        # Not allowed, redirect to the summary
        redirected = response.follow()
        summary_url = url('summary_home', repo_name=backend_svn.repo_name)

        # URL adds leading slash and path doesn't have it
        assert redirected.req.path == summary_url


def test_delete_comment_returns_404_if_comment_does_not_exist(pylonsapp):
    # TODO: johbo: Global import not possible because models.forms blows up
    from rhodecode.controllers.pullrequests import PullrequestsController
    controller = PullrequestsController()
    patcher = mock.patch(
        'rhodecode.model.db.BaseModel.get', return_value=None)
    with pytest.raises(HTTPNotFound), patcher:
        controller._delete_comment(1)
