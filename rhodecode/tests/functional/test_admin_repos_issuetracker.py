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

from rhodecode.lib.utils2 import md5
from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel, IssueTrackerSettingsModel
from rhodecode.tests import url


@pytest.mark.usefixtures("app")
class TestAdminRepos:
    def test_issuetracker_index(self, autologin_user, backend):
        repo = backend.create_repo()
        response = self.app.get(url('repo_settings_issuetracker',
                                repo_name=repo.repo_name))
        assert response.status_code == 200

    def test_add_issuetracker_patterns(
            self, autologin_user, backend, csrf_token, request):
        pattern = 'issuetracker_pat'
        another_pattern = pattern+'1'
        post_url = url('repo_issuetracker_save',
                       repo_name=backend.repo.repo_name)
        post_data = {
            'new_pattern_pattern_0': pattern,
            'new_pattern_url_0': 'url',
            'new_pattern_prefix_0': 'prefix',
            'new_pattern_description_0': 'description',
            'new_pattern_pattern_1': another_pattern,
            'new_pattern_url_1': 'url1',
            'new_pattern_prefix_1': 'prefix1',
            'new_pattern_description_1': 'description1',
            'csrf_token': csrf_token
        }
        self.app.post(post_url, post_data, status=302)
        self.settings_model = IssueTrackerSettingsModel(repo=backend.repo)
        settings = self.settings_model.get_repo_settings()
        self.uid = md5(pattern)
        assert settings[self.uid]['pat'] == pattern
        self.another_uid = md5(another_pattern)
        assert settings[self.another_uid]['pat'] == another_pattern

        @request.addfinalizer
        def cleanup():
            self.settings_model.delete_entries(self.uid)
            self.settings_model.delete_entries(self.another_uid)

    def test_edit_issuetracker_pattern(
            self, autologin_user, backend, csrf_token, request):
        entry_key = 'issuetracker_pat_'
        pattern = 'issuetracker_pat2'
        old_pattern = 'issuetracker_pat'
        old_uid = md5(old_pattern)

        sett = SettingsModel(repo=backend.repo).create_or_update_setting(
            entry_key+old_uid, old_pattern, 'unicode')
        Session().add(sett)
        Session().commit()
        post_url = url('repo_issuetracker_save',
                       repo_name=backend.repo.repo_name)
        post_data = {
            'new_pattern_pattern_0': pattern,
            'new_pattern_url_0': 'url',
            'new_pattern_prefix_0': 'prefix',
            'new_pattern_description_0': 'description',
            'uid': old_uid,
            'csrf_token': csrf_token
        }
        self.app.post(post_url, post_data, status=302)
        self.settings_model = IssueTrackerSettingsModel(repo=backend.repo)
        settings = self.settings_model.get_repo_settings()
        self.uid = md5(pattern)
        assert settings[self.uid]['pat'] == pattern
        with pytest.raises(KeyError):
            settings[old_uid]

        @request.addfinalizer
        def cleanup():
            self.settings_model.delete_entries(self.uid)

    def test_delete_issuetracker_pattern(
            self, autologin_user, backend, csrf_token, settings_util):
        repo = backend.create_repo()
        entry_key = 'issuetracker_pat_'
        pattern = 'issuetracker_pat3'
        uid = md5(pattern)
        settings_util.create_repo_rhodecode_setting(
            repo=backend.repo, name=entry_key+uid,
            value=entry_key, type_='unicode', cleanup=False)

        self.app.post(
            url('repo_issuetracker_delete',
                repo_name=backend.repo.repo_name),
            {
                '_method': 'delete',
                'uid': uid,
                'csrf_token': csrf_token
            }, status=302)
        settings = IssueTrackerSettingsModel(repo=repo).get_repo_settings()
        assert 'rhodecode_%s%s' % (entry_key, uid) not in settings
