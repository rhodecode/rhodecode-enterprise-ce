import collections

import pytest

from rhodecode.lib.utils import PartialRenderer
from rhodecode.model.notification import EmailNotificationModel


def test_get_template_obj(pylonsapp):
    template = EmailNotificationModel().get_renderer(
        EmailNotificationModel.TYPE_TEST)
    assert isinstance(template, PartialRenderer)


def test_render_email(pylonsapp):
    kwargs = {}
    subject, headers, body, body_plaintext = EmailNotificationModel().render_email(
        EmailNotificationModel.TYPE_TEST, **kwargs)

    # subject
    assert subject == 'Test "Subject" hello "world"'

    # headers
    assert headers == 'X=Y'

    # body plaintext
    assert body_plaintext == 'Email Plaintext Body'

    # body
    assert '<b>This is a notification ' \
           'from RhodeCode. http://test.example.com:80/</b>' in body
    assert '<b>Email Body' in body


def test_render_pr_email(pylonsapp, user_admin):

    ref = collections.namedtuple('Ref',
        'name, type')(
        'fxies123', 'book'
        )

    pr = collections.namedtuple('PullRequest',
        'pull_request_id, title, description, source_ref_parts, source_ref_name, target_ref_parts, target_ref_name')(
        200, 'Example Pull Request', 'Desc of PR', ref, 'bookmark', ref, 'Branch')

    source_repo = target_repo = collections.namedtuple('Repo',
        'type, repo_name')(
        'hg', 'pull_request_1')

    kwargs = {
        'user': '<marcin@rhodecode.com> Marcin Kuzminski',
        'pull_request': pr,
        'pull_request_commits': [],

        'pull_request_target_repo': target_repo,
        'pull_request_target_repo_url': 'x',

        'pull_request_source_repo': source_repo,
        'pull_request_source_repo_url': 'x',

        'pull_request_url': 'http://localhost/pr1',
    }

    subject, headers, body, body_plaintext = EmailNotificationModel().render_email(
        EmailNotificationModel.TYPE_PULL_REQUEST, **kwargs)

    # subject
    assert subject == 'Marcin Kuzminski wants you to review pull request #200: "Example Pull Request"'
