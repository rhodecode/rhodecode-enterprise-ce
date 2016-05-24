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

import logging


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = xrange(30, 38)

# Sequences
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[0;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'CRITICAL': MAGENTA,
    'ERROR': RED,
    'WARNING': CYAN,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'SQL': YELLOW
}


def one_space_trim(s):
    if s.find("  ") == -1:
        return s
    else:
        s = s.replace('  ', ' ')
        return one_space_trim(s)


def format_sql(sql):
    sql = sql.replace('\n', '')
    sql = one_space_trim(sql)
    sql = sql\
        .replace(',', ',\n\t')\
        .replace('SELECT', '\n\tSELECT \n\t')\
        .replace('UPDATE', '\n\tUPDATE \n\t')\
        .replace('DELETE', '\n\tDELETE \n\t')\
        .replace('FROM', '\n\tFROM')\
        .replace('ORDER BY', '\n\tORDER BY')\
        .replace('LIMIT', '\n\tLIMIT')\
        .replace('WHERE', '\n\tWHERE')\
        .replace('AND', '\n\tAND')\
        .replace('LEFT', '\n\tLEFT')\
        .replace('INNER', '\n\tINNER')\
        .replace('INSERT', '\n\tINSERT')\
        .replace('DELETE', '\n\tDELETE')
    return sql


class Pyro4AwareFormatter(logging.Formatter):
    """
    Extended logging formatter which prints out Pyro4 remote tracebacks.
    """

    def formatException(self, ei):
        ex_type, ex_value, ex_tb = ei
        if hasattr(ex_value, '_pyroTraceback'):
            # johbo: Avoiding to import pyro4 until we get an exception
            # which actually has a remote traceback. This avoids issues
            # when gunicorn is used with gevent, since the logging would
            # trigger an import of Pyro4 before the patches of gevent
            # are applied.
            import Pyro4.util
            return ''.join(
                Pyro4.util.getPyroTraceback(ex_type, ex_value, ex_tb))
        return logging.Formatter.formatException(self, ei)


class ColorFormatter(Pyro4AwareFormatter):

    def format(self, record):
        """
        Changes record's levelname to use with COLORS enum
        """

        levelname = record.levelname
        start = COLOR_SEQ % (COLORS[levelname])
        def_record = logging.Formatter.format(self, record)
        end = RESET_SEQ

        colored_record = ''.join([start, def_record, end])
        return colored_record


class ColorFormatterSql(logging.Formatter):

    def format(self, record):
        """
        Changes record's levelname to use with COLORS enum
        """

        start = COLOR_SEQ % (COLORS['SQL'])
        def_record = format_sql(logging.Formatter.format(self, record))
        end = RESET_SEQ

        colored_record = ''.join([start, def_record, end])
        return colored_record
