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

import pytest
from mock import Mock, patch
from pylons import url

from rhodecode.lib import base
from rhodecode.lib.vcs.exceptions import RepositoryRequirementError
from rhodecode.model import db


@pytest.mark.parametrize('result_key, expected_value', [
    ('username', 'stub_username'),
    ('action', 'stub_action'),
    ('repository', 'stub_repo_name'),
    ('scm', 'stub_scm'),
    ('hooks', ['stub_hook']),
    ('config', 'stub_ini_filename'),
    ('ip', 'fake_ip'),
    ('server_url', 'https://example.com'),
    # TODO: johbo: Commpare locking parameters with `_get_rc_scm_extras`
    # in hooks_utils.
    ('make_lock', None),
    ('locked_by', [None, None, None]),
])
def test_vcs_operation_context_parameters(result_key, expected_value):
    result = call_vcs_operation_context()
    assert result[result_key] == expected_value


@patch('rhodecode.model.db.User.get_by_username', Mock())
@patch('rhodecode.model.db.Repository.get_by_repo_name')
def test_vcs_operation_context_checks_locking(mock_get_by_repo_name):
    mock_get_locking_state = mock_get_by_repo_name().get_locking_state
    mock_get_locking_state.return_value = (None, None, [None, None, None])
    call_vcs_operation_context(check_locking=True)
    assert mock_get_locking_state.called


@patch('rhodecode.model.db.Repository.get_locking_state')
def test_vcs_operation_context_skips_locking_checks_if_anonymouse(
        mock_get_locking_state):
    call_vcs_operation_context(
        username=db.User.DEFAULT_USER, check_locking=True)
    assert not mock_get_locking_state.called


@patch('rhodecode.model.db.Repository.get_locking_state')
def test_vcs_operation_context_can_skip_locking_check(mock_get_locking_state):
    call_vcs_operation_context(check_locking=False)
    assert not mock_get_locking_state.called


@patch.object(
    base, 'get_enabled_hook_classes', Mock(return_value=['stub_hook']))
@patch.object(base, 'get_ip_addr', Mock(return_value="fake_ip"))
@patch('rhodecode.lib.utils2.get_server_url',
       Mock(return_value='https://example.com'))
def call_vcs_operation_context(**kwargs_override):
    kwargs = {
        'repo_name': 'stub_repo_name',
        'username': 'stub_username',
        'action': 'stub_action',
        'scm': 'stub_scm',
        'check_locking': False,
    }
    kwargs.update(kwargs_override)
    config_file_patch = patch.dict(
        'rhodecode.CONFIG', {'__file__': 'stub_ini_filename'})
    settings_patch = patch.object(base, 'VcsSettingsModel')
    with config_file_patch, settings_patch as settings_mock:
        result = base.vcs_operation_context(environ={}, **kwargs)
    settings_mock.assert_called_once_with(repo='stub_repo_name')
    return result


class TestBaseRepoController(object):
    def test_context_is_updated_when_update_global_counters_is_called(self):
        followers = 1
        forks = 2
        pull_requests = 3
        is_following = True
        scm_model = Mock(name="scm_model")
        db_repo = Mock(name="db_repo")
        scm_model.get_followers.return_value = followers
        scm_model.get_forks.return_value = forks
        scm_model.get_pull_requests.return_value = pull_requests
        scm_model.is_following_repo.return_value = is_following

        controller = base.BaseRepoController()
        with patch.object(base, 'c') as context_mock:
            controller._update_global_counters(scm_model, db_repo)

        scm_model.get_pull_requests.assert_called_once_with(db_repo)

        assert context_mock.repository_pull_requests == pull_requests


class TestBaseRepoControllerHandleMissingRequirements(object):
    def test_logs_error_and_sets_repo_to_none(self, app):
        controller = base.BaseRepoController()
        error_message = 'Some message'
        error = RepositoryRequirementError(error_message)
        context_patcher = patch.object(base, 'c')
        log_patcher = patch.object(base, 'log')
        request_patcher = patch.object(base, 'request')
        redirect_patcher = patch.object(base, 'redirect')
        controller.rhodecode_repo = 'something'

        with context_patcher as context_mock, log_patcher as log_mock, \
                request_patcher, redirect_patcher:
            context_mock.repo_name = 'abcde'
            controller._handle_missing_requirements(error)

        expected_log_message = (
            'Requirements are missing for repository %s: %s', 'abcde',
            error_message)
        log_mock.error.assert_called_once_with(*expected_log_message)

        assert controller.rhodecode_repo is None

    @pytest.mark.parametrize('path, should_redirect', [
        ('/abcde', False),
        ('/abcde/settings', False),
        ('/abcde/settings/vcs', False),
        ('/_admin/repos/abcde', False),  # Settings update
        ('/abcde/changelog', True),
        ('/abcde/files/tip', True),
        ('/abcde/settings/statistics', True),
    ])
    def test_redirects_if_not_summary_or_settings_page(
            self, app, path, should_redirect):
        repo_name = 'abcde'
        controller = base.BaseRepoController()
        error = RepositoryRequirementError('Some message')
        context_patcher = patch.object(base, 'c')
        controller.rhodecode_repo = repo_name
        request_patcher = patch.object(base, 'request')
        redirect_patcher = patch.object(base, 'redirect')

        with context_patcher as context_mock, \
                request_patcher as request_mock, \
                redirect_patcher as redirect_mock:
            request_mock.path = path
            context_mock.repo_name = repo_name
            controller._handle_missing_requirements(error)

        expected_url = url('summary_home', repo_name=repo_name)
        if should_redirect:
            redirect_mock.assert_called_once_with(expected_url)
        else:
            redirect_mock.call_count == 0


class TestBaseRepoControllerBefore(object):
    def test_flag_is_true_when_requirements_are_missing(self, before_mocks):
        controller = self._get_controller()

        handle_patcher = patch.object(
            controller, '_handle_missing_requirements')

        error = RepositoryRequirementError()
        before_mocks.repository.scm_instance.side_effect = error

        with handle_patcher as handle_mock:
            controller.__before__()

        handle_mock.assert_called_once_with(error)
        assert before_mocks['context'].repository_requirements_missing is True

    def test_flag_is_false_when_no_requirements_are_missing(
            self, before_mocks):
        controller = self._get_controller()

        handle_patcher = patch.object(
            controller, '_handle_missing_requirements')
        with handle_patcher as handle_mock:
            controller.__before__()
        handle_mock.call_count == 0
        assert before_mocks['context'].repository_requirements_missing is False

    def test_update_global_counters_is_called(self, before_mocks):
        controller = self._get_controller()

        update_counters_patcher = patch.object(
            controller, '_update_global_counters')

        with update_counters_patcher as update_counters_mock:
            controller.__before__()
        update_counters_mock.assert_called_once_with(
            controller.scm_model, before_mocks.repository)

    def _get_controller(self):
        controller = base.BaseRepoController()
        controller.scm_model = Mock()
        controller.rhodecode_repo = Mock()
        return controller


@pytest.fixture
def before_mocks(request):
    patcher = BeforePatcher()
    patcher.start()
    request.addfinalizer(patcher.stop)
    return patcher


class BeforePatcher(object):
    patchers = {}
    mocks = {}
    repository = None

    def __init__(self):
        self.repository = Mock()

    def start(self):
        self.patchers = {
            'request': patch.object(base, 'request'),
            'before': patch.object(base.BaseController, '__before__'),
            'context': patch.object(base, 'c'),
            'repo': patch.object(
                base.Repository, 'get_by_repo_name',
                return_value=self.repository)

        }
        self.mocks = {
            p: self.patchers[p].start() for p in self.patchers
        }

    def stop(self):
        for patcher in self.patchers.values():
            patcher.stop()

    def __getitem__(self, key):
        return self.mocks[key]
