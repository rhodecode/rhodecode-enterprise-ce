# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016  RhodeCode GmbH
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
Various config settings for RhodeCode
"""
from rhodecode import EXTENSIONS

from rhodecode.lib.utils2 import __get_lem


# language map is also used by whoosh indexer, which for those specified
# extensions will index it's content
LANGUAGES_EXTENSIONS_MAP = __get_lem()

# list of readme files to search in file tree and display in summary
# attached weights defines the search  order lower is first
ALL_READMES = [
    ('readme', 0), ('README', 0), ('Readme', 0),
    ('doc/readme', 1), ('doc/README', 1), ('doc/Readme', 1),
    ('Docs/readme', 2), ('Docs/README', 2), ('Docs/Readme', 2),
    ('DOCS/readme', 2), ('DOCS/README', 2), ('DOCS/Readme', 2),
    ('docs/readme', 2), ('docs/README', 2), ('docs/Readme', 2),
]

# extension together with weights to search lower is first
RST_EXTS = [
    ('', 0), ('.rst', 1), ('.rest', 1),
    ('.RST', 2), ('.REST', 2)
]

MARKDOWN_EXTS = [
    ('.md', 1), ('.MD', 1),
    ('.mkdn', 2), ('.MKDN', 2),
    ('.mdown', 3), ('.MDOWN', 3),
    ('.markdown', 4), ('.MARKDOWN', 4)
]

PLAIN_EXTS = [
    ('.text', 2), ('.TEXT', 2),
    ('.txt', 3), ('.TXT', 3)
]

ALL_EXTS = MARKDOWN_EXTS + RST_EXTS + PLAIN_EXTS

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

DATE_FORMAT = "%Y-%m-%d"
