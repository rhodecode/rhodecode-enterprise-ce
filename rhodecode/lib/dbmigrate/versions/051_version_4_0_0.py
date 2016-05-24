# -*- coding: utf-8 -*-

import logging

from sqlalchemy.orm.attributes import flag_modified

from rhodecode.lib.dbmigrate.versions import _reset_base
from rhodecode.model import init_model_encryption, meta

log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_3_7_0_0
    init_model_encryption(db_3_7_0_0)
    fixups(db_3_7_0_0, meta.Session)


def downgrade(migrate_engine):
    pass


AUTH_PLUGINS_SETTING = "auth_plugins"

PLUGIN_ID_MAP = {
    'rhodecode.lib.auth_modules.auth_crowd': 'egg:rhodecode-enterprise-ce#crowd',
    'rhodecode.lib.auth_modules.auth_container': 'egg:rhodecode-enterprise-ce#container',
    'rhodecode.lib.auth_modules.auth_jasig_cas': 'egg:rhodecode-enterprise-ce#jasig_cas',
    'rhodecode.lib.auth_modules.auth_ldap': 'egg:rhodecode-enterprise-ce#ldap',
    'rhodecode.lib.auth_modules.auth_pam': 'egg:rhodecode-enterprise-ce#pam',
    'rhodecode.lib.auth_modules.auth_rhodecode': 'egg:rhodecode-enterprise-ce#rhodecode',

    'rhodecode.lib.auth_modules.auth_bitbucket': 'egg:rhodecode-enterprise-ee#bitbucket',
    'rhodecode.lib.auth_modules.auth_github': 'egg:rhodecode-enterprise-ee#github',
    'rhodecode.lib.auth_modules.auth_google': 'egg:rhodecode-enterprise-ee#google',
    'rhodecode.lib.auth_modules.auth_ldap_group': 'egg:rhodecode-enterprise-ee#ldap_group',
    'rhodecode.lib.auth_modules.auth_token': 'egg:rhodecode-enterprise-ee#token',
    'rhodecode.lib.auth_modules.auth_twitter': 'egg:rhodecode-enterprise-ee#twitter',
}


def fixups(models, Session):

    query = models.RhodeCodeSetting.query().filter(
        models.RhodeCodeSetting.app_settings_name == AUTH_PLUGINS_SETTING)
    plugin_setting = query.scalar()
    plugins = plugin_setting.app_settings_value

    new_plugins = []
    missed_plugins = []

    for plugin_id in plugins:
        new_plugin_id = PLUGIN_ID_MAP.get(plugin_id, None)
        if new_plugin_id:
            new_plugins.append(new_plugin_id)
        else:
            new_plugins.append(plugin_id)
            missed_plugins.append(plugin_id)

    plugin_setting.app_settings_value = ','.join(new_plugins)

    log.info("Migration of the auth plugin IDs")
    log.info("Original setting value: %s", plugins)
    log.info("New setting value: %s", new_plugins)
    if missed_plugins:
        log.warning("Unknown plugin ids: %s", missed_plugins)
        log.warning(
            "Please check the auth settings and re-enable needed plugins.")

    Session().commit()
