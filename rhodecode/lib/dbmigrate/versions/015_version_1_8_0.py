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


def get_by_name(cls, key):
    return cls.query().filter(cls.app_settings_name == key).scalar()


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_1_8_0
    tbl = db_1_8_0.RhodeCodeSetting.__table__
    app_settings_type = Column("app_settings_type",
                               String(255, convert_unicode=False),
                               nullable=True, unique=None, default=None)
    app_settings_type.create(table=tbl)

    # issue fixups
    fixups(db_1_8_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    notify('Fixing default options now...')

    settings = [
        #general
        ('realm', '', 'unicode'),
        ('title', '', 'unicode'),
        ('ga_code', '', 'unicode'),
        ('show_public_icon', False, 'bool'),
        ('show_private_icon', True, 'bool'),
        ('stylify_metatags', True, 'bool'),

        # defaults
        ('default_repo_enable_locking',  False, 'bool'),
        ('default_repo_enable_downloads', False, 'bool'),
        ('default_repo_enable_statistics', False, 'bool'),
        ('default_repo_private', False, 'bool'),
        ('default_repo_type', 'hg', 'unicode'),

        #other
        ('dashboard_items', 100, 'int'),
        ('show_version', True, 'bool')
    ]

    for name, default, type_ in settings:
        setting = get_by_name(models.RhodeCodeSetting, name)
        if not setting:
            # if we don't have this option create it
            setting = models.RhodeCodeSetting(name, default, type_)

        # fix certain key to new defaults
        if name in ['title', 'show_public_icon']:
            # change title if it's only the default
            if name == 'title' and setting.app_settings_value == 'RhodeCode':
                setting.app_settings_value = default
            else:
                setting.app_settings_value = default

        setting._app_settings_type = type_
        _SESSION().add(setting)
        _SESSION().commit()
