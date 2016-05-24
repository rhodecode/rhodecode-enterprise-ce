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
    from pylons import config
    from rhodecode.lib.utils2 import str2bool

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

    notify('migrating options from .ini file')
    use_gravatar = str2bool(config.get('use_gravatar'))
    print('Setting gravatar use to: %s' % use_gravatar)
    sett = create_or_update(models.RhodeCodeSetting,
        'use_gravatar', use_gravatar, 'bool')
    _SESSION().add(sett)
    _SESSION.commit()
    # set the new format of gravatar URL
    gravatar_url = models.User.DEFAULT_GRAVATAR_URL
    if config.get('alternative_gravatar_url'):
        gravatar_url = config.get('alternative_gravatar_url')

    print('Setting gravatar url to:%s' % gravatar_url)
    sett = create_or_update(models.RhodeCodeSetting,
        'gravatar_url', gravatar_url, 'unicode')
    _SESSION().add(sett)
    _SESSION.commit()

    # now create new changed value of clone_url
    clone_uri_tmpl = models.Repository.DEFAULT_CLONE_URI
    print('settings new clone url template to %s' % clone_uri_tmpl)

    sett = create_or_update(models.RhodeCodeSetting,
        'clone_uri_tmpl', clone_uri_tmpl, 'unicode')
    _SESSION().add(sett)
    _SESSION.commit()
