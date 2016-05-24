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

from rhodecode.lib.vcs.exceptions import VCSError


def import_class(class_path):
    """
    Returns class from the given path.

    For example, in order to get class located at
    ``vcs.backends.hg.MercurialRepository``:

        try:
            hgrepo = import_class('vcs.backends.hg.MercurialRepository')
        except VCSError:
            # hadle error
    """
    splitted = class_path.split('.')
    mod_path = '.'.join(splitted[:-1])
    class_name = splitted[-1]
    try:
        class_mod = __import__(mod_path, {}, {}, [class_name])
    except ImportError as err:
        msg = "There was problem while trying to import backend class. "\
            "Original error was:\n%s" % err
        raise VCSError(msg)
    cls = getattr(class_mod, class_name)

    return cls
