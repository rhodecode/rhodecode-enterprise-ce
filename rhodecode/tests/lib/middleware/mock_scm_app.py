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
Provides a mock implementation of the scm_app module.

It resembles the same API as :mod:`rhodecode.lib.middleware.utils.scm_app`
for testing purposes.
"""
import mock


def create_git_wsgi_app(repo_path, repo_name, config):
    return mock_git_wsgi


def create_hg_wsgi_app(repo_path, repo_name, config):
    return mock_hg_wsgi


# Utilities to ease testing

mock_hg_wsgi = mock.Mock()
mock_git_wsgi = mock.Mock()
