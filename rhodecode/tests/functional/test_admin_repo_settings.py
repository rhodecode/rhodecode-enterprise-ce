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

from rhodecode.tests import url, HG_REPO


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
