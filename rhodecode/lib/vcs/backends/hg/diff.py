# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016  RhodeCode GmbH
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
GIT diff module
"""

import re

from rhodecode.lib.vcs.backends import base


class MercurialDiff(base.Diff):

    _header_re = re.compile(r"""
        #^diff[ ]--git
            [ ]"?a/(?P<a_path>.+?)"?[ ]"?b/(?P<b_path>.+?)"?\n
        (?:^old[ ]mode[ ](?P<old_mode>\d+)\n
           ^new[ ]mode[ ](?P<new_mode>\d+)(?:\n|$))?
        (?:^similarity[ ]index[ ](?P<similarity_index>\d+)%(?:\n|$))?
        (?:^rename[ ]from[ ](?P<rename_from>[^\r\n]+)\n
           ^rename[ ]to[ ](?P<rename_to>[^\r\n]+)(?:\n|$))?
        (?:^copy[ ]from[ ](?P<copy_from>[^\r\n]+)\n
           ^copy[ ]to[ ](?P<copy_to>[^\r\n]+)(?:\n|$))?
        (?:^new[ ]file[ ]mode[ ](?P<new_file_mode>.+)(?:\n|$))?
        (?:^deleted[ ]file[ ]mode[ ](?P<deleted_file_mode>.+)(?:\n|$))?
        (?:^index[ ](?P<a_blob_id>[0-9A-Fa-f]+)
            \.\.(?P<b_blob_id>[0-9A-Fa-f]+)[ ]?(?P<b_mode>.+)?(?:\n|$))?
        (?:^(?P<bin_patch>GIT[ ]binary[ ]patch)(?:\n|$))?
        (?:^---[ ](a/(?P<a_file>.+)|/dev/null)(?:\n|$))?
        (?:^\+\+\+[ ](b/(?P<b_file>.+)|/dev/null)(?:\n|$))?
    """, re.VERBOSE | re.MULTILINE)
