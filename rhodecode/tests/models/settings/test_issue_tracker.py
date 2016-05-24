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

from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel, IssueTrackerSettingsModel


class TestIssueTrackerSettingsModel(object):
    def test_get_global_settings(self):
        model = IssueTrackerSettingsModel()
        input_settings = {
            'rhodecode_issuetracker_pat_123': 'pat',
            'rhodecode_issuetracker_url_123': 'url',
            'rhodecode_issuetracker_desc_123': 'desc',
            'rhodecode_issuetracker_pref_123': 'pref',
        }
        expected_result = {
            '123': {
                'desc': 'desc', 'pat': 'pat', 'pref': 'pref', 'url': 'url'}}
        with mock.patch.object(model, 'global_settings') as settings_mock:
            get_settings = settings_mock.get_all_settings
            get_settings.return_value = input_settings
            settings_mock.return_value = input_settings
            result = model.get_global_settings(cache=True)
        get_settings.assert_called_once_with(cache=True)
        assert expected_result == result

    def test_get_repo_settings_raise_exception_when_repo_is_not_set(self):
        model = IssueTrackerSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.get_repo_settings(cache=True)
        assert exc_info.value.message == 'Repository is not specified'

    def test_get_repo_settings(self, repo_stub):
        model = IssueTrackerSettingsModel(repo=repo_stub.repo_name)
        input_settings = {
            'rhodecode_issuetracker_pat_123': 'pat',
            'rhodecode_issuetracker_url_123': 'url',
            'rhodecode_issuetracker_desc_123': 'desc',
            'rhodecode_issuetracker_pref_123': 'pref',
        }
        expected_result = {
            '123': {
                'desc': 'desc', 'pat': 'pat', 'pref': 'pref', 'url': 'url'}}
        with mock.patch.object(model, 'repo_settings') as settings_mock:
            get_settings = settings_mock.get_all_settings
            get_settings.return_value = input_settings
            settings_mock.return_value = input_settings
            result = model.get_repo_settings(cache=True)
        get_settings.assert_called_once_with(cache=True)
        assert expected_result == result

    @pytest.mark.parametrize("inherit_settings, method", [
        (True, 'get_global_settings'),
        (False, 'get_repo_settings')
    ])
    def test_effective_settings(self, inherit_settings, method):
        model = IssueTrackerSettingsModel()
        expected_result = {'test': 'test'}
        inherit_patch = mock.patch(
            'rhodecode.model.settings.IssueTrackerSettingsModel'
            '.inherit_global_settings', inherit_settings)
        settings_patch = mock.patch.object(
            model, method, return_value=expected_result)
        with inherit_patch, settings_patch as settings_mock:
            result = model.get_settings(cache=True)
        settings_mock.assert_called_once_with(cache=True)
        assert result == expected_result


class TestInheritIssueTrackerSettingsProperty(object):
    def test_true_is_returned_when_repository_not_specified(self):
        model = IssueTrackerSettingsModel()
        assert model.inherit_global_settings is True

    def test_true_is_returned_when_value_is_not_found(self, repo_stub):
        model = IssueTrackerSettingsModel(repo=repo_stub.repo_name)
        assert model.inherit_global_settings is True

    def test_value_is_returned(self, repo_stub, settings_util):
        model = IssueTrackerSettingsModel(repo=repo_stub.repo_name)
        settings_util.create_repo_rhodecode_setting(
            repo_stub, IssueTrackerSettingsModel.INHERIT_SETTINGS, False,
            'bool')
        assert model.inherit_global_settings is False

    def test_value_is_set(self, repo_stub):
        model = IssueTrackerSettingsModel(repo=repo_stub.repo_name)
        model.inherit_global_settings = False
        setting = model.repo_settings.get_setting_by_name(
            IssueTrackerSettingsModel.INHERIT_SETTINGS)
        try:
            assert setting.app_settings_type == 'bool'
            assert setting.app_settings_value is False
        finally:
            Session().delete(setting)
            Session().commit()

    def test_value_is_not_set_when_repository_is_not_specified(
            self, repo_stub):
        it_model = IssueTrackerSettingsModel()
        it_model.inherit_global_settings = False
        settings_model = SettingsModel(repo=repo_stub.repo_name)
        setting = settings_model.get_setting_by_name(
            IssueTrackerSettingsModel.INHERIT_SETTINGS)
        assert setting is None
        global_setting = it_model.global_settings.get_setting_by_name(
            IssueTrackerSettingsModel.INHERIT_SETTINGS)
        assert global_setting is None
