# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016  RhodeCode GmbH
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
Disable VCS pages when VCS Server is not available
"""

import logging
import re


log = logging.getLogger(__name__)


class DisableVCSPagesWrapper(object):
    """
    Wrapper to disable all pages that require VCS Server to be running,
    avoiding that errors explode to the user.

    This Wrapper should be enabled only in case VCS Server is not available
    for the instance.
    """

    VCS_NOT_REQUIRED = [
        '^/$',
        ('/_admin(?!/settings/mapping)(?!/my_account/repos)'
         '(?!/create_repository)(?!/gists)(?!/notifications/)'
         ),
    ]
    _REGEX_VCS_NOT_REQUIRED = [re.compile(path) for path in VCS_NOT_REQUIRED]

    def _check_vcs_requirement(self, path_info):
        """
        Tries to match the current path to one of the safe URLs to be rendered.
        Displays an error message in case
        """
        for regex in self._REGEX_VCS_NOT_REQUIRED:
            safe_url = regex.match(path_info)
            if safe_url:
                return True

        # Url is not safe to be rendered without VCS Server
        log.debug('accessing: `%s` with VCS Server disabled', path_info)
        return False

    def __init__(self, app):
        self.application = app

    def __call__(self, environ, start_response):
        if not self._check_vcs_requirement(environ['PATH_INFO']):
            environ['PATH_INFO'] = '/error/vcs_unavailable'

        return self.application(environ, start_response)
