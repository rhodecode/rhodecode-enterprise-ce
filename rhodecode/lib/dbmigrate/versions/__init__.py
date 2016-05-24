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
Package containing new versions of database models
"""

from sqlalchemy import *
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import relation, backref, class_mapper, joinedload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from rhodecode.lib.dbmigrate.migrate import *
from rhodecode.lib.dbmigrate.migrate.changeset import *

from rhodecode.model import meta


def notify(msg, caps=True):
    """
    Notification for migrations messages
    """
    ml = len(msg) + (4 * 2)
    formatted_msg = ('\n%s\n*** %s ***\n%s' % ('*' * ml, msg, '*' * ml))
    if caps:
        formatted_msg = formatted_msg.upper()
    print(formatted_msg)


def _reset_base(migrate_engine):
    ## RESET COMPLETLY THE metadata for sqlalchemy to use previous declared Base
    Base = declarative_base()
    Base.metadata.clear()
    Base.metadata = MetaData()
    Base.metadata.bind = migrate_engine

    # new session and base
    #meta.Session = scoped_session(sessionmaker(expire_on_commit=True,))
    #meta.Session.configure(bind=migrate_engine)
    meta.Base = Base

    notify('SQLA BASE RESET !')
