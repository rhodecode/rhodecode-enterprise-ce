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

from rhodecode.lib.utils2 import str2bool
from rhodecode.model.meta import Session
from rhodecode.model.settings import VcsSettingsModel, UiSetting


HOOKS_FORM_DATA = {
    'hooks_changegroup_repo_size': True,
    'hooks_changegroup_push_logger': True,
    'hooks_outgoing_pull_logger': True
}

SVN_FORM_DATA = {
    'new_svn_branch': 'test-branch',
    'new_svn_tag': 'test-tag'
}

GENERAL_FORM_DATA = {
    'rhodecode_pr_merge_enabled': True,
    'rhodecode_use_outdated_comments': True
}


class TestInheritGlobalSettingsProperty(object):
    def test_get_raises_exception_when_repository_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.inherit_global_settings
        assert exc_info.value.message == 'Repository is not specified'

    def test_true_is_returned_when_value_is_not_found(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        assert model.inherit_global_settings is True

    def test_value_is_returned(self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        settings_util.create_repo_rhodecode_setting(
            repo_stub, VcsSettingsModel.INHERIT_SETTINGS, False, 'bool')
        assert model.inherit_global_settings is False

    def test_value_is_set(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model.inherit_global_settings = False
        setting = model.repo_settings.get_setting_by_name(
            VcsSettingsModel.INHERIT_SETTINGS)
        try:
            assert setting.app_settings_type == 'bool'
            assert setting.app_settings_value is False
        finally:
            Session().delete(setting)
            Session().commit()

    def test_set_raises_exception_when_repository_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.inherit_global_settings = False
        assert exc_info.value.message == 'Repository is not specified'


class TestVcsSettingsModel(object):
    def test_global_svn_branch_patterns(self):
        model = VcsSettingsModel()
        expected_result = {'test': 'test'}
        with mock.patch.object(model, 'global_settings') as settings_mock:
            get_settings = settings_mock.get_ui_by_section
            get_settings.return_value = expected_result
            settings_mock.return_value = expected_result
            result = model.get_global_svn_branch_patterns()

        get_settings.assert_called_once_with(model.SVN_BRANCH_SECTION)
        assert expected_result == result

    def test_repo_svn_branch_patterns(self):
        model = VcsSettingsModel()
        expected_result = {'test': 'test'}
        with mock.patch.object(model, 'repo_settings') as settings_mock:
            get_settings = settings_mock.get_ui_by_section
            get_settings.return_value = expected_result
            settings_mock.return_value = expected_result
            result = model.get_repo_svn_branch_patterns()

        get_settings.assert_called_once_with(model.SVN_BRANCH_SECTION)
        assert expected_result == result

    def test_repo_svn_branch_patterns_raises_exception_when_repo_is_not_set(
            self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.get_repo_svn_branch_patterns()
        assert exc_info.value.message == 'Repository is not specified'

    def test_global_svn_tag_patterns(self):
        model = VcsSettingsModel()
        expected_result = {'test': 'test'}
        with mock.patch.object(model, 'global_settings') as settings_mock:
            get_settings = settings_mock.get_ui_by_section
            get_settings.return_value = expected_result
            settings_mock.return_value = expected_result
            result = model.get_global_svn_tag_patterns()

        get_settings.assert_called_once_with(model.SVN_TAG_SECTION)
        assert expected_result == result

    def test_repo_svn_tag_patterns(self):
        model = VcsSettingsModel()
        expected_result = {'test': 'test'}
        with mock.patch.object(model, 'repo_settings') as settings_mock:
            get_settings = settings_mock.get_ui_by_section
            get_settings.return_value = expected_result
            settings_mock.return_value = expected_result
            result = model.get_repo_svn_tag_patterns()

        get_settings.assert_called_once_with(model.SVN_TAG_SECTION)
        assert expected_result == result

    def test_repo_svn_tag_patterns_raises_exception_when_repo_is_not_set(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.get_repo_svn_tag_patterns()
        assert exc_info.value.message == 'Repository is not specified'

    def test_get_global_settings(self):
        expected_result = {'test': 'test'}
        model = VcsSettingsModel()
        with mock.patch.object(model, '_collect_all_settings') as collect_mock:
            collect_mock.return_value = expected_result
            result = model.get_global_settings()

        collect_mock.assert_called_once_with(global_=True)
        assert result == expected_result

    def test_get_repo_settings(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        expected_result = {'test': 'test'}
        with mock.patch.object(model, '_collect_all_settings') as collect_mock:
            collect_mock.return_value = expected_result
            result = model.get_repo_settings()

        collect_mock.assert_called_once_with(global_=False)
        assert result == expected_result

    @pytest.mark.parametrize('settings, global_', [
        ('global_settings', True),
        ('repo_settings', False)
    ])
    def test_collect_all_settings(self, settings, global_):
        model = VcsSettingsModel()
        result_mock = self._mock_result()

        settings_patch = mock.patch.object(model, settings)
        with settings_patch as settings_mock:
            settings_mock.get_ui_by_section_and_key.return_value = result_mock
            settings_mock.get_setting_by_name.return_value = result_mock
            result = model._collect_all_settings(global_=global_)

        ui_settings = model.HG_SETTINGS + model.HOOKS_SETTINGS
        self._assert_get_settings_calls(
            settings_mock, ui_settings, model.GENERAL_SETTINGS)
        self._assert_collect_all_settings_result(
            ui_settings, model.GENERAL_SETTINGS, result)

    @pytest.mark.parametrize('settings, global_', [
        ('global_settings', True),
        ('repo_settings', False)
    ])
    def test_collect_all_settings_without_empty_value(self, settings, global_):
        model = VcsSettingsModel()

        settings_patch = mock.patch.object(model, settings)
        with settings_patch as settings_mock:
            settings_mock.get_ui_by_section_and_key.return_value = None
            settings_mock.get_setting_by_name.return_value = None
            result = model._collect_all_settings(global_=global_)

        assert result == {}

    def _mock_result(self):
        result_mock = mock.Mock()
        result_mock.ui_value = 'ui_value'
        result_mock.ui_active = True
        result_mock.app_settings_value = 'setting_value'
        return result_mock

    def _assert_get_settings_calls(
            self, settings_mock, ui_settings, general_settings):
        assert (
            settings_mock.get_ui_by_section_and_key.call_count ==
            len(ui_settings))
        assert (
            settings_mock.get_setting_by_name.call_count ==
            len(general_settings))

        for section, key in ui_settings:
            expected_call = mock.call(section, key)
            assert (
                expected_call in
                settings_mock.get_ui_by_section_and_key.call_args_list)

        for name in general_settings:
            expected_call = mock.call(name)
            assert (
                expected_call in
                settings_mock.get_setting_by_name.call_args_list)

    def _assert_collect_all_settings_result(
            self, ui_settings, general_settings, result):
        expected_result = {}
        for section, key in ui_settings:
            key = '{}_{}'.format(section, key.replace('.', '_'))
            value = True if section in ('extensions', 'hooks') else 'ui_value'
            expected_result[key] = value

        for name in general_settings:
            key = 'rhodecode_' + name
            expected_result[key] = 'setting_value'

        assert expected_result == result


class TestCreateOrUpdateRepoHookSettings(object):
    def test_create_when_no_repo_object_found(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)

        self._create_settings(model, HOOKS_FORM_DATA)

        cleanup = []
        try:
            for section, key in model.HOOKS_SETTINGS:
                ui = model.repo_settings.get_ui_by_section_and_key(
                    section, key)
                assert ui.ui_active is True
                cleanup.append(ui)
        finally:
            for ui in cleanup:
                Session().delete(ui)
            Session().commit()

    def test_create_raises_exception_when_data_incomplete(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)

        deleted_key = 'hooks_changegroup_repo_size'
        data = HOOKS_FORM_DATA.copy()
        data.pop(deleted_key)

        with pytest.raises(ValueError) as exc_info:
            model.create_or_update_repo_hook_settings(data)
        assert (
            exc_info.value.message ==
            'The given data does not contain {} key'.format(deleted_key))

    def test_update_when_repo_object_found(self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        for section, key in model.HOOKS_SETTINGS:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, None, key=key, active=False)
        model.create_or_update_repo_hook_settings(HOOKS_FORM_DATA)
        for section, key in model.HOOKS_SETTINGS:
            ui = model.repo_settings.get_ui_by_section_and_key(section, key)
            assert ui.ui_active is True

    def _create_settings(self, model, data):
        global_patch = mock.patch.object(model, 'global_settings')
        global_setting = mock.Mock()
        global_setting.ui_value = 'Test value'
        with global_patch as global_mock:
            global_mock.get_ui_by_section_and_key.return_value = global_setting
            model.create_or_update_repo_hook_settings(HOOKS_FORM_DATA)


class TestUpdateGlobalHookSettings(object):
    def test_update_raises_exception_when_data_incomplete(self):
        model = VcsSettingsModel()

        deleted_key = 'hooks_changegroup_repo_size'
        data = HOOKS_FORM_DATA.copy()
        data.pop(deleted_key)

        with pytest.raises(ValueError) as exc_info:
            model.update_global_hook_settings(data)
        assert (
            exc_info.value.message ==
            'The given data does not contain {} key'.format(deleted_key))

    def test_update_global_hook_settings(self, settings_util):
        model = VcsSettingsModel()
        setting_mock = mock.MagicMock()
        setting_mock.ui_active = False
        get_settings_patcher = mock.patch.object(
            model.global_settings, 'get_ui_by_section_and_key',
            return_value=setting_mock)
        session_patcher = mock.patch('rhodecode.model.settings.Session')
        with get_settings_patcher as get_settings_mock, session_patcher:
            model.update_global_hook_settings(HOOKS_FORM_DATA)
        assert setting_mock.ui_active is True
        assert get_settings_mock.call_count == 3


class TestCreateOrUpdateRepoGeneralSettings(object):
    def test_calls_create_or_update_general_settings(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        create_patch = mock.patch.object(
            model, '_create_or_update_general_settings')
        with create_patch as create_mock:
            model.create_or_update_repo_pr_settings(GENERAL_FORM_DATA)
        create_mock.assert_called_once_with(
            model.repo_settings, GENERAL_FORM_DATA)

    def test_raises_exception_when_repository_is_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.create_or_update_repo_pr_settings(GENERAL_FORM_DATA)
        assert exc_info.value.message == 'Repository is not specified'


class TestCreateOrUpdatGlobalGeneralSettings(object):
    def test_calls_create_or_update_general_settings(self):
        model = VcsSettingsModel()
        create_patch = mock.patch.object(
            model, '_create_or_update_general_settings')
        with create_patch as create_mock:
            model.create_or_update_global_pr_settings(GENERAL_FORM_DATA)
        create_mock.assert_called_once_with(
            model.global_settings, GENERAL_FORM_DATA)


class TestCreateOrUpdateGeneralSettings(object):
    def test_create_when_no_repo_settings_found(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model._create_or_update_general_settings(
            model.repo_settings, GENERAL_FORM_DATA)

        cleanup = []
        try:
            for name in model.GENERAL_SETTINGS:
                setting = model.repo_settings.get_setting_by_name(name)
                assert setting.app_settings_value is True
                cleanup.append(setting)
        finally:
            for setting in cleanup:
                Session().delete(setting)
            Session().commit()

    def test_create_raises_exception_when_data_incomplete(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)

        deleted_key = 'rhodecode_pr_merge_enabled'
        data = GENERAL_FORM_DATA.copy()
        data.pop(deleted_key)

        with pytest.raises(ValueError) as exc_info:
            model._create_or_update_general_settings(model.repo_settings, data)
        assert (
            exc_info.value.message ==
            'The given data does not contain {} key'.format(deleted_key))

    def test_update_when_repo_setting_found(self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        for name in model.GENERAL_SETTINGS:
            settings_util.create_repo_rhodecode_setting(
                repo_stub, name, False, 'bool')

        model._create_or_update_general_settings(
            model.repo_settings, GENERAL_FORM_DATA)

        for name in model.GENERAL_SETTINGS:
            setting = model.repo_settings.get_setting_by_name(name)
            assert setting.app_settings_value is True


class TestCreateRepoSvnSettings(object):
    def test_calls_create_svn_settings(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        with mock.patch.object(model, '_create_svn_settings') as create_mock:
            model.create_repo_svn_settings(SVN_FORM_DATA)
        create_mock.assert_called_once_with(model.repo_settings, SVN_FORM_DATA)

    def test_raises_exception_when_repository_is_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.create_repo_svn_settings(SVN_FORM_DATA)
        assert exc_info.value.message == 'Repository is not specified'


class TestCreateGlobalSvnSettings(object):
    def test_calls_create_svn_settings(self):
        model = VcsSettingsModel()
        with mock.patch.object(model, '_create_svn_settings') as create_mock:
            model.create_global_svn_settings(SVN_FORM_DATA)
        create_mock.assert_called_once_with(
            model.global_settings, SVN_FORM_DATA)


class TestCreateSvnSettings(object):
    def test_create(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model._create_svn_settings(model.repo_settings, SVN_FORM_DATA)
        Session().commit()

        branch_ui = model.repo_settings.get_ui_by_section(
            model.SVN_BRANCH_SECTION)
        tag_ui = model.repo_settings.get_ui_by_section(
            model.SVN_TAG_SECTION)

        try:
            assert len(branch_ui) == 1
            assert len(tag_ui) == 1
        finally:
            Session().delete(branch_ui[0])
            Session().delete(tag_ui[0])
            Session().commit()

    def test_create_tag(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        data = SVN_FORM_DATA.copy()
        data.pop('new_svn_branch')
        model._create_svn_settings(model.repo_settings, data)
        Session().commit()

        branch_ui = model.repo_settings.get_ui_by_section(
            model.SVN_BRANCH_SECTION)
        tag_ui = model.repo_settings.get_ui_by_section(
            model.SVN_TAG_SECTION)

        try:
            assert len(branch_ui) == 0
            assert len(tag_ui) == 1
        finally:
            Session().delete(tag_ui[0])
            Session().commit()

    def test_create_nothing_when_no_svn_settings_specified(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model._create_svn_settings(model.repo_settings, {})
        Session().commit()

        branch_ui = model.repo_settings.get_ui_by_section(
            model.SVN_BRANCH_SECTION)
        tag_ui = model.repo_settings.get_ui_by_section(
            model.SVN_TAG_SECTION)

        assert len(branch_ui) == 0
        assert len(tag_ui) == 0

    def test_create_nothing_when_empty_settings_specified(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        data = {
            'new_svn_branch': '',
            'new_svn_tag': ''
        }
        model._create_svn_settings(model.repo_settings, data)
        Session().commit()

        branch_ui = model.repo_settings.get_ui_by_section(
            model.SVN_BRANCH_SECTION)
        tag_ui = model.repo_settings.get_ui_by_section(
            model.SVN_TAG_SECTION)

        assert len(branch_ui) == 0
        assert len(tag_ui) == 0


class TestCreateOrUpdateUi(object):
    def test_create(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model._create_or_update_ui(
            model.repo_settings, 'test-section', 'test-key', active=False,
            value='False')
        Session().commit()

        created_ui = model.repo_settings.get_ui_by_section_and_key(
            'test-section', 'test-key')

        try:
            assert created_ui.ui_active is False
            assert str2bool(created_ui.ui_value) is False
        finally:
            Session().delete(created_ui)
            Session().commit()

    def test_update(self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)

        largefiles, phases = model.HG_SETTINGS
        section = 'test-section'
        key = 'test-key'
        settings_util.create_repo_rhodecode_ui(
            repo_stub, section, 'True', key=key, active=True)

        model._create_or_update_ui(
            model.repo_settings, section, key, active=False, value='False')
        Session().commit()

        created_ui = model.repo_settings.get_ui_by_section_and_key(
            section, key)
        assert created_ui.ui_active is False
        assert str2bool(created_ui.ui_value) is False


class TestCreateOrUpdateRepoHgSettings(object):
    FORM_DATA = {
        'extensions_largefiles': False,
        'phases_publish': False
    }

    def test_creates_repo_hg_settings_when_data_is_correct(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        with mock.patch.object(model, '_create_or_update_ui') as create_mock:
            model.create_or_update_repo_hg_settings(self.FORM_DATA)
        expected_calls = [
            mock.call(model.repo_settings, 'extensions', 'largefiles',
                      active=False, value=''),
            mock.call(model.repo_settings, 'phases', 'publish', value='False'),
        ]
        assert expected_calls == create_mock.call_args_list

    @pytest.mark.parametrize('field_to_remove', FORM_DATA.keys())
    def test_key_is_not_found(self, repo_stub, field_to_remove):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        data = self.FORM_DATA.copy()
        data.pop(field_to_remove)
        with pytest.raises(ValueError) as exc_info:
            model.create_or_update_repo_hg_settings(data)
        expected_message = 'The given data does not contain {} key'.format(
            field_to_remove)
        assert exc_info.value.message == expected_message

    def test_create_raises_exception_when_repository_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.create_or_update_repo_hg_settings(self.FORM_DATA)
        assert exc_info.value.message == 'Repository is not specified'


class TestUpdateGlobalSslSetting(object):
    def test_updates_global_hg_settings(self):
        model = VcsSettingsModel()
        with mock.patch.object(model, '_create_or_update_ui') as create_mock:
            model.update_global_ssl_setting('False')
        create_mock.assert_called_once_with(
            model.global_settings, 'web', 'push_ssl', value='False')


class TestUpdateGlobalPathSetting(object):
    def test_updates_global_path_settings(self):
        model = VcsSettingsModel()
        with mock.patch.object(model, '_create_or_update_ui') as create_mock:
            model.update_global_path_setting('False')
        create_mock.assert_called_once_with(
            model.global_settings, 'paths', '/', value='False')


class TestCreateOrUpdateGlobalHgSettings(object):
    FORM_DATA = {
        'extensions_largefiles': False,
        'phases_publish': False,
        'extensions_hgsubversion': False
    }

    def test_creates_repo_hg_settings_when_data_is_correct(self):
        model = VcsSettingsModel()
        with mock.patch.object(model, '_create_or_update_ui') as create_mock:
            model.create_or_update_global_hg_settings(self.FORM_DATA)
        expected_calls = [
            mock.call(model.global_settings, 'extensions', 'largefiles',
                      active=False, value=''),
            mock.call(model.global_settings, 'phases', 'publish',
                      value='False'),
            mock.call(model.global_settings, 'extensions', 'hgsubversion',
                      active=False)
        ]
        assert expected_calls == create_mock.call_args_list

    @pytest.mark.parametrize('field_to_remove', FORM_DATA.keys())
    def test_key_is_not_found(self, repo_stub, field_to_remove):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        data = self.FORM_DATA.copy()
        data.pop(field_to_remove)
        with pytest.raises(Exception) as exc_info:
            model.create_or_update_global_hg_settings(data)
        expected_message = 'The given data does not contain {} key'.format(
            field_to_remove)
        assert exc_info.value.message == expected_message


class TestDeleteRepoSvnPattern(object):
    def test_success_when_repo_is_set(self, backend_svn):
        repo_name = backend_svn.repo_name
        model = VcsSettingsModel(repo=repo_name)
        delete_ui_patch = mock.patch.object(model.repo_settings, 'delete_ui')
        with delete_ui_patch as delete_ui_mock:
            model.delete_repo_svn_pattern(123)
        delete_ui_mock.assert_called_once_with(123)

    def test_raises_exception_when_repository_is_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.delete_repo_svn_pattern(123)
        assert exc_info.value.message == 'Repository is not specified'


class TestDeleteGlobalSvnPattern(object):
    def test_delete_global_svn_pattern_calls_delete_ui(self):
        model = VcsSettingsModel()
        delete_ui_patch = mock.patch.object(model.global_settings, 'delete_ui')
        with delete_ui_patch as delete_ui_mock:
            model.delete_global_svn_pattern(123)
        delete_ui_mock.assert_called_once_with(123)


class TestFilterUiSettings(object):
    def test_settings_are_filtered(self):
        model = VcsSettingsModel()
        repo_settings = [
            UiSetting('extensions', 'largefiles', '', True),
            UiSetting('phases', 'publish', 'True', True),
            UiSetting('hooks', 'changegroup.repo_size', 'hook', True),
            UiSetting('hooks', 'changegroup.push_logger', 'hook', True),
            UiSetting('hooks', 'outgoing.pull_logger', 'hook', True),
            UiSetting(
                'vcs_svn_branch', '84223c972204fa545ca1b22dac7bef5b68d7442d',
                'test_branch', True),
            UiSetting(
                'vcs_svn_tag', '84229c972204fa545ca1b22dac7bef5b68d7442d',
                'test_tag', True),
        ]
        non_repo_settings = [
            UiSetting('test', 'outgoing.pull_logger', 'hook', True),
            UiSetting('hooks', 'test2', 'hook', True),
            UiSetting(
                'vcs_svn_repo', '84229c972204fa545ca1b22dac7bef5b68d7442d',
                'test_tag', True),
        ]
        settings = repo_settings + non_repo_settings
        filtered_settings = model._filter_ui_settings(settings)
        assert sorted(filtered_settings) == sorted(repo_settings)


class TestFilterGeneralSettings(object):
    def test_settings_are_filtered(self):
        model = VcsSettingsModel()
        settings = {
            'rhodecode_abcde': 'value1',
            'rhodecode_vwxyz': 'value2',
        }
        general_settings = {
            'rhodecode_{}'.format(key): 'value'
            for key in VcsSettingsModel.GENERAL_SETTINGS
        }
        settings.update(general_settings)

        filtered_settings = model._filter_general_settings(general_settings)
        assert sorted(filtered_settings) == sorted(general_settings)


class TestGetRepoUiSettings(object):
    def test_global_uis_are_returned_when_no_repo_uis_found(
            self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        result = model.get_repo_ui_settings()
        svn_sections = (
            VcsSettingsModel.SVN_TAG_SECTION,
            VcsSettingsModel.SVN_BRANCH_SECTION)
        expected_result = [
            s for s in model.global_settings.get_ui()
            if s.section not in svn_sections]
        assert sorted(result) == sorted(expected_result)

    def test_repo_uis_are_overriding_global_uis(
            self, repo_stub, settings_util):
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'repo', key=key, active=False)
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        result = model.get_repo_ui_settings()
        for setting in result:
            locator = (setting.section, setting.key)
            if locator in VcsSettingsModel.HOOKS_SETTINGS:
                assert setting.value == 'repo'

                assert setting.active is False

    def test_global_svn_patterns_are_not_in_list(
            self, repo_stub, settings_util):
        svn_sections = (
            VcsSettingsModel.SVN_TAG_SECTION,
            VcsSettingsModel.SVN_BRANCH_SECTION)
        for section in svn_sections:
            settings_util.create_rhodecode_ui(
                section, 'repo', key='deadbeef' + section, active=False)
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        result = model.get_repo_ui_settings()
        for setting in result:
            assert setting.section not in svn_sections

    def test_repo_uis_filtered_by_section_are_returned(
            self, repo_stub, settings_util):
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'repo', key=key, active=False)
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        section, key = VcsSettingsModel.HOOKS_SETTINGS[0]
        result = model.get_repo_ui_settings(section=section)
        for setting in result:
            assert setting.section == section

    def test_repo_uis_filtered_by_key_are_returned(
            self, repo_stub, settings_util):
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'repo', key=key, active=False)
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        section, key = VcsSettingsModel.HOOKS_SETTINGS[0]
        result = model.get_repo_ui_settings(key=key)
        for setting in result:
            assert setting.key == key

    def test_raises_exception_when_repository_is_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.get_repo_ui_settings()
        assert exc_info.value.message == 'Repository is not specified'


class TestGetRepoGeneralSettings(object):
    def test_global_settings_are_returned_when_no_repo_settings_found(
            self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        result = model.get_repo_general_settings()
        expected_result = model.global_settings.get_all_settings()
        assert sorted(result) == sorted(expected_result)

    def test_repo_uis_are_overriding_global_uis(
            self, repo_stub, settings_util):
        for key in VcsSettingsModel.GENERAL_SETTINGS:
            settings_util.create_repo_rhodecode_setting(
                repo_stub, key, 'abcde', type_='unicode')
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        result = model.get_repo_ui_settings()
        for key in result:
            if key in VcsSettingsModel.GENERAL_SETTINGS:
                assert result[key] == 'abcde'

    def test_raises_exception_when_repository_is_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.get_repo_general_settings()
        assert exc_info.value.message == 'Repository is not specified'


class TestGetGlobalGeneralSettings(object):
    def test_global_settings_are_returned(self, repo_stub):
        model = VcsSettingsModel()
        result = model.get_global_general_settings()
        expected_result = model.global_settings.get_all_settings()
        assert sorted(result) == sorted(expected_result)

    def test_repo_uis_are_not_overriding_global_uis(
            self, repo_stub, settings_util):
        for key in VcsSettingsModel.GENERAL_SETTINGS:
            settings_util.create_repo_rhodecode_setting(
                repo_stub, key, 'abcde', type_='unicode')
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        result = model.get_global_general_settings()
        expected_result = model.global_settings.get_all_settings()
        assert sorted(result) == sorted(expected_result)


class TestGetGlobalUiSettings(object):
    def test_global_uis_are_returned(self, repo_stub):
        model = VcsSettingsModel()
        result = model.get_global_ui_settings()
        expected_result = model.global_settings.get_ui()
        assert sorted(result) == sorted(expected_result)

    def test_repo_uis_are_not_overriding_global_uis(
            self, repo_stub, settings_util):
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'repo', key=key, active=False)
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        result = model.get_global_ui_settings()
        expected_result = model.global_settings.get_ui()
        assert sorted(result) == sorted(expected_result)

    def test_ui_settings_filtered_by_section(
            self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        section, key = VcsSettingsModel.HOOKS_SETTINGS[0]
        result = model.get_global_ui_settings(section=section)
        expected_result = model.global_settings.get_ui(section=section)
        assert sorted(result) == sorted(expected_result)

    def test_ui_settings_filtered_by_key(
            self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        section, key = VcsSettingsModel.HOOKS_SETTINGS[0]
        result = model.get_global_ui_settings(key=key)
        expected_result = model.global_settings.get_ui(key=key)
        assert sorted(result) == sorted(expected_result)


class TestGetGeneralSettings(object):
    def test_global_settings_are_returned_when_inherited_is_true(
            self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model.inherit_global_settings = True
        for key in VcsSettingsModel.GENERAL_SETTINGS:
            settings_util.create_repo_rhodecode_setting(
                repo_stub, key, 'abcde', type_='unicode')
        result = model.get_general_settings()
        expected_result = model.get_global_general_settings()
        assert sorted(result) == sorted(expected_result)

    def test_repo_settings_are_returned_when_inherited_is_false(
            self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model.inherit_global_settings = False
        for key in VcsSettingsModel.GENERAL_SETTINGS:
            settings_util.create_repo_rhodecode_setting(
                repo_stub, key, 'abcde', type_='unicode')
        result = model.get_general_settings()
        expected_result = model.get_repo_general_settings()
        assert sorted(result) == sorted(expected_result)

    def test_global_settings_are_returned_when_no_repository_specified(self):
        model = VcsSettingsModel()
        result = model.get_general_settings()
        expected_result = model.get_global_general_settings()
        assert sorted(result) == sorted(expected_result)


class TestGetUiSettings(object):
    def test_global_settings_are_returned_when_inherited_is_true(
            self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model.inherit_global_settings = True
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'repo', key=key, active=True)
        result = model.get_ui_settings()
        expected_result = model.get_global_ui_settings()
        assert sorted(result) == sorted(expected_result)

    def test_repo_settings_are_returned_when_inherited_is_false(
            self, repo_stub, settings_util):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model.inherit_global_settings = False
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'repo', key=key, active=True)
        result = model.get_ui_settings()
        expected_result = model.get_repo_ui_settings()
        assert sorted(result) == sorted(expected_result)

    def test_repo_settings_filtered_by_section_and_key(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        model.inherit_global_settings = False
        args = ('section', 'key')
        with mock.patch.object(model, 'get_repo_ui_settings') as settings_mock:
            model.get_ui_settings(*args)
        settings_mock.assert_called_once_with(*args)

    def test_global_settings_filtered_by_section_and_key(self):
        model = VcsSettingsModel()
        args = ('section', 'key')
        with mock.patch.object(model, 'get_global_ui_settings') as (
                settings_mock):
            model.get_ui_settings(*args)
        settings_mock.assert_called_once_with(*args)

    def test_global_settings_are_returned_when_no_repository_specified(self):
        model = VcsSettingsModel()
        result = model.get_ui_settings()
        expected_result = model.get_global_ui_settings()
        assert sorted(result) == sorted(expected_result)


class TestGetSvnPatterns(object):
    def test_repo_settings_filtered_by_section_and_key(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub.repo_name)
        args = ('section', )
        with mock.patch.object(model, 'get_repo_ui_settings') as settings_mock:
            model.get_svn_patterns(*args)
        settings_mock.assert_called_once_with(*args)

    def test_global_settings_filtered_by_section_and_key(self):
        model = VcsSettingsModel()
        args = ('section', )
        with mock.patch.object(model, 'get_global_ui_settings') as (
                settings_mock):
            model.get_svn_patterns(*args)
        settings_mock.assert_called_once_with(*args)


class TestGetReposLocation(object):
    def test_returns_repos_location(self, repo_stub):
        model = VcsSettingsModel()

        result_mock = mock.Mock()
        result_mock.ui_value = '/tmp'

        with mock.patch.object(model, 'global_settings') as settings_mock:
            settings_mock.get_ui_by_key.return_value = result_mock
            result = model.get_repos_location()

        settings_mock.get_ui_by_key.assert_called_once_with('/')
        assert result == '/tmp'


class TestCreateOrUpdateRepoSettings(object):
    FORM_DATA = {
        'inherit_global_settings': False,
        'hooks_changegroup_repo_size': False,
        'hooks_changegroup_push_logger': False,
        'hooks_outgoing_pull_logger': False,
        'extensions_largefiles': False,
        'phases_publish': 'false',
        'rhodecode_pr_merge_enabled': False,
        'rhodecode_use_outdated_comments': False,
        'new_svn_branch': '',
        'new_svn_tag': ''
    }

    def test_get_raises_exception_when_repository_not_specified(self):
        model = VcsSettingsModel()
        with pytest.raises(Exception) as exc_info:
            model.create_or_update_repo_settings(data=self.FORM_DATA)
        assert exc_info.value.message == 'Repository is not specified'

    def test_only_svn_settings_are_updated_when_type_is_svn(self, backend_svn):
        repo = backend_svn.create_repo()
        model = VcsSettingsModel(repo=repo)
        with self._patch_model(model) as mocks:
            model.create_or_update_repo_settings(
                data=self.FORM_DATA, inherit_global_settings=False)
        mocks['create_repo_svn_settings'].assert_called_once_with(
            self.FORM_DATA)
        non_called_methods = (
            'create_or_update_repo_hook_settings',
            'create_or_update_repo_pr_settings',
            'create_or_update_repo_hg_settings')
        for method in non_called_methods:
            assert mocks[method].call_count == 0

    def test_non_svn_settings_are_updated_when_type_is_hg(self, backend_hg):
        repo = backend_hg.create_repo()
        model = VcsSettingsModel(repo=repo)
        with self._patch_model(model) as mocks:
            model.create_or_update_repo_settings(
                data=self.FORM_DATA, inherit_global_settings=False)

        assert mocks['create_repo_svn_settings'].call_count == 0
        called_methods = (
            'create_or_update_repo_hook_settings',
            'create_or_update_repo_pr_settings',
            'create_or_update_repo_hg_settings')
        for method in called_methods:
            mocks[method].assert_called_once_with(self.FORM_DATA)

    def test_non_svn_and_hg_settings_are_updated_when_type_is_git(
            self, backend_git):
        repo = backend_git.create_repo()
        model = VcsSettingsModel(repo=repo)
        with self._patch_model(model) as mocks:
            model.create_or_update_repo_settings(
                data=self.FORM_DATA, inherit_global_settings=False)

        assert mocks['create_repo_svn_settings'].call_count == 0
        called_methods = (
            'create_or_update_repo_hook_settings',
            'create_or_update_repo_pr_settings')
        non_called_methods = (
            'create_repo_svn_settings',
            'create_or_update_repo_hg_settings'
        )
        for method in called_methods:
            mocks[method].assert_called_once_with(self.FORM_DATA)
        for method in non_called_methods:
            assert mocks[method].call_count == 0

    def test_no_methods_are_called_when_settings_are_inherited(
            self, backend):
        repo = backend.create_repo()
        model = VcsSettingsModel(repo=repo)
        with self._patch_model(model) as mocks:
            model.create_or_update_repo_settings(
                data=self.FORM_DATA, inherit_global_settings=True)
        for method_name in mocks:
            assert mocks[method_name].call_count == 0

    def test_cache_is_marked_for_invalidation(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub)
        invalidation_patcher = mock.patch(
            'rhodecode.controllers.admin.repos.ScmModel.mark_for_invalidation')
        with invalidation_patcher as invalidation_mock:
            model.create_or_update_repo_settings(
                data=self.FORM_DATA, inherit_global_settings=True)
        invalidation_mock.assert_called_once_with(
            repo_stub.repo_name, delete=True)

    def test_inherit_flag_is_saved(self, repo_stub):
        model = VcsSettingsModel(repo=repo_stub)
        model.inherit_global_settings = True
        with self._patch_model(model):
            model.create_or_update_repo_settings(
                data=self.FORM_DATA, inherit_global_settings=False)
        assert model.inherit_global_settings is False

    def _patch_model(self, model):
        return mock.patch.multiple(
            model,
            create_repo_svn_settings=mock.DEFAULT,
            create_or_update_repo_hook_settings=mock.DEFAULT,
            create_or_update_repo_pr_settings=mock.DEFAULT,
            create_or_update_repo_hg_settings=mock.DEFAULT)
