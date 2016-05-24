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
VCS Backends module
"""

import os
from pprint import pformat

from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import VCSError
from rhodecode.lib.vcs.utils.helpers import get_scm
from rhodecode.lib.vcs.utils.imports import import_class


def get_repo(path=None, alias=None, create=False):
    """
    Returns ``Repository`` object of type linked with given ``alias`` at
    the specified ``path``. If ``alias`` is not given it will try to guess it
    using get_scm method
    """
    if create:
        if not (path or alias):
            raise TypeError(
                "If create is specified, we need path and scm type")
        return get_backend(alias)(path, create=True)
    if path is None:
        path = os.path.abspath(os.path.curdir)
    try:
        scm, path = get_scm(path, search_path_up=True)
        path = os.path.abspath(path)
        alias = scm
    except VCSError:
        raise VCSError("No scm found at %s" % path)
    if alias is None:
        alias = get_scm(path)[0]

    backend = get_backend(alias)
    repo = backend(path, create=create)
    return repo


def get_backend(alias):
    """
    Returns ``Repository`` class identified by the given alias or raises
    VCSError if alias is not recognized or backend class cannot be imported.
    """
    if alias not in settings.BACKENDS:
        raise VCSError(
            "Given alias '%s' is not recognized! Allowed aliases:\n%s" %
            (alias, pformat(settings.BACKENDS.keys())))
    backend_path = settings.BACKENDS[alias]
    klass = import_class(backend_path)
    return klass


def get_supported_backends():
    """
    Returns list of aliases of supported backends.
    """
    return settings.BACKENDS.keys()
