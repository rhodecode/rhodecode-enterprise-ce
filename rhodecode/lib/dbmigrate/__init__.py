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
Database migration modules
"""

import logging

from rhodecode.lib.utils import BasePasterCommand, Command, add_cache
from rhodecode.lib.db_manage import DbManage

log = logging.getLogger(__name__)


class UpgradeDb(BasePasterCommand):
    """Command used for paster to upgrade our database to newer version
    """

    max_args = 1
    min_args = 1

    usage = "CONFIG_FILE"
    summary = "Upgrades current db to newer version"
    group_name = "RhodeCode"

    parser = Command.standard_parser(verbose=True)

    def command(self):
        from pylons import config
        add_cache(config)
        self.logging_file_config(self.path_to_ini_file)

        db_uri = config['sqlalchemy.db1.url']
        dbmanage = DbManage(log_sql=True, dbconf=db_uri,
                            root=config['here'], tests=False,
                            cli_args=self.options.__dict__)
        dbmanage.upgrade()

    def update_parser(self):
        self.parser.add_option('--sql',
                      action='store_true',
                      dest='just_sql',
                      help="Prints upgrade sql for further investigation",
                      default=False)

        self.parser.add_option('--force-yes',
                           action='store_true',
                           dest='force_ask',
                           default=None,
                           help='Force yes to every question')
        self.parser.add_option('--force-no',
                           action='store_false',
                           dest='force_ask',
                           default=None,
                           help='Force no to every question')
