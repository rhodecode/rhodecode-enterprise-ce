# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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
Whoosh fallback schema for RhodeCode in case rhodecode_tools defined one is
not available
"""

from __future__ import absolute_import

from whoosh.analysis import RegexTokenizer, LowercaseFilter
from whoosh.formats import Characters
from whoosh.fields import (
    TEXT, ID, STORED, NUMERIC, BOOLEAN, Schema, FieldType, DATETIME)

# CUSTOM ANALYZER wordsplit + lowercase filter for case insensitive search
ANALYZER = RegexTokenizer(expression=r"\w+") | LowercaseFilter()

# FILE INDEX SCHEMA DEFINITION
FILE_INDEX_NAME = 'FILE_INDEX'
FILE_SCHEMA = Schema(
    fileid=ID(unique=True),  # Path
    repository=ID(stored=True),
    repository_id=NUMERIC(unique=True, stored=True),  # Numeric id of repo
    repo_name=TEXT(stored=True),
    owner=TEXT(),
    path=TEXT(stored=True),
    content=FieldType(format=Characters(), analyzer=ANALYZER,
                      scorable=True, stored=True),
    modtime=STORED(),
    md5=STORED(),
    extension=ID(stored=True),
    commit_id=TEXT(stored=True),

    size=NUMERIC(stored=True),
    mimetype=TEXT(stored=True),
    lines=NUMERIC(stored=True),
)


# COMMIT INDEX SCHEMA
COMMIT_INDEX_NAME = 'COMMIT_INDEX'
COMMIT_SCHEMA = Schema(
    commit_id=ID(unique=True, stored=True),
    repository=ID(unique=True, stored=True),
    repository_id=NUMERIC(unique=True, stored=True),
    commit_idx=NUMERIC(stored=True, sortable=True),
    commit_idx_sort=ID(),
    date=NUMERIC(stored=True, sortable=True),
    owner=TEXT(stored=True),
    author=TEXT(stored=True),
    message=FieldType(format=Characters(), analyzer=ANALYZER,
                      scorable=True, stored=True),
    parents=TEXT(stored=True),
    added=TEXT(stored=True),  # space separated names of added files
    removed=TEXT(stored=True),  # space separated names of removed files
    changed=TEXT(stored=True),  # space separated names of changed files
)
