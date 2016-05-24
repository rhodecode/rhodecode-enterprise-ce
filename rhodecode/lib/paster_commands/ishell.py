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
interactive shell paster command for RhodeCode
"""

import os
import sys
import logging

from rhodecode.lib.utils import BasePasterCommand

# fix rhodecode import
from os.path import dirname as dn
rc_path = dn(dn(dn(os.path.realpath(__file__))))
sys.path.append(rc_path)

log = logging.getLogger(__name__)


class Command(BasePasterCommand):

    max_args = 1
    min_args = 1

    usage = "CONFIG_FILE"
    group_name = "RhodeCode"
    takes_config_file = -1
    parser = BasePasterCommand.standard_parser(verbose=True)
    summary = "Interactive shell"

    def command(self):
        #get SqlAlchemy session
        self._init_session()

        # imports, used in ipython shell
        import os
        import sys
        import time
        import shutil
        import datetime
        from rhodecode.model.db import *

        try:
            from IPython import embed
            from IPython.config.loader import Config
            cfg = Config()
            cfg.InteractiveShellEmbed.confirm_exit = False
            embed(config=cfg, banner1="RhodeCode IShell.")
        except ImportError:
            print 'ipython installation required for ishell'
            sys.exit(-1)

    def update_parser(self):
        pass
