# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
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

"""
Authentication modules
"""

import logging
import time
import traceback

from pyramid.threadlocal import get_current_registry
from sqlalchemy.ext.hybrid import hybrid_property

from rhodecode.authentication.interface import IAuthnPluginRegistry
from rhodecode.authentication.schema import AuthnPluginSettingsSchemaBase
from rhodecode.lib import caches
from rhodecode.lib.auth import PasswordGenerator, _RhodeCodeCryptoBCrypt
from rhodecode.lib.utils2 import md5_safe, safe_int
from rhodecode.lib.utils2 import safe_str
from rhodecode.model.db import User
from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel
from rhodecode.model.user import UserModel
from rhodecode.model.user_group import UserGroupModel


log = logging.getLogger(__name__)

# auth types that authenticate() function can receive
VCS_TYPE = 'vcs'
HTTP_TYPE = 'http'


class LazyFormencode(object):
    def __init__(self, formencode_obj, *args, **kwargs):
        self.formencode_obj = formencode_obj
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        from inspect import isfunction
        formencode_obj = self.formencode_obj
        if isfunction(formencode_obj):
            # case we wrap validators into functions
            formencode_obj = self.formencode_obj(*args, **kwargs)
        return formencode_obj(*self.args, **self.kwargs)


class RhodeCodeAuthPluginBase(object):
    # cache the authentication request for N amount of seconds. Some kind
    # of authentication methods are very heavy and it's very efficient to cache
    # the result of a call. If it's set to None (default) cache is off
    AUTH_CACHE_TTL = None
    AUTH_CACHE = {}

    auth_func_attrs = {
        "username": "unique username",
        "firstname": "first name",
        "lastname": "last name",
        "email": "email address",
        "groups": '["list", "of", "groups"]',
        "extern_name": "name in external source of record",
        "extern_type": "type of external source of record",
        "admin": 'True|False defines if user should be RhodeCode super admin',
        "active":
            'True|False defines active state of user internally for RhodeCode',
        "active_from_extern":
            "True|False\None, active state from the external auth, "
            "None means use definition from RhodeCode extern_type active value"
    }
    # set on authenticate() method and via set_auth_type func.
    auth_type = None

    # List of setting names to store encrypted. Plugins may override this list
    # to store settings encrypted.
    _settings_encrypted = []

    # Mapping of python to DB settings model types. Plugins may override or
    # extend this mapping.
    _settings_type_map = {
        str: 'str',
        int: 'int',
        unicode: 'unicode',
        bool: 'bool',
        list: 'list',
    }

    def __init__(self, plugin_id):
        self._plugin_id = plugin_id

    def _get_setting_full_name(self, name):
        """
        Return the full setting name used for storing values in the database.
        """
        # TODO: johbo: Using the name here is problematic. It would be good to
        # introduce either new models in the database to hold Plugin and
        # PluginSetting or to use the plugin id here.
        return 'auth_{}_{}'.format(self.name, name)

    def _get_setting_type(self, name, value):
        """
        Get the type as used by the SettingsModel accordingly to type of passed
        value. Optionally the suffix `.encrypted` is appended to instruct
        SettingsModel to store it encrypted.
        """
        type_ = self._settings_type_map.get(type(value), 'unicode')
        if name in self._settings_encrypted:
            type_ = '{}.encrypted'.format(type_)
        return type_

    def is_enabled(self):
        """
        Returns true if this plugin is enabled. An enabled plugin can be
        configured in the admin interface but it is not consulted during
        authentication.
        """
        auth_plugins = SettingsModel().get_auth_plugins()
        return self.get_id() in auth_plugins

    def is_active(self):
        """
        Returns true if the plugin is activated. An activated plugin is
        consulted during authentication, assumed it is also enabled.
        """
        return self.get_setting_by_name('enabled')

    def get_id(self):
        """
        Returns the plugin id.
        """
        return self._plugin_id

    def get_display_name(self):
        """
        Returns a translation string for displaying purposes.
        """
        raise NotImplementedError('Not implemented in base class')

    def get_settings_schema(self):
        """
        Returns a colander schema, representing the plugin settings.
        """
        return AuthnPluginSettingsSchemaBase()

    def get_setting_by_name(self, name):
        """
        Returns a plugin setting by name.
        """
        full_name = self._get_setting_full_name(name)
        db_setting = SettingsModel().get_setting_by_name(full_name)
        return db_setting.app_settings_value if db_setting else None

    def create_or_update_setting(self, name, value):
        """
        Create or update a setting for this plugin in the persistent storage.
        """
        full_name = self._get_setting_full_name(name)
        type_ = self._get_setting_type(name, value)
        db_setting = SettingsModel().create_or_update_setting(
            full_name, value, type_)
        return db_setting.app_settings_value

    def get_settings(self):
        """
        Returns the plugin settings as dictionary.
        """
        settings = {}
        for node in self.get_settings_schema():
            settings[node.name] = self.get_setting_by_name(node.name)
        return settings

    @property
    def validators(self):
        """
        Exposes RhodeCode validators modules
        """
        # this is a hack to overcome issues with pylons threadlocals and
        # translator object _() not beein registered properly.
        class LazyCaller(object):
            def __init__(self, name):
                self.validator_name = name

            def __call__(self, *args, **kwargs):
                from rhodecode.model import validators as v
                obj = getattr(v, self.validator_name)
                # log.debug('Initializing lazy formencode object: %s', obj)
                return LazyFormencode(obj, *args, **kwargs)

        class ProxyGet(object):
            def __getattribute__(self, name):
                return LazyCaller(name)

        return ProxyGet()

    @hybrid_property
    def name(self):
        """
        Returns the name of this authentication plugin.

        :returns: string
        """
        raise NotImplementedError("Not implemented in base class")

    @hybrid_property
    def is_container_auth(self):
        """
        Returns bool if this module uses container auth.

        This property will trigger an automatic call to authenticate on
        a visit to the website or during a push/pull.

        :returns: bool
        """
        return False

    @hybrid_property
    def allows_creating_users(self):
        """
        Defines if Plugin allows users to be created on-the-fly when
        authentication is called. Controls how external plugins should behave
        in terms if they are allowed to create new users, or not. Base plugins
        should not be allowed to, but External ones should be !

        :return: bool
        """
        return False

    def set_auth_type(self, auth_type):
        self.auth_type = auth_type

    def allows_authentication_from(
            self, user, allows_non_existing_user=True,
            allowed_auth_plugins=None, allowed_auth_sources=None):
        """
        Checks if this authentication module should accept a request for
        the current user.

        :param user: user object fetched using plugin's get_user() method.
        :param allows_non_existing_user: if True, don't allow the
            user to be empty, meaning not existing in our database
        :param allowed_auth_plugins: if provided, users extern_type will be
            checked against a list of provided extern types, which are plugin
            auth_names in the end
        :param allowed_auth_sources: authentication type allowed,
            `http` or `vcs` default is both.
            defines if plugin will accept only http authentication vcs
            authentication(git/hg) or both
        :returns: boolean
        """
        if not user and not allows_non_existing_user:
            log.debug('User is empty but plugin does not allow empty users,'
                      'not allowed to authenticate')
            return False

        expected_auth_plugins = allowed_auth_plugins or [self.name]
        if user and (user.extern_type and
                     user.extern_type not in expected_auth_plugins):
            log.debug(
                'User `%s` is bound to `%s` auth type. Plugin allows only '
                '%s, skipping', user, user.extern_type, expected_auth_plugins)

            return False

        # by default accept both
        expected_auth_from = allowed_auth_sources or [HTTP_TYPE, VCS_TYPE]
        if self.auth_type not in expected_auth_from:
            log.debug('Current auth source is %s but plugin only allows %s',
                      self.auth_type, expected_auth_from)
            return False

        return True

    def get_user(self, username=None, **kwargs):
        """
        Helper method for user fetching in plugins, by default it's using
        simple fetch by username, but this method can be custimized in plugins
        eg. container auth plugin to fetch user by environ params

        :param username: username if given to fetch from database
        :param kwargs: extra arguments needed for user fetching.
        """
        user = None
        log.debug(
            'Trying to fetch user `%s` from RhodeCode database', username)
        if username:
            user = User.get_by_username(username)
            if not user:
                log.debug('User not found, fallback to fetch user in '
                          'case insensitive mode')
                user = User.get_by_username(username, case_insensitive=True)
        else:
            log.debug('provided username:`%s` is empty skipping...', username)
        if not user:
            log.debug('User `%s` not found in database', username)
        return user

    def user_activation_state(self):
        """
        Defines user activation state when creating new users

        :returns: boolean
        """
        raise NotImplementedError("Not implemented in base class")

    def auth(self, userobj, username, passwd, settings, **kwargs):
        """
        Given a user object (which may be null), username, a plaintext
        password, and a settings object (containing all the keys needed as
        listed in settings()), authenticate this user's login attempt.

        Return None on failure. On success, return a dictionary of the form:

            see: RhodeCodeAuthPluginBase.auth_func_attrs
        This is later validated for correctness
        """
        raise NotImplementedError("not implemented in base class")

    def _authenticate(self, userobj, username, passwd, settings, **kwargs):
        """
        Wrapper to call self.auth() that validates call on it

        :param userobj: userobj
        :param username: username
        :param passwd: plaintext password
        :param settings: plugin settings
        """
        auth = self.auth(userobj, username, passwd, settings, **kwargs)
        if auth:
            # check if hash should be migrated ?
            new_hash = auth.get('_hash_migrate')
            if new_hash:
                self._migrate_hash_to_bcrypt(username, passwd, new_hash)
            return self._validate_auth_return(auth)
        return auth

    def _migrate_hash_to_bcrypt(self, username, password, new_hash):
        new_hash_cypher = _RhodeCodeCryptoBCrypt()
        # extra checks, so make sure new hash is correct.
        password_encoded = safe_str(password)
        if new_hash and new_hash_cypher.hash_check(
                password_encoded, new_hash):
            cur_user = User.get_by_username(username)
            cur_user.password = new_hash
            Session().add(cur_user)
            Session().flush()
            log.info('Migrated user %s hash to bcrypt', cur_user)

    def _validate_auth_return(self, ret):
        if not isinstance(ret, dict):
            raise Exception('returned value from auth must be a dict')
        for k in self.auth_func_attrs:
            if k not in ret:
                raise Exception('Missing %s attribute from returned data' % k)
        return ret


class RhodeCodeExternalAuthPlugin(RhodeCodeAuthPluginBase):

    @hybrid_property
    def allows_creating_users(self):
        return True

    def use_fake_password(self):
        """
        Return a boolean that indicates whether or not we should set the user's
        password to a random value when it is authenticated by this plugin.
        If your plugin provides authentication, then you will generally
        want this.

        :returns: boolean
        """
        raise NotImplementedError("Not implemented in base class")

    def _authenticate(self, userobj, username, passwd, settings, **kwargs):
        # at this point _authenticate calls plugin's `auth()` function
        auth = super(RhodeCodeExternalAuthPlugin, self)._authenticate(
            userobj, username, passwd, settings, **kwargs)
        if auth:
            # maybe plugin will clean the username ?
            # we should use the return value
            username = auth['username']

            # if external source tells us that user is not active, we should
            # skip rest of the process. This can prevent from creating users in
            # RhodeCode when using external authentication, but if it's
            # inactive user we shouldn't create that user anyway
            if auth['active_from_extern'] is False:
                log.warning(
                    "User %s authenticated against %s, but is inactive",
                    username, self.__module__)
                return None

            cur_user = User.get_by_username(username, case_insensitive=True)
            is_user_existing = cur_user is not None

            if is_user_existing:
                log.debug('Syncing user `%s` from '
                          '`%s` plugin', username, self.name)
            else:
                log.debug('Creating non existing user `%s` from '
                          '`%s` plugin', username, self.name)

            if self.allows_creating_users:
                log.debug('Plugin `%s` allows to '
                          'create new users', self.name)
            else:
                log.debug('Plugin `%s` does not allow to '
                          'create new users', self.name)

            user_parameters = {
                'username': username,
                'email': auth["email"],
                'firstname': auth["firstname"],
                'lastname': auth["lastname"],
                'active': auth["active"],
                'admin': auth["admin"],
                'extern_name': auth["extern_name"],
                'extern_type': self.name,
                'plugin': self,
                'allow_to_create_user': self.allows_creating_users,
            }

            if not is_user_existing:
                if self.use_fake_password():
                    # Randomize the PW because we don't need it, but don't want
                    # them blank either
                    passwd = PasswordGenerator().gen_password(length=16)
                user_parameters['password'] = passwd
            else:
                # Since the password is required by create_or_update method of
                # UserModel, we need to set it explicitly.
                # The create_or_update method is smart and recognises the
                # password hashes as well.
                user_parameters['password'] = cur_user.password

            # we either create or update users, we also pass the flag
            # that controls if this method can actually do that.
            # raises NotAllowedToCreateUserError if it cannot, and we try to.
            user = UserModel().create_or_update(**user_parameters)
            Session().flush()
            # enforce user is just in given groups, all of them has to be ones
            # created from plugins. We store this info in _group_data JSON
            # field
            try:
                groups = auth['groups'] or []
                UserGroupModel().enforce_groups(user, groups, self.name)
            except Exception:
                # for any reason group syncing fails, we should
                # proceed with login
                log.error(traceback.format_exc())
            Session().commit()
        return auth


def loadplugin(plugin_id):
    """
    Loads and returns an instantiated authentication plugin.
    Returns the RhodeCodeAuthPluginBase subclass on success,
    or None on failure.
    """
    # TODO: Disusing pyramids thread locals to retrieve the registry.
    authn_registry = get_current_registry().getUtility(IAuthnPluginRegistry)
    plugin = authn_registry.get_plugin(plugin_id)
    if plugin is None:
        log.error('Authentication plugin not found: "%s"', plugin_id)
    return plugin


def get_auth_cache_manager(custom_ttl=None):
    return caches.get_cache_manager(
        'auth_plugins', 'rhodecode.authentication', custom_ttl)


def authenticate(username, password, environ=None, auth_type=None,
                 skip_missing=False):
    """
    Authentication function used for access control,
    It tries to authenticate based on enabled authentication modules.

    :param username: username can be empty for container auth
    :param password: password can be empty for container auth
    :param environ: environ headers passed for container auth
    :param auth_type: type of authentication, either `HTTP_TYPE` or `VCS_TYPE`
    :param skip_missing: ignores plugins that are in db but not in environment
    :returns: None if auth failed, plugin_user dict if auth is correct
    """
    if not auth_type or auth_type not in [HTTP_TYPE, VCS_TYPE]:
        raise ValueError('auth type must be on of http, vcs got "%s" instead'
                         % auth_type)
    container_only = environ and not (username and password)

    authn_registry = get_current_registry().getUtility(IAuthnPluginRegistry)
    for plugin in authn_registry.get_plugins_for_authentication():
        plugin.set_auth_type(auth_type)
        user = plugin.get_user(username)
        display_user = user.username if user else username

        if container_only and not plugin.is_container_auth:
            log.debug('Auth type is for container only and plugin `%s` is not '
                      'container plugin, skipping...', plugin.get_id())
            continue

        # load plugin settings from RhodeCode database
        plugin_settings = plugin.get_settings()
        log.debug('Plugin settings:%s', plugin_settings)

        log.debug('Trying authentication using ** %s **', plugin.get_id())
        # use plugin's method of user extraction.
        user = plugin.get_user(username, environ=environ,
                               settings=plugin_settings)
        display_user = user.username if user else username
        log.debug(
            'Plugin %s extracted user is `%s`', plugin.get_id(), display_user)

        if not plugin.allows_authentication_from(user):
            log.debug('Plugin %s does not accept user `%s` for authentication',
                      plugin.get_id(), display_user)
            continue
        else:
            log.debug('Plugin %s accepted user `%s` for authentication',
                      plugin.get_id(), display_user)

        log.info('Authenticating user `%s` using %s plugin',
                 display_user, plugin.get_id())

        _cache_ttl = 0

        if isinstance(plugin.AUTH_CACHE_TTL, (int, long)):
            # plugin cache set inside is more important than the settings value
            _cache_ttl = plugin.AUTH_CACHE_TTL
        elif plugin_settings.get('auth_cache_ttl'):
            _cache_ttl = safe_int(plugin_settings.get('auth_cache_ttl'), 0)

        plugin_cache_active = bool(_cache_ttl and _cache_ttl > 0)

        # get instance of cache manager configured for a namespace
        cache_manager = get_auth_cache_manager(custom_ttl=_cache_ttl)

        log.debug('Cache for plugin `%s` active: %s', plugin.get_id(),
                  plugin_cache_active)

        # for environ based password can be empty, but then the validation is
        # on the server that fills in the env data needed for authentication
        _password_hash = md5_safe(plugin.name + username + (password or ''))

        # _authenticate is a wrapper for .auth() method of plugin.
        # it checks if .auth() sends proper data.
        # For RhodeCodeExternalAuthPlugin it also maps users to
        # Database and maps the attributes returned from .auth()
        # to RhodeCode database. If this function returns data
        # then auth is correct.
        start = time.time()
        log.debug('Running plugin `%s` _authenticate method',
                  plugin.get_id())

        def auth_func():
            """
            This function is used internally in Cache of Beaker to calculate
            Results
            """
            return plugin._authenticate(
                user, username, password, plugin_settings,
                environ=environ or {})

        if plugin_cache_active:
            plugin_user = cache_manager.get(
                _password_hash, createfunc=auth_func)
        else:
            plugin_user = auth_func()

        auth_time = time.time() - start
        log.debug('Authentication for plugin `%s` completed in %.3fs, '
                  'expiration time of fetched cache %.1fs.',
                  plugin.get_id(), auth_time, _cache_ttl)

        log.debug('PLUGIN USER DATA: %s', plugin_user)

        if plugin_user:
            log.debug('Plugin returned proper authentication data')
            return plugin_user
        # we failed to Auth because .auth() method didn't return proper user
        log.debug("User `%s` failed to authenticate against %s",
                  display_user, plugin.get_id())
    return None
