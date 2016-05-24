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
from rhodecode.model import meta, init_model_encryption
from rhodecode.lib.dbmigrate.versions import _reset_base, notify

log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_3_3_0_0
    init_model_encryption(db_3_3_0_0)
    fixups(db_3_3_0_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    for repo in models.Repository.get_all():
        _lock_info = repo._locked.split(':') if repo._locked else []
        if len(_lock_info) == 2:
            _lock_info.append(repo.LOCK_AUTOMATIC)
            repo.locked = _lock_info
            _SESSION().add(repo)
            _SESSION().commit()
