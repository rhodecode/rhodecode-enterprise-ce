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

RhodeCode, a web based repository management software
versioning implementation: http://www.python.org/dev/peps/pep-0386/
"""

import os
import sys
import platform

VERSION = tuple(open(os.path.join(
    os.path.dirname(__file__), 'VERSION')).read().split('.'))

BACKENDS = {
    'hg': 'Mercurial repository',
    'git': 'Git repository',
    'svn': 'Subversion repository',
}

CELERY_ENABLED = False
CELERY_EAGER = False

# link to config for pylons
CONFIG = {}

# Linked module for extensions
EXTENSIONS = {}

__version__ = ('.'.join((str(each) for each in VERSION[:3])))
__dbversion__ = 55  # defines current db version for migrations
__platform__ = platform.system()
__license__ = 'AGPLv3, and Commercial License'
__author__ = 'RhodeCode GmbH'
__url__ = 'http://rhodecode.com'

is_windows = __platform__ in ['Windows']
is_unix = not is_windows
is_test = False
