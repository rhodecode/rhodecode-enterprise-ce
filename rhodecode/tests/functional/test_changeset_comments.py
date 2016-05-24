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

from pylons.i18n import ungettext
import pytest

from rhodecode.tests import *
from rhodecode.model.db import (
    ChangesetComment, Notification, UserNotification)
from rhodecode.model.meta import Session


@pytest.mark.backends("git", "hg", "svn")
class TestChangeSetCommentsController(TestController):

    @pytest.fixture(autouse=True)
    def prepare(self, request, pylonsapp):
        for x in ChangesetComment.query().all():
            Session().delete(x)
        Session().commit()

        for x in Notification.query().all():
            Session().delete(x)
        Session().commit()

        request.addfinalizer(self.cleanup)

    def cleanup(self):
        for x in ChangesetComment.query().all():
            Session().delete(x)
        Session().commit()

        for x in Notification.query().all():
            Session().delete(x)
        Session().commit()

    def test_create(self, backend):
        self.log_user()
        commit_id = backend.repo.get_commit('300').raw_id
        text = u'CommentOnCommit'

        params = {'text': text, 'csrf_token': self.csrf_token}
        self.app.post(
            url(controller='changeset', action='comment',
                repo_name=backend.repo_name, revision=commit_id), params=params)

        response = self.app.get(
            url(controller='changeset', action='index',
                repo_name=backend.repo_name, revision=commit_id))

        # test DB
        assert ChangesetComment.query().count() == 1
        assert_comment_links(response, ChangesetComment.query().count(), 0)

        assert Notification.query().count() == 1
        assert ChangesetComment.query().count() == 1

        notification = Notification.query().all()[0]

        comment_id = ChangesetComment.query().first().comment_id
        assert notification.type_ == Notification.TYPE_CHANGESET_COMMENT

        sbj = 'commented on commit of {0}'.format(backend.repo_name)
        assert sbj in notification.subject

        lnk = (u'/{0}/changeset/{1}#comment-{2}'.format(
            backend.repo_name, commit_id, comment_id))
        assert lnk in notification.body

    def test_create_inline(self, backend):
        self.log_user()
        commit_id = backend.repo.get_commit('300').raw_id
        text = u'CommentOnCommit'
        f_path = 'vcs/web/simplevcs/views/repository.py'
        line = 'n1'

        params = {'text': text, 'f_path': f_path, 'line': line,
                  'csrf_token': self.csrf_token}

        self.app.post(
            url(controller='changeset', action='comment',
                repo_name=backend.repo_name, revision=commit_id), params=params)

        response = self.app.get(
            url(controller='changeset', action='index',
                repo_name=backend.repo_name, revision=commit_id))

        # test DB
        assert ChangesetComment.query().count() == 1
        assert_comment_links(response, 0, ChangesetComment.query().count())
        response.mustcontain(
            '''class="inline-comment-placeholder" '''
            '''path="vcs/web/simplevcs/views/repository.py" '''
            '''target_id="vcswebsimplevcsviewsrepositorypy"'''
        )

        assert Notification.query().count() == 1
        assert ChangesetComment.query().count() == 1

        notification = Notification.query().all()[0]
        comment = ChangesetComment.query().first()
        assert notification.type_ == Notification.TYPE_CHANGESET_COMMENT

        assert comment.revision == commit_id

        sbj = 'commented on commit of {0}'.format(backend.repo_name)
        assert sbj in notification.subject

        lnk = (u'/{0}/changeset/{1}#comment-{2}'.format(
            backend.repo_name, commit_id, comment.comment_id))
        assert lnk in notification.body
        assert 'on line n1' in notification.body

    def test_create_with_mention(self, backend):
        self.log_user()

        commit_id = backend.repo.get_commit('300').raw_id
        text = u'@test_regular check CommentOnCommit'

        params = {'text': text, 'csrf_token': self.csrf_token}
        self.app.post(
            url(controller='changeset', action='comment',
                repo_name=backend.repo_name, revision=commit_id), params=params)

        response = self.app.get(
            url(controller='changeset', action='index',
                repo_name=backend.repo_name, revision=commit_id))
        # test DB
        assert ChangesetComment.query().count() == 1
        assert_comment_links(response, ChangesetComment.query().count(), 0)

        notification = Notification.query().one()

        assert len(notification.recipients) == 2
        users = [x.username for x in notification.recipients]

        # test_regular gets notification by @mention
        assert sorted(users) == [u'test_admin', u'test_regular']

    def test_delete(self, backend):
        self.log_user()
        commit_id = backend.repo.get_commit('300').raw_id
        text = u'CommentOnCommit'

        params = {'text': text, 'csrf_token': self.csrf_token}
        self.app.post(
            url(
                controller='changeset', action='comment',
                repo_name=backend.repo_name, revision=commit_id),
            params=params)

        comments = ChangesetComment.query().all()
        assert len(comments) == 1
        comment_id = comments[0].comment_id

        self.app.post(
            url(controller='changeset', action='delete_comment',
                repo_name=backend.repo_name, comment_id=comment_id),
            params={'_method': 'delete', 'csrf_token': self.csrf_token})

        comments = ChangesetComment.query().all()
        assert len(comments) == 0

        response = self.app.get(
            url(controller='changeset', action='index',
                repo_name=backend.repo_name, revision=commit_id))
        assert_comment_links(response, 0, 0)

    @pytest.mark.parametrize('renderer, input, output', [
        ('rst', 'plain text', '<p>plain text</p>'),
        ('rst', 'header\n======', '<h1 class="title">header</h1>'),
        ('rst', '*italics*', '<em>italics</em>'),
        ('rst', '**bold**', '<strong>bold</strong>'),
        ('markdown', 'plain text', '<p>plain text</p>'),
        ('markdown', '# header', '<h1>header</h1>'),
        ('markdown', '*italics*', '<em>italics</em>'),
        ('markdown', '**bold**', '<strong>bold</strong>'),
    ])
    def test_preview(self, renderer, input, output, backend):
        self.log_user()
        params = {
            'renderer': renderer,
            'text': input,
            'csrf_token': self.csrf_token
        }
        environ = {
            'HTTP_X_PARTIAL_XHR': 'true'
        }
        response = self.app.post(
            url(controller='changeset',
                action='preview_comment',
                repo_name=backend.repo_name),
            params=params,
            extra_environ=environ)

        response.mustcontain(output)


def assert_comment_links(response, comments, inline_comments):
    comments_text = ungettext("%d Commit comment",
                              "%d Commit comments", comments) % comments
    if comments:
        response.mustcontain('<a href="#comments">%s</a>,' % comments_text)
    else:
        response.mustcontain(comments_text)

    inline_comments_text = ungettext("%d Inline Comment", "%d Inline Comments",
                                     inline_comments) % inline_comments
    if inline_comments:
        response.mustcontain(
            '<a href="#inline-comments" '
            'id="inline-comments-counter">%s</a>' % inline_comments_text)
    else:
        response.mustcontain(inline_comments_text)
