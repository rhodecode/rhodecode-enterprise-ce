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

import rhodecode
from rhodecode.model.settings import SettingsModel
from rhodecode.tests import url, HG_REPO
from rhodecode.tests.utils import AssertResponse


@pytest.mark.usefixtures('autologin_user', 'app')
class TestAdminRepoSettingsController:
    @pytest.mark.parametrize('urlname', [
        'edit_repo',
        'edit_repo_perms',
        'edit_repo_advanced',
        'repo_vcs_settings',
        'edit_repo_fields',
        'repo_settings_issuetracker',
        'edit_repo_caches',
        'edit_repo_remote',
        'edit_repo_statistics',
    ])
    def test_simple_get(self, urlname, app):
        app.get(url(urlname, repo_name=HG_REPO))

    @pytest.mark.parametrize('setting_name, setting_backends', [
        ('hg_use_rebase_for_merging', ['hg']),
    ])
    def test_labs_settings_visible_if_enabled(
            self, setting_name, setting_backends, backend):
        if backend.alias not in setting_backends:
            pytest.skip('Setting not available for backend {}'.format(backend))

        vcs_settings_url = url(
            'repo_vcs_settings', repo_name=backend.repo.repo_name)

        with mock.patch.dict(
                rhodecode.CONFIG, {'labs_settings_active': 'true'}):
            response = self.app.get(vcs_settings_url)

        assertr = AssertResponse(response)
        assertr.one_element_exists('#rhodecode_{}'.format(setting_name))

    @pytest.mark.parametrize('setting_name, setting_backends', [
        ('hg_use_rebase_for_merging', ['hg']),
    ])
    def test_labs_settings_not_visible_if_disabled(
            self, setting_name, setting_backends, backend):
        if backend.alias not in setting_backends:
            pytest.skip('Setting not available for backend {}'.format(backend))

        vcs_settings_url = url(
            'repo_vcs_settings', repo_name=backend.repo.repo_name)

        with mock.patch.dict(
                rhodecode.CONFIG, {'labs_settings_active': 'false'}):
            response = self.app.get(vcs_settings_url)

        assertr = AssertResponse(response)
        assertr.no_element_exists('#rhodecode_{}'.format(setting_name))

    @pytest.mark.parametrize('setting_name, setting_backends', [
        ('hg_use_rebase_for_merging', ['hg']),
    ])
    def test_update_boolean_settings(
            self, csrf_token, setting_name, setting_backends, backend):
        if backend.alias not in setting_backends:
            pytest.skip('Setting not available for backend {}'.format(backend))

        settings_model = SettingsModel(repo=backend.repo)
        vcs_settings_url = url(
            'repo_vcs_settings', repo_name=backend.repo.repo_name)

        self.app.post(
            vcs_settings_url,
            params={
                'new_svn_branch': 'dummy-value-for-testing',
                'new_svn_tag': 'dummy-value-for-testing',
                'rhodecode_{}'.format(setting_name): 'true',
                'csrf_token': csrf_token,
            })
        setting = settings_model.get_setting_by_name(setting_name)
        assert setting.app_settings_value

        self.app.post(
            vcs_settings_url,
            params={
                'new_svn_branch': 'dummy-value-for-testing',
                'new_svn_tag': 'dummy-value-for-testing',
                'rhodecode_{}'.format(setting_name): 'false',
                'csrf_token': csrf_token,
            })
        setting = settings_model.get_setting_by_name(setting_name)
        assert not setting.app_settings_value
