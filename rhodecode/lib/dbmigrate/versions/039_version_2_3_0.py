import logging
import datetime

from sqlalchemy import *
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import relation, backref, class_mapper, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base

from rhodecode.lib.dbmigrate.migrate import *
from rhodecode.lib.dbmigrate.migrate.changeset import *
from rhodecode.lib.utils2 import str2bool

from rhodecode.model.meta import Base
from rhodecode.model import meta
from rhodecode.lib.dbmigrate.versions import _reset_base, notify

log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_2_3_0_2

    tbl = db_2_3_0_2.PullRequest.__table__

    _last_merge_org_rev = Column('last_merge_org_rev', String(40), nullable=True)
    _last_merge_other_rev = Column('last_merge_other_rev', String(40), nullable=True)
    _last_merge_status = Column('merge_status', Integer(), nullable=True)
    merge_rev = Column('merge_rev', String(40), nullable=True)
    _last_merge_org_rev.create(table=tbl)
    _last_merge_other_rev.create(table=tbl)
    _last_merge_status.create(table=tbl)
    merge_rev.create(table=tbl)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
