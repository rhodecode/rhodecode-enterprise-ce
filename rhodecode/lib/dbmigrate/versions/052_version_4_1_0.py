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

PLUGIN_RENAME_MAP = {
    'egg:rhodecode-enterprise-ce#container': 'egg:rhodecode-enterprise-ce#headers',
}

SETTINGS_RENAME_MAP = {
    'auth_container_cache_ttl': 'auth_headers_cache_ttl',
    'auth_container_clean_username': 'auth_headers_clean_username',
    'auth_container_enabled': 'auth_headers_enabled',
    'auth_container_fallback_header': 'auth_headers_fallback_header',
    'auth_container_header': 'auth_headers_header',
}


def rename_plugins(models, Session):
    query = models.RhodeCodeSetting.query().filter(
        models.RhodeCodeSetting.app_settings_name == AUTH_PLUGINS_SETTING)
    plugin_setting = query.scalar()
    plugins = plugin_setting.app_settings_value

    new_plugins = []

    for plugin_id in plugins:
        new_plugin_id = PLUGIN_RENAME_MAP.get(plugin_id, None)
        if new_plugin_id:
            new_plugins.append(new_plugin_id)
        else:
            new_plugins.append(plugin_id)

    plugin_setting.app_settings_value = ','.join(new_plugins)

    log.info("Rename of auth plugin IDs")
    log.info("Original setting value: %s", plugins)
    log.info("New setting value: %s", new_plugins)


def rename_plugin_settings(models, Session):
    for old_name, new_name in SETTINGS_RENAME_MAP.items():
        query = models.RhodeCodeSetting.query().filter(
            models.RhodeCodeSetting.app_settings_name == old_name)
        setting = query.scalar()
        if setting:
            setting.app_settings_name = new_name
            log.info(
                'Rename of plugin setting "%s" to "%s"', old_name, new_name)


def fixups(models, Session):
    rename_plugins(models, Session)
    rename_plugin_settings(models, Session)

    Session().commit()
