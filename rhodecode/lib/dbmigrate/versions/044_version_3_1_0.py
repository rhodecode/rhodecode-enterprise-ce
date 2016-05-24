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
    from rhodecode.lib.dbmigrate.schema import db_3_1_0_1

    # Add table for PullRequestVersion
    tbl = db_3_1_0_1.PullRequestVersion.__table__
    tbl.create()

    # Add pull_request_version to ChangesetComment
    tbl = db_3_1_0_1.ChangesetComment.__table__
    pull_request_version_id = Column(
        "pull_request_version_id", Integer(),
        ForeignKey('pull_request_versions.pull_request_version_id'),
        nullable=True)
    pull_request_version_id.create(table=tbl)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
