# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# RhodeCode Enterprise Edition, including its added features, Support services,
# and proprietary license terms, please see https://rhodecode.com/licenses/


def get_plugin_settings(prefix, settings):
    """
    Returns plugin settings. Use::

    :param prefix:
    :param settings:
    :return:
    """
    prefix = prefix + '.' if not prefix.endswith('.') else prefix
    plugin_settings = {}
    for k, v in settings.items():
        if k.startswith(prefix):
            plugin_settings[k[len(prefix):]] = v

    return plugin_settings


def register_rhodecode_plugin(config, plugin_name, plugin_config):
    def register():
        if plugin_name not in config.registry.rhodecode_plugins:
            config.registry.rhodecode_plugins[plugin_name] = {
                'javascript': None,
                'static': None,
                'css': None,
                'nav': None,
                'fulltext_indexer': None,
                'sqlalchemy_migrations': None,
                'default_values_setter': None,
                'url_gen': None,
                'template_hooks': {}
            }
        config.registry.rhodecode_plugins[plugin_name].update(
            plugin_config)

    config.action(
        'register_rhodecode_plugin={}'.format(plugin_name), register)
