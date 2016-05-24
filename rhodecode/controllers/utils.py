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
Utilities to be shared by multiple controllers.

Should only contain utilities to be shared in the controller layer.
"""

from rhodecode.lib import helpers as h
from rhodecode.lib.vcs.exceptions import RepositoryError

def parse_path_ref(ref, default_path=None):
    """
    Parse out a path and reference combination and return both parts of it.

    This is used to allow support of path based comparisons for Subversion
    as an iterim solution in parameter handling.
    """
    if '@' in ref:
        return ref.rsplit('@', 1)
    else:
        return default_path, ref


def get_format_ref_id(repo):
    """Returns a `repo` specific reference formatter function"""
    if h.is_svn(repo):
        return _format_ref_id_svn
    else:
        return _format_ref_id


def _format_ref_id(name, raw_id):
    """Default formatting of a given reference `name`"""
    return name


def _format_ref_id_svn(name, raw_id):
    """Special way of formatting a reference for Subversion including path"""
    return '%s@%s' % (name, raw_id)


def get_commit_from_ref_name(repo, ref_name, ref_type=None):
    """
    Gets the commit for a `ref_name` taking into account `ref_type`.
    Needed in case a bookmark / tag share the same name.

    :param repo: the repo instance
    :param ref_name: the name of the ref to get
    :param ref_type: optional, used to disambiguate colliding refs
    """
    repo_scm = repo.scm_instance()
    ref_type_mapping = {
        'book': repo_scm.bookmarks,
        'bookmark': repo_scm.bookmarks,
        'tag': repo_scm.tags,
        'branch': repo_scm.branches,
    }

    commit_id = ref_name
    if repo_scm.alias != 'svn': # pass svn refs straight to backend until
                                # the branch issue with svn is fixed
        if ref_type and ref_type in ref_type_mapping:
            try:
                commit_id = ref_type_mapping[ref_type][ref_name]
            except KeyError:
                raise RepositoryError(
                    '%s "%s" does not exist' % (ref_type, ref_name))

    return repo_scm.get_commit(commit_id)
