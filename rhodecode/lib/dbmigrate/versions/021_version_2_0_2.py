import os
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


def get_by_key(cls, key):
    return cls.query().filter(cls.ui_key == key).scalar()


def get_repos_location(cls):
    return get_by_key(cls, '/').ui_value


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_2_0_1
    tbl = db_2_0_1.RepoGroup.__table__

    created_on = Column('created_on', DateTime(timezone=False), nullable=True,
                        default=datetime.datetime.now)
    created_on.create(table=tbl)

    #fix null values on certain columns when upgrading from older releases
    tbl = db_2_0_1.UserLog.__table__
    col = tbl.columns.user_id
    col.alter(nullable=True)

    tbl = db_2_0_1.UserFollowing.__table__
    col = tbl.columns.follows_repository_id
    col.alter(nullable=True)

    tbl = db_2_0_1.UserFollowing.__table__
    col = tbl.columns.follows_user_id
    col.alter(nullable=True)

    # issue fixups
    fixups(db_2_0_1, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    notify('Fixing default created on for repo groups')

    for gr in models.RepoGroup.get_all():
        gr.created_on = datetime.datetime.now()
        _SESSION().add(gr)
        _SESSION().commit()

    repo_store_path = get_repos_location(models.RhodeCodeUi)
    _store = os.path.join(repo_store_path, '.cache', 'largefiles')
    notify('Setting largefiles usercache')
    print _store

    if not models.RhodeCodeUi.query().filter(
                    models.RhodeCodeUi.ui_key == 'usercache').scalar():
        largefiles = models.RhodeCodeUi()
        largefiles.ui_section = 'largefiles'
        largefiles.ui_key = 'usercache'
        largefiles.ui_value = _store
        _SESSION().add(largefiles)
        _SESSION().commit()
