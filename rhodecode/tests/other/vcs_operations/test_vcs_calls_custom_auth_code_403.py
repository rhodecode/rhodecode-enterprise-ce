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

"""
Test suite for making push/pull operations, on specially modified INI files

.. important::

   You must have git >= 1.8.5 for tests to work fine. With 68b939b git started
   to redirect things to stderr instead of stdout.
"""

import pytest

from rhodecode.tests import (GIT_REPO, HG_REPO)
from rhodecode.tests.other.vcs_operations import Command


# override rc_web_server_config fixture with custom INI
@pytest.fixture(scope='module')
def rc_web_server_config(testini_factory):
    CUSTOM_PARAMS = [
        {'app:main': {'auth_ret_code': '403'}},
        {'app:main': {'auth_ret_code_detection': 'true'}},
    ]
    return testini_factory(CUSTOM_PARAMS)


@pytest.mark.usefixtures("disable_locking")
class TestVCSOperationsOnCustomIniConfig:

    def test_clone_wrong_credentials_hg_ret_code(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(HG_REPO, passwd='bad!')
        stdout, stderr = Command('/tmp').execute(
            'hg clone', clone_url, tmpdir.strpath)
        assert 'abort: HTTP Error 403: Forbidden' in stderr

    def test_clone_wrong_credentials_git_ret_code(self, rc_web_server, tmpdir):
        clone_url = rc_web_server.repo_clone_url(GIT_REPO, passwd='bad!')
        stdout, stderr = Command('/tmp').execute(
            'git clone', clone_url, tmpdir.strpath)
        assert 'The requested URL returned error: 403' in stderr
