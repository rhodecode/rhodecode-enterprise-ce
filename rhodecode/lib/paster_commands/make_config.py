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
depracated make-config paster command for RhodeCode
"""

import os
import sys
from paste.script.appinstall import AbstractInstallCommand
from paste.script.command import BadCommand
from paste.deploy import appconfig

# fix rhodecode import
from os.path import dirname as dn
rc_path = dn(dn(dn(os.path.realpath(__file__))))
sys.path.append(rc_path)

class Command(AbstractInstallCommand):

    default_verbosity = 1
    max_args = None
    min_args = 1
    summary = "*DEPRECATED* Install a package and create a fresh config file/directory"
    usage = "PACKAGE_NAME [CONFIG_FILE] [VAR=VALUE]"

    description = """\
    Note: this is an experimental command, and it will probably change
    in several ways by the next release.

    make-config is part of a two-phase installation process (the
    second phase is setup-app).  make-config installs the package
    (using easy_install) and asks it to create a bare configuration
    file or directory (possibly filling in defaults from the extra
    variables you give).
    """

    parser = AbstractInstallCommand.standard_parser(
        simulate=True, quiet=True, no_interactive=True)

    def command(self):
        sys.stderr.write(
            '** Warning **\n'
            'This command is now removed and depracated, please '
            'use new rhodecode-config command instead.')
        sys.exit(-1)
    def update_parser(self):
        pass
