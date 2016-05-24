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
    from rhodecode.lib.dbmigrate.schema import db_2_0_0

    # issue fixups
    fixups(db_2_0_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    notify('Fixing default auth modules')
    plugins = 'rhodecode.lib.auth_modules.auth_rhodecode'
    opts = []
    ldap_enabled = str2bool(getattr(
        get_by_name(models.RhodeCodeSetting, 'ldap_active'),
        'app_settings_value', False))
    if ldap_enabled:
        plugins += ',rhodecode.lib.auth_modules.auth_ldap'
        opts.append(('auth_ldap_enabled', 'True', 'bool'))

    opts.append(('auth_plugins', plugins, 'list'),)
    opts.append(('auth_rhodecode_enabled', 'True', 'bool'))

    for name, default, type_ in opts:
        setting = get_by_name(models.RhodeCodeSetting, name)
        if not setting:
            # if we don't have this option create it
            setting = models.RhodeCodeSetting(name, default, type_)

        _SESSION().add(setting)
        _SESSION().commit()

    #copy over the LDAP settings
    old_ldap = [('ldap_active', 'false', 'bool'), ('ldap_host', '', 'unicode'),
                ('ldap_port', '389', 'int'), ('ldap_tls_kind', 'PLAIN', 'unicode'),
                ('ldap_tls_reqcert', '', 'unicode'), ('ldap_dn_user', '', 'unicode'),
                ('ldap_dn_pass', '', 'unicode'), ('ldap_base_dn', '', 'unicode'),
                ('ldap_filter', '', 'unicode'), ('ldap_search_scope', '', 'unicode'),
                ('ldap_attr_login', '', 'unicode'), ('ldap_attr_firstname', '', 'unicode'),
                ('ldap_attr_lastname', '', 'unicode'), ('ldap_attr_email', '', 'unicode')]
    for k, v, t in old_ldap:
        old_setting = get_by_name(models.RhodeCodeSetting, k)
        name = 'auth_%s' % k
        setting = get_by_name(models.RhodeCodeSetting, name)
        if not setting:
            # if we don't have this option create it
            setting = models.RhodeCodeSetting(name, old_setting.app_settings_value, t)

        _SESSION().add(setting)
        _SESSION().commit()
