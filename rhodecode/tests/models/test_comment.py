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

from rhodecode.lib.diffs import DiffLineNumber
from rhodecode.model import comment


@pytest.mark.parametrize('value, expected', [
    ('o1', DiffLineNumber(1, None)),
    ('o798', DiffLineNumber(798, None)),
    ('n1', DiffLineNumber(None, 1)),
    ('n100000', DiffLineNumber(None, 100000)),
])
def test_parse_comment_line_number(value, expected):
    result = comment._parse_comment_line_number(value)
    assert result == expected


@pytest.mark.parametrize('value, should_raise', [
    (None, AttributeError),
    ('2', ValueError),
    ('first_line', ValueError),
    ('olast_line', ValueError),
])
def test_parse_comment_line_number_raises(value, should_raise):
    with pytest.raises(should_raise):
        comment._parse_comment_line_number(value)


@pytest.mark.parametrize('old, new, expected', [
    (None, 1, 'n1'),
    (None, 2, 'n2'),
    (None, 10, 'n10'),
    (1, None, 'o1'),
    (10, None, 'o10'),
    # Ensuring consistent behavior, although there is no line 0 used.
    (None, 0, 'n0'),
    (0, None, 'o0'),
    # Using the empty string to reflect what the comment model does
    (None, None, ''),
    # Give a preference to the new line number if both are given
    (1, 1, 'n1'),
])
def test_diff_to_comment_line_number(old, new, expected):
    diff_line = DiffLineNumber(old=old, new=new)
    comment_line = comment._diff_to_comment_line_number(diff_line)
    assert comment_line == expected


@pytest.mark.parametrize('diff_line, expected', [
    (DiffLineNumber(old=1, new=None), DiffLineNumber(old=2, new=None)),
    (DiffLineNumber(old=11, new=None), DiffLineNumber(old=2, new=None)),
    (DiffLineNumber(old=12, new=None), DiffLineNumber(old=21, new=None)),
])
def test_choose_closest_diff_line_normal(diff_line, expected):
    comment_model = comment.ChangesetCommentsModel()
    candidates = [
        DiffLineNumber(old=2, new=None),
        DiffLineNumber(old=21, new=None),
    ]
    result = comment_model._choose_closest_diff_line(diff_line, candidates)
    assert result == expected


def test_revision_comments_are_sorted():
    comment_model = comment.ChangesetCommentsModel()
    query = comment_model._get_inline_comments_query(
        repo_id='fake_repo_name',
        revision='fake_revision',
        pull_request=None)
    assert_inline_comments_order(query)


@pytest.mark.parametrize('use_outdated', [True, False])
def test_pull_request_comments_are_sorted(use_outdated):
    comment_model = comment.ChangesetCommentsModel()
    pull_request = mock.Mock()
    # TODO: johbo: Had to do this since we have an inline call to
    # self.__get_pull_request. Should be moved out at some point.
    get_instance_patcher = mock.patch.object(
        comment.ChangesetCommentsModel, '_get_instance',
        return_value=pull_request)
    config_patcher = mock.patch.object(
        comment.ChangesetCommentsModel, 'use_outdated_comments',
        return_value=use_outdated)

    with get_instance_patcher, config_patcher as config_mock:
        query = comment_model._get_inline_comments_query(
            repo_id='fake_repo_name',
            revision=None,
            pull_request=pull_request)
    config_mock.assert_called_once_with(pull_request)
    assert_inline_comments_order(query)


def assert_inline_comments_order(query):
    """
    Sorting by ID will make sure that the latest comments are at the bottom.
    """
    order_by = query._order_by
    assert order_by
    assert len(order_by) == 1
    assert str(order_by[0]) == 'changeset_comments.comment_id ASC'


def test_get_renderer():
    model = comment.ChangesetCommentsModel()
    renderer = model._get_renderer()
    assert renderer == "rst"


class TestUseOutdatedComments(object):
    @pytest.mark.parametrize('use_outdated', [True, False])
    def test_returns_value_from_db(self, use_outdated):
        pull_request = mock.Mock()

        general_settings = {
            'rhodecode_use_outdated_comments': use_outdated
        }
        with self._patch_settings(general_settings) as settings_mock:
            result = comment.ChangesetCommentsModel.use_outdated_comments(
                pull_request)
        settings_mock.assert_called_once_with(repo=pull_request.target_repo)
        assert result == use_outdated

    def test_default_value(self):
        pull_request = mock.Mock()

        general_settings = {}
        with self._patch_settings(general_settings) as settings_mock:
            result = comment.ChangesetCommentsModel.use_outdated_comments(
                pull_request)
        settings_mock.assert_called_once_with(repo=pull_request.target_repo)
        assert result is False

    def _patch_settings(self, value):
        vcs_settings_mock = mock.Mock()
        vcs_settings_mock.get_general_settings.return_value = value
        return mock.patch.object(
            comment, 'VcsSettingsModel', return_value=vcs_settings_mock)
