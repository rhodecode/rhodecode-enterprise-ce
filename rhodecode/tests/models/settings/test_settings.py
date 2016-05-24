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

from rhodecode.lib.utils2 import safe_str
from rhodecode.model.db import (
    RhodeCodeUi, RepoRhodeCodeUi, RhodeCodeSetting, RepoRhodeCodeSetting)
from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel, SettingNotFound, UiSetting


class TestRepoGetUiByKey(object):
    def test_ui_settings_are_returned_when_key_is_found(
            self, repo_stub, settings_util):
        section = 'test section'
        value = 'test value'

        settings_util.create_repo_rhodecode_ui(
            repo_stub, 'wrong section', 'wrong value')
        setting = settings_util.create_repo_rhodecode_ui(
            repo_stub, section, value)
        key = setting.ui_key

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui_by_key(key)
        assert result.ui_value == value
        assert result.ui_section == section
        assert result.ui_active is True

    def test_none_is_returned_when_key_is_not_found(
            self, repo_stub, settings_util):
        settings_util.create_repo_rhodecode_ui(
            repo_stub, 'wrong section', 'wrong value')

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui_by_key('abcde')
        assert result is None


class TestGlobalGetUiByKey(object):
    def test_ui_settings_are_returned_when_key_is_found(self, settings_util):
        section = 'test section'
        value = 'test value'

        settings_util.create_rhodecode_ui('wrong section', 'wrong value')
        setting = settings_util.create_rhodecode_ui(section, value)
        key = setting.ui_key

        model = SettingsModel()
        result = model.get_ui_by_key(key)
        assert result.ui_value == value
        assert result.ui_section == section
        assert result.ui_active is True

    def test_none_is_returned_when_key_is_not_found(self, settings_util):
        settings_util.create_rhodecode_ui('wrong section', 'wrong value')
        model = SettingsModel()
        result = model.get_ui_by_key('abcde')
        assert result is None


class TestRepoGetUiBySection(object):
    def test_ui_settings_are_returned_when_section_is_found(
            self, repo_stub, settings_util):
        section = 'test section'
        values = ['test value 1', 'test value 2']

        expected_pairs = []
        for value in values:
            setting = settings_util.create_repo_rhodecode_ui(
                repo_stub, section, value)
            expected_pairs.append((setting.ui_key, value))

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui_by_section(section)
        result_pairs = [(r.ui_key, r.ui_value) for r in result]
        assert sorted(result_pairs) == sorted(expected_pairs)

    def test_empty_list_is_returned_when_section_is_not_found(
            self, repo_stub, settings_util):
        settings_util.create_repo_rhodecode_ui(
            repo_stub, 'wrong section', 'wrong value')

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui_by_section('correct section')
        assert result == []


class TestGlobalGetUiBySection(object):
    def test_ui_settings_are_returned_when_section_is_found(
            self, settings_util):
        section = 'test section'
        values = ['test value 1', 'test value 2']

        expected_pairs = []
        for value in values:
            setting = settings_util.create_rhodecode_ui(section, value)
            expected_pairs.append((setting.ui_key, value))

        model = SettingsModel()
        result = model.get_ui_by_section(section)
        result_pairs = [(r.ui_key, r.ui_value) for r in result]
        assert sorted(result_pairs) == sorted(expected_pairs)

    def test_empty_list_is_returned_when_section_is_not_found(
            self, settings_util):
        settings_util.create_rhodecode_ui('wrong section', 'wrong value')

        model = SettingsModel()
        result = model.get_ui_by_section('correct section')
        assert result == []


class TestRepoGetUiBySectionAndKey(object):
    def test_ui_settings_are_returned_when_section_and_key_are_found(
            self, repo_stub, settings_util):
        section = 'test section'
        value = 'test value'
        key = 'test key'

        settings_util.create_rhodecode_ui(
            'wrong section', 'wrong value', key='wrong key')
        setting = settings_util.create_repo_rhodecode_ui(
            repo_stub, section, value, key=key)
        key = setting.ui_key

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui_by_section_and_key(section, key)
        assert result.ui_value == value
        assert result.ui_section == section
        assert result.ui_active is True

    def test_none_is_returned_when_key_section_pair_is_not_found(
            self, repo_stub, settings_util):
        settings_util.create_repo_rhodecode_ui(
            repo_stub, 'section', 'wrong value', key='wrong key')

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui_by_section_and_key('section', 'test key')
        assert result is None


class TestGlobalGetUiBySectionAndKey(object):
    def test_ui_settings_are_returned_when_section_and_key_are_found(
            self, settings_util):
        section = 'test section'
        value = 'test value'
        key = 'test key'

        settings_util.create_rhodecode_ui(
            'wrong section', 'wrong value', key='wrong key')
        setting = settings_util.create_rhodecode_ui(section, value, key=key)
        key = setting.ui_key

        model = SettingsModel()
        result = model.get_ui_by_section_and_key(section, key)
        assert result.ui_value == value
        assert result.ui_section == section
        assert result.ui_active is True

    def test_none_is_returned_when_key_section_pair_is_not_found(
            self, settings_util):
        settings_util.create_rhodecode_ui(
            'section', 'wrong value', key='wrong key')
        model = SettingsModel()
        result = model.get_ui_by_section_and_key('section', 'test key')
        assert result is None


class TestRepoGetUi(object):
    def test_non_empty_list_is_returned_when_ui_settings_found(
            self, repo_stub, settings_util, fake_ui_values):
        for ui in fake_ui_values:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, ui.section, ui.value, key=ui.key)
            # Create few global settings to check that only repo ones are
            # displayed
            settings_util.create_rhodecode_ui(ui.section, ui.value, key=ui.key)

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui()
        assert sorted(result) == sorted(fake_ui_values)

    def test_settings_filtered_by_section(
            self, repo_stub, settings_util, fake_ui_values):
        for ui in fake_ui_values:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, ui.section, ui.value, key=ui.key)

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui(section=fake_ui_values[0].section)
        expected_result = [
            s for s in fake_ui_values
            if s.section == fake_ui_values[0].section]
        assert sorted(result) == sorted(expected_result)

    def test_settings_filtered_by_key(
            self, repo_stub, settings_util, fake_ui_values):
        for ui in fake_ui_values:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, ui.section, ui.value, key=ui.key)

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui(key=fake_ui_values[0].key)
        expected_result = [
            s for s in fake_ui_values if s.key == fake_ui_values[0].key]
        assert sorted(result) == sorted(expected_result)

    def test_empty_list_is_returned_when_ui_settings_are_not_found(
            self, repo_stub, settings_util):
        for i in range(10):
            settings_util.create_rhodecode_ui(
                'section{}'.format(i), 'value{}'.format(i),
                key='key{}'.format(i), active=True)

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_ui()
        assert result == []


class TestGlobalGetUi(object):
    def test_non_empty_list_is_returned_when_ui_settings_found(
            self, backend_stub, settings_util, fake_ui_values):
        repo = backend_stub.create_repo()
        for ui in fake_ui_values:
            settings_util.create_rhodecode_ui(ui.section, ui.value, key=ui.key)
            # Create few repo settings to check that only global ones are
            # displayed
            settings_util.create_repo_rhodecode_ui(
                repo, ui.section, ui.value, key=ui.key)

        model = SettingsModel()
        result = model.get_ui()
        for ui in fake_ui_values:
            assert ui in result

    def test_settings_filtered_by_key(self, settings_util, fake_ui_values):
        for ui in fake_ui_values:
            settings_util.create_rhodecode_ui(ui.section, ui.value, key=ui.key)
        expected_result = [
            s for s in fake_ui_values if s.key == fake_ui_values[0].key]

        model = SettingsModel()
        result = model.get_ui(key=fake_ui_values[0].key)
        assert sorted(result) == sorted(expected_result)

    def test_settings_filtered_by_section(self, settings_util, fake_ui_values):
        for ui in fake_ui_values:
            settings_util.create_rhodecode_ui(ui.section, ui.value, key=ui.key)
        expected_result = [
            s for s in fake_ui_values
            if s.section == fake_ui_values[0].section]

        model = SettingsModel()
        result = model.get_ui(section=fake_ui_values[0].section)
        assert sorted(result) == sorted(expected_result)

    def test_repo_settings_are_not_displayed(
            self, backend_stub, settings_util, fake_ui_values):
        repo = backend_stub.create_repo()
        for ui in fake_ui_values:
            settings_util.create_repo_rhodecode_ui(
                repo, ui.section, ui.value, key=ui.key, active=ui.active)

        model = SettingsModel()
        result = model.get_ui()
        for ui in fake_ui_values:
            assert ui not in result


class TestRepoGetBuiltInHooks(object):
    def test_only_builtin_hooks_are_returned(self, repo_stub, settings_util):
        section = 'hooks'
        valid_keys = SettingsModel.BUILTIN_HOOKS
        invalid_keys = ('fake_hook', )
        keys = valid_keys + invalid_keys

        for key in keys:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'test value', key=key)

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_builtin_hooks()

        assert len(result) == len(valid_keys)
        for entry in result:
            assert entry.ui_key in valid_keys


class TestGlobalGetBuiltInHooks(object):
    def test_only_builtin_hooks_are_returned(self, settings_util):
        section = 'hooks'
        valid_keys = ('valid_key1', 'valid_key2')
        invalid_keys = ('fake_hook', )
        keys = valid_keys + invalid_keys

        for key in keys:
            settings_util.create_rhodecode_ui(section, 'test value', key=key)

        model = SettingsModel()
        with mock.patch.object(model, 'BUILTIN_HOOKS', valid_keys):
            result = model.get_builtin_hooks()

        assert len(result) == len(valid_keys)
        for entry in result:
            assert entry.ui_key in valid_keys


class TestRepoGetCustomHooks(object):
    def test_only_custom_hooks_are_returned(self, repo_stub, settings_util):
        section = 'hooks'
        valid_keys = ('custom', )
        invalid_keys = SettingsModel.BUILTIN_HOOKS
        keys = valid_keys + invalid_keys

        for key in keys:
            settings_util.create_repo_rhodecode_ui(
                repo_stub, section, 'test value', key=key)

        model = SettingsModel(repo=repo_stub.repo_name)
        result = model.get_custom_hooks()

        assert len(result) == len(valid_keys)
        for entry in result:
            assert entry.ui_key in valid_keys


class TestGlobalGetCustomHooks(object):
    def test_only_custom_hooks_are_returned(self, settings_util):
        section = 'hooks'
        valid_keys = ('valid_key1', 'valid_key2')
        invalid_keys = ('fake_hook', )
        keys = valid_keys + invalid_keys

        for key in keys:
            settings_util.create_rhodecode_ui(section, 'test value', key=key)

        model = SettingsModel()
        with mock.patch.object(model, 'BUILTIN_HOOKS', invalid_keys):
            result = model.get_custom_hooks()
        for entry in result:
            assert entry.ui_key not in invalid_keys


class TestRepoCreateUiSectionValue(object):
    @pytest.mark.parametrize("additional_kwargs", [
        {'key': 'abcde'},
        {'active': False},
        {}
    ])
    def test_ui_section_value_is_created(
            self, repo_stub, additional_kwargs):
        model = SettingsModel(repo=repo_stub.repo_name)
        section = 'test section'
        value = 'test value'
        result = model.create_ui_section_value(section, value)
        key = result.ui_key
        Session().commit()

        setting = model.get_ui_by_key(key)
        try:
            assert setting == result
            assert isinstance(setting, RepoRhodeCodeUi)
        finally:
            Session().delete(result)
            Session().commit()


class TestGlobalCreateUiSectionValue(object):
    @pytest.mark.parametrize("additional_kwargs", [
        {'key': 'abcde'},
        {'active': False},
        {}
    ])
    def test_ui_section_value_is_created_with_autogenerated_key(
            self, backend_stub, additional_kwargs):
        model = SettingsModel()
        section = 'test section'
        value = 'test value'
        result = model.create_ui_section_value(
            section, value, **additional_kwargs)
        key = result.ui_key
        Session().commit()

        setting = model.get_ui_by_key(key)
        try:
            assert setting == result
            assert isinstance(setting, RhodeCodeUi)
        finally:
            Session().delete(result)
            Session().commit()


class TestRepoCreateOrUpdateHook(object):
    def test_hook_created(self, repo_stub):
        model = SettingsModel(repo=repo_stub.repo_name)
        key = 'test_key'
        value = 'test value'
        result = model.create_or_update_hook(key, value)
        Session().commit()

        setting = model.get_ui_by_section_and_key('hooks', key)
        try:
            assert setting == result
            assert isinstance(setting, RepoRhodeCodeUi)
        finally:
            Session().delete(result)
            Session().commit()

    def test_hook_updated(self, repo_stub, settings_util):
        section = 'hooks'
        key = 'test_key'

        settings_util.create_repo_rhodecode_ui(
            repo_stub, section, 'old value', key=key)

        model = SettingsModel(repo=repo_stub.repo_name)
        value = 'test value'
        model.create_or_update_hook(key, value)
        Session().commit()

        setting = model.get_ui_by_section_and_key('hooks', key)
        assert setting.ui_value == value


class TestGlobalCreateOrUpdateHook(object):
    def test_hook_created(self):
        model = SettingsModel()
        key = 'test_key'
        value = 'test value'
        result = model.create_or_update_hook(key, value)
        Session().commit()

        setting = model.get_ui_by_section_and_key('hooks', key)
        try:
            assert setting == result
            assert isinstance(setting, RhodeCodeUi)
        finally:
            Session().delete(result)
            Session().commit()

    def test_hook_updated(self, settings_util):
        section = 'hooks'
        key = 'test_key'

        settings_util.create_rhodecode_ui(section, 'old value', key=key)

        model = SettingsModel()
        value = 'test value'
        model.create_or_update_hook(key, value)
        Session().commit()

        setting = model.get_ui_by_section_and_key('hooks', key)
        assert setting.ui_value == value


class TestDeleteUiValue(object):
    def test_delete_ui_when_repo_is_set(self, repo_stub, settings_util):
        model = SettingsModel(repo=repo_stub.repo_name)
        result = settings_util.create_repo_rhodecode_ui(
            repo_stub, 'section', None, cleanup=False)

        key = result.ui_key
        model.delete_ui(result.ui_id)
        Session().commit()

        setting = model.get_ui_by_key(key)
        assert setting is None

    @pytest.mark.parametrize('id_', (None, 123))
    def test_raises_exception_when_id_is_not_specified(self, id_):
        model = SettingsModel()
        with pytest.raises(SettingNotFound) as exc_info:
            model.delete_ui(id_)
        assert exc_info.value.message == 'Setting is not found'

    def test_delete_ui_when_repo_is_not_set(self, settings_util):
        model = SettingsModel()
        result = settings_util.create_rhodecode_ui(
            'section', None, cleanup=False)

        key = result.ui_key
        model.delete_ui(result.ui_id)
        Session().commit()

        setting = model.get_ui_by_key(key)
        assert setting is None


class TestRepoGetSettingByName(object):
    @pytest.mark.parametrize("name, value, type_, expected_value", [
        ('test_unicode', 'Straße', 'unicode', 'Straße'),
        ('test_int', '1234', 'int', 1234),
        ('test_bool', 'True', 'bool', True),
        ('test_list', 'a,b,c', 'list', ['a', 'b', 'c'])
    ])
    def test_setting_is_returned_when_name_is_found(
            self, repo_stub, settings_util, name, value, type_,
            expected_value):
        settings_util.create_repo_rhodecode_setting(
            repo_stub, name, value, type_)

        model = SettingsModel(repo=repo_stub.repo_name)
        setting = model.get_setting_by_name(name)
        assert setting.app_settings_type == type_
        actual_value = setting.app_settings_value
        if type_ == 'unicode':
            actual_value = safe_str(actual_value)
        assert actual_value == expected_value

    def test_returns_none_if_the_setting_does_not_exist(self, repo_stub):
        model = SettingsModel(repo=repo_stub.repo_name)
        setting = model.get_setting_by_name('abcde')
        assert setting is None


class TestGlobalGetSettingByName(object):
    @pytest.mark.parametrize("name, value, type_, expected_value", [
        ('test_unicode', 'Straße', 'unicode', 'Straße'),
        ('test_int', '1234', 'int', 1234),
        ('test_bool', 'True', 'bool', True),
        ('test_list', 'a,b,c', 'list', ['a', 'b', 'c'])
    ])
    def test_setting_is_returned_when_name_is_found(
            self, settings_util, name, value, type_, expected_value):
        settings_util.create_rhodecode_setting(name, value, type_)

        model = SettingsModel()
        setting = model.get_setting_by_name(name)
        assert setting.app_settings_type == type_
        actual_value = setting.app_settings_value
        if type_ == 'unicode':
            actual_value = safe_str(actual_value)
        assert actual_value == expected_value

    def test_returns_none_if_the_setting_does_not_exist(self):
        model = SettingsModel()
        setting = model.get_setting_by_name('abcde')
        assert setting is None


class TestRepoGetAllSettings(object):
    def test_settings_are_found(self, repo_stub, settings_util):
        initial_settings = {
            'test_setting_{}'.format(i): 'value' for i in range(10)}
        settings = [
            settings_util.create_repo_rhodecode_setting(
                repo_stub, name, initial_settings[name], 'unicode')
            for name in initial_settings
        ]
        model = SettingsModel(repo=repo_stub.repo_name)

        settings = model.get_all_settings()
        expected_settings = {
            'rhodecode_' + name: initial_settings[name]
            for name in initial_settings
        }

        assert len(settings) == 10
        assert expected_settings == settings

    def test_settings_are_not_found(self, repo_stub):
        model = SettingsModel(repo=repo_stub.repo_name)
        setting = model.get_all_settings()
        assert setting == {}


class TestGlobalGetAllSettings(object):
    def test_settings_are_found(self, settings_util):
        initial_settings = {
            'test_setting_{}'.format(i): 'value' for i in range(10)}
        settings = [
            settings_util.create_rhodecode_setting(
                name, initial_settings[name], 'unicode')
            for name in initial_settings
        ]
        model = SettingsModel()

        settings = model.get_all_settings()
        expected_settings = {
            'rhodecode_' + name: initial_settings[name]
            for name in initial_settings
        }

        filtered_settings = {
            name: settings[name]
            for name in settings if name.startswith('rhodecode_test_setting')
        }
        assert len(filtered_settings) == 10
        assert expected_settings == filtered_settings

    def test_settings_are_not_found(self, repo_stub):
        model = SettingsModel(repo=repo_stub.repo_name)
        setting = model.get_all_settings()
        assert setting == {}


class TestRepoCreateOrUpdateSetting(object):
    def test_setting_is_created(self, repo_stub):
        model = SettingsModel(repo=repo_stub.repo_name)
        name = 'test_setting'
        value = 'test_value'
        model.create_or_update_setting(name, val=value)

        setting = model.get_setting_by_name(name)
        try:
            assert setting.app_settings_name == name
            assert setting.app_settings_value == value
            assert setting.app_settings_type == 'unicode'
            assert isinstance(setting, RepoRhodeCodeSetting)
        finally:
            Session().delete(setting)
            Session().commit()

    def test_setting_is_updated(self, repo_stub, settings_util):
        model = SettingsModel(repo=repo_stub.repo_name)
        name = 'test_setting'
        value = 'test_value'
        settings_util.create_repo_rhodecode_setting(
            repo_stub, name, value, 'unicode', cleanup=False)

        updated_value = 'test_value_2'
        model.create_or_update_setting(name, val=updated_value)

        setting = model.get_setting_by_name(name)
        try:
            assert setting.app_settings_name == name
            assert setting.app_settings_value == updated_value
            assert setting.app_settings_type == 'unicode'
            assert isinstance(setting, RepoRhodeCodeSetting)
        finally:
            Session().delete(setting)
            Session().commit()


class TestGlobalCreateOrUpdateSetting(object):
    def test_setting_is_created(self):
        model = SettingsModel()
        name = 'test_setting'
        value = 'test_value'
        model.create_or_update_setting(name, val=value)

        setting = model.get_setting_by_name(name)
        try:
            assert setting.app_settings_name == name
            assert setting.app_settings_value == value
            assert setting.app_settings_type == 'unicode'
            assert isinstance(setting, RhodeCodeSetting)
        finally:
            Session().delete(setting)
            Session().commit()

    def test_setting_is_updated(self, settings_util):
        model = SettingsModel()
        name = 'test_setting'
        value = 'test_value'
        settings_util.create_rhodecode_setting(
            name, value, 'unicode', cleanup=False)

        updated_value = 'test_value_2'
        model.create_or_update_setting(name, val=updated_value)

        setting = model.get_setting_by_name(name)
        try:
            assert setting.app_settings_name == name
            assert setting.app_settings_value == updated_value
            assert setting.app_settings_type == 'unicode'
            assert isinstance(setting, RhodeCodeSetting)
        finally:
            Session().delete(setting)
            Session().commit()


class TestRepoGetAuthSettings(object):
    def test_settings_prefixed_with_auth_are_retured(
            self, repo_stub, settings_util):
        model = SettingsModel(repo=repo_stub.repo_name)
        valid_settings = ('auth_test1', 'auth_test2')
        invalid_settings = ('test1', 'test2')
        fake_value = 'test_value'

        for name in valid_settings + invalid_settings:
            settings_util.create_repo_rhodecode_setting(
                repo_stub, name, fake_value, 'unicode')

        auth_settings = model.get_auth_settings()
        assert auth_settings == {name: fake_value for name in valid_settings}


class TestGlobalGetAuthSettings(object):
    def test_settings_prefixed_with_auth_are_retured(self, settings_util):
        model = SettingsModel()
        valid_settings = ('auth_test1', 'auth_test2')
        invalid_settings = ('test1', 'test2')
        fake_value = 'test_value'

        for name in valid_settings + invalid_settings:
            settings_util.create_rhodecode_setting(name, fake_value, 'unicode')

        auth_settings = model.get_auth_settings()
        for name in auth_settings:
            assert name not in invalid_settings
            if name in valid_settings:
                assert auth_settings[name] == fake_value


class TestGetAuthPlugins(object):
    def test_get_setting_by_name_is_called(self):
        model = SettingsModel()

        fake_value = 'some value'
        result_mock = mock.Mock()
        result_mock.app_settings_value = fake_value

        get_setting_patch = mock.patch.object(
            model, 'get_setting_by_name', return_value=result_mock)

        with get_setting_patch as get_setting_mock:
            result = model.get_auth_plugins()

        get_setting_mock.assert_called_once_with('auth_plugins')
        assert result == fake_value


class TestDefaultRepoSettings(object):
    DEFAULT_SETTINGS_NAMES = ['default_a{}'.format(i) for i in range(10)]
    CUSTOM_SETTINGS_NAMES = ['setting_b_{}'.format(i) for i in range(10)]

    def test_returns_global_settings_prefixed_with_default(
            self, settings_util):
        self._create_values(settings_util)
        model = SettingsModel()
        result = model.get_default_repo_settings()
        self._assert_prefixed_settings(result)

    def test_returns_global_settings_without_default_prefix(
            self, settings_util):
        self._create_values(settings_util)
        model = SettingsModel()
        result = model.get_default_repo_settings(strip_prefix=True)
        self._assert_non_prefixed_settings(result)

    def test_returns_per_repo_settings_prefixed_with_default(
            self, repo_stub, settings_util):
        model = SettingsModel(repo=repo_stub)
        self._create_values(settings_util, repo=repo_stub)
        result = model.get_default_repo_settings()
        self._assert_prefixed_settings(result)

    def test_returns_per_repo_settings_without_default_prefix(
            self, repo_stub, settings_util):
        model = SettingsModel(repo=repo_stub)
        self._create_values(settings_util, repo=repo_stub)
        result = model.get_default_repo_settings(strip_prefix=True)
        self._assert_non_prefixed_settings(result)

    def _create_values(self, settings_util, repo=None):
        for name in self.DEFAULT_SETTINGS_NAMES + self.CUSTOM_SETTINGS_NAMES:
            if not repo:
                settings_util.create_rhodecode_setting(
                    name, 'value', 'unicode')
            else:
                settings_util.create_repo_rhodecode_setting(
                    repo, name, 'value', 'unicode')

    def _assert_prefixed_settings(self, result):
        for setting in self.DEFAULT_SETTINGS_NAMES:
            assert setting in result
            assert result[setting] == 'value'

        for setting in self.CUSTOM_SETTINGS_NAMES:
            assert setting not in result

    def _assert_non_prefixed_settings(self, result):
        for setting in self.DEFAULT_SETTINGS_NAMES:
            setting = setting.replace('default_', '')
            assert setting in result
            assert result[setting] == 'value'


@pytest.fixture
def fake_ui_values():
    return [
        UiSetting(
            'section{}'.format(i % 2), 'key{}'.format(i),
            'value{}'.format(i), True)
        for i in range(10)
    ]
