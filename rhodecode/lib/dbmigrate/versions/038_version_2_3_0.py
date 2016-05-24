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


def get_by_name(cls, key):
    return cls.query().filter(cls.app_settings_name == key).scalar()


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_2_3_0_1

    # issue fixups
    fixups(db_2_3_0_1, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    notify('Adding revision look items options now...')

    settings = [
        ('show_revision_number', True, 'bool'),
        ('show_sha_length', 12, 'int'),
    ]

    for name, default, type_ in settings:
        setting = get_by_name(models.RhodeCodeSetting, name)
        if not setting:
            # if we don't have this option create it
            setting = models.RhodeCodeSetting(name, default, type_)
        setting._app_settings_type = type_
        _SESSION().add(setting)
        _SESSION().commit()
