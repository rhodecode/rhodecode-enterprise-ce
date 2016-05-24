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
    from rhodecode.lib.dbmigrate.schema import db_2_1_0

    # issue fixups
    fixups(db_2_1_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    Optional = models.Optional

    def get_by_name(cls, key):
        return cls.query().filter(cls.app_settings_name == key).scalar()

    def create_or_update(cls, key, val=Optional(''), type=Optional('unicode')):
        res = get_by_name(cls, key)
        if not res:
            val = Optional.extract(val)
            type = Optional.extract(type)
            res = cls(key, val, type)
        else:
            res.app_settings_name = key
            if not isinstance(val, Optional):
                # update if set
                res.app_settings_value = val
            if not isinstance(type, Optional):
                # update if set
                res.app_settings_type = type
        return res

    notify('Creating upgrade URL')
    sett = create_or_update(models.RhodeCodeSetting,
        'update_url', models.RhodeCodeSetting.DEFAULT_UPDATE_URL, 'unicode')
    _SESSION().add(sett)
    _SESSION.commit()
