import logging
import datetime

from sqlalchemy import *
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import relation, backref, class_mapper, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base

from rhodecode.lib.dbmigrate.migrate import *
from rhodecode.lib.dbmigrate.migrate.changeset import *

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
    from rhodecode.lib.dbmigrate.schema import db_2_0_0
    tbl = db_2_0_0.UserGroup.__table__

    user_group_description = Column("user_group_description",
                                    String(10000, convert_unicode=False),
                                    nullable=True, unique=None, default=None)
    user_group_description.create(table=tbl)

    created_on = Column('created_on', DateTime(timezone=False),
                        nullable=True, default=datetime.datetime.now)
    created_on.create(table=tbl)

    # issue fixups
    fixups(db_2_0_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    notify('Fixing default created on')

    for gr in models.UserGroup.get_all():
        gr.created_on = datetime.datetime.now()
        _SESSION().commit()
