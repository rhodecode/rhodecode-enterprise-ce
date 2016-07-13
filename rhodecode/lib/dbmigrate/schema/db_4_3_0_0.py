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
Database Models for RhodeCode Enterprise
"""

import os
import sys
import time
import hashlib
import logging
import datetime
import warnings
import ipaddress
import functools
import traceback
import collections


from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    relationship, joinedload, class_mapper, validates, aliased)
from sqlalchemy.sql.expression import true
from beaker.cache import cache_region, region_invalidate
from webob.exc import HTTPNotFound
from zope.cachedescriptors.property import Lazy as LazyProperty

from pylons import url
from pylons.i18n.translation import lazy_ugettext as _

from rhodecode.lib.vcs import get_backend
from rhodecode.lib.vcs.utils.helpers import get_scm
from rhodecode.lib.vcs.exceptions import VCSError
from rhodecode.lib.vcs.backends.base import (
    EmptyCommit, Reference, MergeFailureReason)
from rhodecode.lib.utils2 import (
    str2bool, safe_str, get_commit_safe, safe_unicode, remove_prefix, md5_safe,
    time_to_datetime, aslist, Optional, safe_int, get_clone_url, AttributeDict)
from rhodecode.lib.ext_json import json
from rhodecode.lib.caching_query import FromCache
from rhodecode.lib.encrypt import AESCipher

from rhodecode.model.meta import Base, Session

URL_SEP = '/'
log = logging.getLogger(__name__)

# =============================================================================
# BASE CLASSES
# =============================================================================

# this is propagated from .ini file rhodecode.encrypted_values.secret or
# beaker.session.secret if first is not set.
# and initialized at environment.py
ENCRYPTION_KEY = None

# used to sort permissions by types, '#' used here is not allowed to be in
# usernames, and it's very early in sorted string.printable table.
PERMISSION_TYPE_SORT = {
    'admin': '####',
    'write': '###',
    'read':  '##',
    'none':  '#',
}


def display_sort(obj):
    """
    Sort function used to sort permissions in .permissions() function of
    Repository, RepoGroup, UserGroup. Also it put the default user in front
    of all other resources
    """

    if obj.username == User.DEFAULT_USER:
        return '#####'
    prefix = PERMISSION_TYPE_SORT.get(obj.permission.split('.')[-1], '')
    return prefix + obj.username


def _hash_key(k):
    return md5_safe(k)


class EncryptedTextValue(TypeDecorator):
    """
    Special column for encrypted long text data, use like::

        value = Column("encrypted_value", EncryptedValue(), nullable=False)

    This column is intelligent so if value is in unencrypted form it return
    unencrypted form, but on save it always encrypts
    """
    impl = Text

    def process_bind_param(self, value, dialect):
        if not value:
            return value
        if value.startswith('enc$aes$') or value.startswith('enc$aes_hmac$'):
            # protect against double encrypting if someone manually starts
            # doing
            raise ValueError('value needs to be in unencrypted format, ie. '
                             'not starting with enc$aes')
        return 'enc$aes_hmac$%s' % AESCipher(
            ENCRYPTION_KEY, hmac=True).encrypt(value)

    def process_result_value(self, value, dialect):
        import rhodecode

        if not value:
            return value

        parts = value.split('$', 3)
        if not len(parts) == 3:
            # probably not encrypted values
            return value
        else:
            if parts[0] != 'enc':
                # parts ok but without our header ?
                return value
            enc_strict_mode = str2bool(rhodecode.CONFIG.get(
                'rhodecode.encrypted_values.strict') or True)
            # at that stage we know it's our encryption
            if parts[1] == 'aes':
                decrypted_data = AESCipher(ENCRYPTION_KEY).decrypt(parts[2])
            elif parts[1] == 'aes_hmac':
                decrypted_data = AESCipher(
                    ENCRYPTION_KEY, hmac=True,
                    strict_verification=enc_strict_mode).decrypt(parts[2])
            else:
                raise ValueError(
                    'Encryption type part is wrong, must be `aes` '
                    'or `aes_hmac`, got `%s` instead' % (parts[1]))
            return decrypted_data


class BaseModel(object):
    """
    Base Model for all classes
    """

    @classmethod
    def _get_keys(cls):
        """return column names for this model """
        return class_mapper(cls).c.keys()

    def get_dict(self):
        """
        return dict with keys and values corresponding
        to this model data """

        d = {}
        for k in self._get_keys():
            d[k] = getattr(self, k)

        # also use __json__() if present to get additional fields
        _json_attr = getattr(self, '__json__', None)
        if _json_attr:
            # update with attributes from __json__
            if callable(_json_attr):
                _json_attr = _json_attr()
            for k, val in _json_attr.iteritems():
                d[k] = val
        return d

    def get_appstruct(self):
        """return list with keys and values tuples corresponding
        to this model data """

        l = []
        for k in self._get_keys():
            l.append((k, getattr(self, k),))
        return l

    def populate_obj(self, populate_dict):
        """populate model with data from given populate_dict"""

        for k in self._get_keys():
            if k in populate_dict:
                setattr(self, k, populate_dict[k])

    @classmethod
    def query(cls):
        return Session().query(cls)

    @classmethod
    def get(cls, id_):
        if id_:
            return cls.query().get(id_)

    @classmethod
    def get_or_404(cls, id_):
        try:
            id_ = int(id_)
        except (TypeError, ValueError):
            raise HTTPNotFound

        res = cls.query().get(id_)
        if not res:
            raise HTTPNotFound
        return res

    @classmethod
    def getAll(cls):
        # deprecated and left for backward compatibility
        return cls.get_all()

    @classmethod
    def get_all(cls):
        return cls.query().all()

    @classmethod
    def delete(cls, id_):
        obj = cls.query().get(id_)
        Session().delete(obj)

    @classmethod
    def identity_cache(cls, session, attr_name, value):
        exist_in_session = []
        for (item_cls, pkey), instance in session.identity_map.items():
            if cls == item_cls and getattr(instance, attr_name) == value:
                exist_in_session.append(instance)
        if exist_in_session:
            if len(exist_in_session) == 1:
                return exist_in_session[0]
            log.exception(
                'multiple objects with attr %s and '
                'value %s found with same name: %r',
                attr_name, value, exist_in_session)

    def __repr__(self):
        if hasattr(self, '__unicode__'):
            # python repr needs to return str
            try:
                return safe_str(self.__unicode__())
            except UnicodeDecodeError:
                pass
        return '<DB:%s>' % (self.__class__.__name__)


class RhodeCodeSetting(Base, BaseModel):
    __tablename__ = 'rhodecode_settings'
    __table_args__ = (
        UniqueConstraint('app_settings_name'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    SETTINGS_TYPES = {
        'str': safe_str,
        'int': safe_int,
        'unicode': safe_unicode,
        'bool': str2bool,
        'list': functools.partial(aslist, sep=',')
    }
    DEFAULT_UPDATE_URL = 'https://rhodecode.com/api/v1/info/versions'
    GLOBAL_CONF_KEY = 'app_settings'

    app_settings_id = Column("app_settings_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    app_settings_name = Column("app_settings_name", String(255), nullable=True, unique=None, default=None)
    _app_settings_value = Column("app_settings_value", String(4096), nullable=True, unique=None, default=None)
    _app_settings_type = Column("app_settings_type", String(255), nullable=True, unique=None, default=None)

    def __init__(self, key='', val='', type='unicode'):
        self.app_settings_name = key
        self.app_settings_type = type
        self.app_settings_value = val

    @validates('_app_settings_value')
    def validate_settings_value(self, key, val):
        assert type(val) == unicode
        return val

    @hybrid_property
    def app_settings_value(self):
        v = self._app_settings_value
        _type = self.app_settings_type
        if _type:
            _type = self.app_settings_type.split('.')[0]
            # decode the encrypted value
            if 'encrypted' in self.app_settings_type:
                cipher = EncryptedTextValue()
                v = safe_unicode(cipher.process_result_value(v, None))

        converter = self.SETTINGS_TYPES.get(_type) or \
            self.SETTINGS_TYPES['unicode']
        return converter(v)

    @app_settings_value.setter
    def app_settings_value(self, val):
        """
        Setter that will always make sure we use unicode in app_settings_value

        :param val:
        """
        val = safe_unicode(val)
        # encode the encrypted value
        if 'encrypted' in self.app_settings_type:
            cipher = EncryptedTextValue()
            val = safe_unicode(cipher.process_bind_param(val, None))
        self._app_settings_value = val

    @hybrid_property
    def app_settings_type(self):
        return self._app_settings_type

    @app_settings_type.setter
    def app_settings_type(self, val):
        if val.split('.')[0] not in self.SETTINGS_TYPES:
            raise Exception('type must be one of %s got %s'
                            % (self.SETTINGS_TYPES.keys(), val))
        self._app_settings_type = val

    def __unicode__(self):
        return u"<%s('%s:%s[%s]')>" % (
            self.__class__.__name__,
            self.app_settings_name, self.app_settings_value,
            self.app_settings_type
        )


class RhodeCodeUi(Base, BaseModel):
    __tablename__ = 'rhodecode_ui'
    __table_args__ = (
        UniqueConstraint('ui_key'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    HOOK_REPO_SIZE = 'changegroup.repo_size'
    # HG
    HOOK_PRE_PULL = 'preoutgoing.pre_pull'
    HOOK_PULL = 'outgoing.pull_logger'
    HOOK_PRE_PUSH = 'prechangegroup.pre_push'
    HOOK_PUSH = 'changegroup.push_logger'

    # TODO: johbo: Unify way how hooks are configured for git and hg,
    # git part is currently hardcoded.

    # SVN PATTERNS
    SVN_BRANCH_ID = 'vcs_svn_branch'
    SVN_TAG_ID = 'vcs_svn_tag'

    ui_id = Column(
        "ui_id", Integer(), nullable=False, unique=True, default=None,
        primary_key=True)
    ui_section = Column(
        "ui_section", String(255), nullable=True, unique=None, default=None)
    ui_key = Column(
        "ui_key", String(255), nullable=True, unique=None, default=None)
    ui_value = Column(
        "ui_value", String(255), nullable=True, unique=None, default=None)
    ui_active = Column(
        "ui_active", Boolean(), nullable=True, unique=None, default=True)

    def __repr__(self):
        return '<%s[%s]%s=>%s]>' % (self.__class__.__name__, self.ui_section,
                                    self.ui_key, self.ui_value)


class RepoRhodeCodeSetting(Base, BaseModel):
    __tablename__ = 'repo_rhodecode_settings'
    __table_args__ = (
        UniqueConstraint(
            'app_settings_name', 'repository_id',
            name='uq_repo_rhodecode_setting_name_repo_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    repository_id = Column(
        "repository_id", Integer(), ForeignKey('repositories.repo_id'),
        nullable=False)
    app_settings_id = Column(
        "app_settings_id", Integer(), nullable=False, unique=True,
        default=None, primary_key=True)
    app_settings_name = Column(
        "app_settings_name", String(255), nullable=True, unique=None,
        default=None)
    _app_settings_value = Column(
        "app_settings_value", String(4096), nullable=True, unique=None,
        default=None)
    _app_settings_type = Column(
        "app_settings_type", String(255), nullable=True, unique=None,
        default=None)

    repository = relationship('Repository')

    def __init__(self, repository_id, key='', val='', type='unicode'):
        self.repository_id = repository_id
        self.app_settings_name = key
        self.app_settings_type = type
        self.app_settings_value = val

    @validates('_app_settings_value')
    def validate_settings_value(self, key, val):
        assert type(val) == unicode
        return val

    @hybrid_property
    def app_settings_value(self):
        v = self._app_settings_value
        type_ = self.app_settings_type
        SETTINGS_TYPES = RhodeCodeSetting.SETTINGS_TYPES
        converter = SETTINGS_TYPES.get(type_) or SETTINGS_TYPES['unicode']
        return converter(v)

    @app_settings_value.setter
    def app_settings_value(self, val):
        """
        Setter that will always make sure we use unicode in app_settings_value

        :param val:
        """
        self._app_settings_value = safe_unicode(val)

    @hybrid_property
    def app_settings_type(self):
        return self._app_settings_type

    @app_settings_type.setter
    def app_settings_type(self, val):
        SETTINGS_TYPES = RhodeCodeSetting.SETTINGS_TYPES
        if val not in SETTINGS_TYPES:
            raise Exception('type must be one of %s got %s'
                            % (SETTINGS_TYPES.keys(), val))
        self._app_settings_type = val

    def __unicode__(self):
        return u"<%s('%s:%s:%s[%s]')>" % (
            self.__class__.__name__, self.repository.repo_name,
            self.app_settings_name, self.app_settings_value,
            self.app_settings_type
        )


class RepoRhodeCodeUi(Base, BaseModel):
    __tablename__ = 'repo_rhodecode_ui'
    __table_args__ = (
        UniqueConstraint(
            'repository_id', 'ui_section', 'ui_key',
            name='uq_repo_rhodecode_ui_repository_id_section_key'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    repository_id = Column(
        "repository_id", Integer(), ForeignKey('repositories.repo_id'),
        nullable=False)
    ui_id = Column(
        "ui_id", Integer(), nullable=False, unique=True, default=None,
        primary_key=True)
    ui_section = Column(
        "ui_section", String(255), nullable=True, unique=None, default=None)
    ui_key = Column(
        "ui_key", String(255), nullable=True, unique=None, default=None)
    ui_value = Column(
        "ui_value", String(255), nullable=True, unique=None, default=None)
    ui_active = Column(
        "ui_active", Boolean(), nullable=True, unique=None, default=True)

    repository = relationship('Repository')

    def __repr__(self):
        return '<%s[%s:%s]%s=>%s]>' % (
            self.__class__.__name__, self.repository.repo_name,
            self.ui_section, self.ui_key, self.ui_value)


class User(Base, BaseModel):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('username'), UniqueConstraint('email'),
        Index('u_username_idx', 'username'),
        Index('u_email_idx', 'email'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    DEFAULT_USER = 'default'
    DEFAULT_USER_EMAIL = 'anonymous@rhodecode.org'
    DEFAULT_GRAVATAR_URL = 'https://secure.gravatar.com/avatar/{md5email}?d=identicon&s={size}'

    user_id = Column("user_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    username = Column("username", String(255), nullable=True, unique=None, default=None)
    password = Column("password", String(255), nullable=True, unique=None, default=None)
    active = Column("active", Boolean(), nullable=True, unique=None, default=True)
    admin = Column("admin", Boolean(), nullable=True, unique=None, default=False)
    name = Column("firstname", String(255), nullable=True, unique=None, default=None)
    lastname = Column("lastname", String(255), nullable=True, unique=None, default=None)
    _email = Column("email", String(255), nullable=True, unique=None, default=None)
    last_login = Column("last_login", DateTime(timezone=False), nullable=True, unique=None, default=None)
    extern_type = Column("extern_type", String(255), nullable=True, unique=None, default=None)
    extern_name = Column("extern_name", String(255), nullable=True, unique=None, default=None)
    api_key = Column("api_key", String(255), nullable=True, unique=None, default=None)
    inherit_default_permissions = Column("inherit_default_permissions", Boolean(), nullable=False, unique=None, default=True)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    _user_data = Column("user_data", LargeBinary(), nullable=True)  # JSON data

    user_log = relationship('UserLog')
    user_perms = relationship('UserToPerm', primaryjoin="User.user_id==UserToPerm.user_id", cascade='all')

    repositories = relationship('Repository')
    repository_groups = relationship('RepoGroup')
    user_groups = relationship('UserGroup')

    user_followers = relationship('UserFollowing', primaryjoin='UserFollowing.follows_user_id==User.user_id', cascade='all')
    followings = relationship('UserFollowing', primaryjoin='UserFollowing.user_id==User.user_id', cascade='all')

    repo_to_perm = relationship('UserRepoToPerm', primaryjoin='UserRepoToPerm.user_id==User.user_id', cascade='all')
    repo_group_to_perm = relationship('UserRepoGroupToPerm', primaryjoin='UserRepoGroupToPerm.user_id==User.user_id', cascade='all')
    user_group_to_perm = relationship('UserUserGroupToPerm', primaryjoin='UserUserGroupToPerm.user_id==User.user_id', cascade='all')

    group_member = relationship('UserGroupMember', cascade='all')

    notifications = relationship('UserNotification', cascade='all')
    # notifications assigned to this user
    user_created_notifications = relationship('Notification', cascade='all')
    # comments created by this user
    user_comments = relationship('ChangesetComment', cascade='all')
    # user profile extra info
    user_emails = relationship('UserEmailMap', cascade='all')
    user_ip_map = relationship('UserIpMap', cascade='all')
    user_auth_tokens = relationship('UserApiKeys', cascade='all')
    # gists
    user_gists = relationship('Gist', cascade='all')
    # user pull requests
    user_pull_requests = relationship('PullRequest', cascade='all')
    # external identities
    extenal_identities = relationship(
        'ExternalIdentity',
        primaryjoin="User.user_id==ExternalIdentity.local_user_id",
        cascade='all')

    def __unicode__(self):
        return u"<%s('id:%s:%s')>" % (self.__class__.__name__,
                                      self.user_id, self.username)

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, val):
        self._email = val.lower() if val else None

    @property
    def firstname(self):
        # alias for future
        return self.name

    @property
    def emails(self):
        other = UserEmailMap.query().filter(UserEmailMap.user==self).all()
        return [self.email] + [x.email for x in other]

    @property
    def auth_tokens(self):
        return [self.api_key] + [x.api_key for x in self.extra_auth_tokens]

    @property
    def extra_auth_tokens(self):
        return UserApiKeys.query().filter(UserApiKeys.user == self).all()

    @property
    def feed_token(self):
        feed_tokens = UserApiKeys.query()\
            .filter(UserApiKeys.user == self)\
            .filter(UserApiKeys.role == UserApiKeys.ROLE_FEED)\
            .all()
        if feed_tokens:
            return feed_tokens[0].api_key
        else:
            # use the main token so we don't end up with nothing...
            return self.api_key

    @classmethod
    def extra_valid_auth_tokens(cls, user, role=None):
        tokens = UserApiKeys.query().filter(UserApiKeys.user == user)\
                .filter(or_(UserApiKeys.expires == -1,
                            UserApiKeys.expires >= time.time()))
        if role:
            tokens = tokens.filter(or_(UserApiKeys.role == role,
                                       UserApiKeys.role == UserApiKeys.ROLE_ALL))
        return tokens.all()

    @property
    def ip_addresses(self):
        ret = UserIpMap.query().filter(UserIpMap.user == self).all()
        return [x.ip_addr for x in ret]

    @property
    def username_and_name(self):
        return '%s (%s %s)' % (self.username, self.firstname, self.lastname)

    @property
    def username_or_name_or_email(self):
        full_name = self.full_name if self.full_name is not ' ' else None
        return self.username or full_name or self.email

    @property
    def full_name(self):
        return '%s %s' % (self.firstname, self.lastname)

    @property
    def full_name_or_username(self):
        return ('%s %s' % (self.firstname, self.lastname)
                if (self.firstname and self.lastname) else self.username)

    @property
    def full_contact(self):
        return '%s %s <%s>' % (self.firstname, self.lastname, self.email)

    @property
    def short_contact(self):
        return '%s %s' % (self.firstname, self.lastname)

    @property
    def is_admin(self):
        return self.admin

    @property
    def AuthUser(self):
        """
        Returns instance of AuthUser for this user
        """
        from rhodecode.lib.auth import AuthUser
        return AuthUser(user_id=self.user_id, api_key=self.api_key,
                        username=self.username)

    @hybrid_property
    def user_data(self):
        if not self._user_data:
            return {}

        try:
            return json.loads(self._user_data)
        except TypeError:
            return {}

    @user_data.setter
    def user_data(self, val):
        if not isinstance(val, dict):
            raise Exception('user_data must be dict, got %s' % type(val))
        try:
            self._user_data = json.dumps(val)
        except Exception:
            log.error(traceback.format_exc())

    @classmethod
    def get_by_username(cls, username, case_insensitive=False,
                        cache=False, identity_cache=False):
        session = Session()

        if case_insensitive:
            q = cls.query().filter(
                func.lower(cls.username) == func.lower(username))
        else:
            q = cls.query().filter(cls.username == username)

        if cache:
            if identity_cache:
                val = cls.identity_cache(session, 'username', username)
                if val:
                    return val
            else:
                q = q.options(
                    FromCache("sql_cache_short",
                              "get_user_by_name_%s" % _hash_key(username)))

        return q.scalar()

    @classmethod
    def get_by_auth_token(cls, auth_token, cache=False, fallback=True):
        q = cls.query().filter(cls.api_key == auth_token)

        if cache:
            q = q.options(FromCache("sql_cache_short",
                                    "get_auth_token_%s" % auth_token))
        res = q.scalar()

        if fallback and not res:
            #fallback to additional keys
            _res = UserApiKeys.query()\
                .filter(UserApiKeys.api_key == auth_token)\
                .filter(or_(UserApiKeys.expires == -1,
                            UserApiKeys.expires >= time.time()))\
                .first()
            if _res:
                res = _res.user
        return res

    @classmethod
    def get_by_email(cls, email, case_insensitive=False, cache=False):

        if case_insensitive:
            q = cls.query().filter(func.lower(cls.email) == func.lower(email))

        else:
            q = cls.query().filter(cls.email == email)

        if cache:
            q = q.options(FromCache("sql_cache_short",
                                    "get_email_key_%s" % email))

        ret = q.scalar()
        if ret is None:
            q = UserEmailMap.query()
            # try fetching in alternate email map
            if case_insensitive:
                q = q.filter(func.lower(UserEmailMap.email) == func.lower(email))
            else:
                q = q.filter(UserEmailMap.email == email)
            q = q.options(joinedload(UserEmailMap.user))
            if cache:
                q = q.options(FromCache("sql_cache_short",
                                        "get_email_map_key_%s" % email))
            ret = getattr(q.scalar(), 'user', None)

        return ret

    @classmethod
    def get_from_cs_author(cls, author):
        """
        Tries to get User objects out of commit author string

        :param author:
        """
        from rhodecode.lib.helpers import email, author_name
        # Valid email in the attribute passed, see if they're in the system
        _email = email(author)
        if _email:
            user = cls.get_by_email(_email, case_insensitive=True)
            if user:
                return user
        # Maybe we can match by username?
        _author = author_name(author)
        user = cls.get_by_username(_author, case_insensitive=True)
        if user:
            return user

    def update_userdata(self, **kwargs):
        usr = self
        old = usr.user_data
        old.update(**kwargs)
        usr.user_data = old
        Session().add(usr)
        log.debug('updated userdata with ', kwargs)

    def update_lastlogin(self):
        """Update user lastlogin"""
        self.last_login = datetime.datetime.now()
        Session().add(self)
        log.debug('updated user %s lastlogin', self.username)

    def update_lastactivity(self):
        """Update user lastactivity"""
        usr = self
        old = usr.user_data
        old.update({'last_activity': time.time()})
        usr.user_data = old
        Session().add(usr)
        log.debug('updated user %s lastactivity', usr.username)

    def update_password(self, new_password, change_api_key=False):
        from rhodecode.lib.auth import get_crypt_password,generate_auth_token

        self.password = get_crypt_password(new_password)
        if change_api_key:
            self.api_key = generate_auth_token(self.username)
        Session().add(self)

    @classmethod
    def get_first_super_admin(cls):
        user = User.query().filter(User.admin == true()).first()
        if user is None:
            raise Exception('FATAL: Missing administrative account!')
        return user

    @classmethod
    def get_all_super_admins(cls):
        """
        Returns all admin accounts sorted by username
        """
        return User.query().filter(User.admin == true())\
            .order_by(User.username.asc()).all()

    @classmethod
    def get_default_user(cls, cache=False):
        user = User.get_by_username(User.DEFAULT_USER, cache=cache)
        if user is None:
            raise Exception('FATAL: Missing default account!')
        return user

    def _get_default_perms(self, user, suffix=''):
        from rhodecode.model.permission import PermissionModel
        return PermissionModel().get_default_perms(user.user_perms, suffix)

    def get_default_perms(self, suffix=''):
        return self._get_default_perms(self, suffix)

    def get_api_data(self, include_secrets=False, details='full'):
        """
        Common function for generating user related data for API

        :param include_secrets: By default secrets in the API data will be replaced
           by a placeholder value to prevent exposing this data by accident. In case
           this data shall be exposed, set this flag to ``True``.

        :param details: details can be 'basic|full' basic gives only a subset of
           the available user information that includes user_id, name and emails.
        """
        user = self
        user_data = self.user_data
        data = {
            'user_id': user.user_id,
            'username': user.username,
            'firstname': user.name,
            'lastname': user.lastname,
            'email': user.email,
            'emails': user.emails,
        }
        if details == 'basic':
            return data

        api_key_length = 40
        api_key_replacement = '*' * api_key_length

        extras = {
            'api_key': api_key_replacement,
            'api_keys': [api_key_replacement],
            'active': user.active,
            'admin': user.admin,
            'extern_type': user.extern_type,
            'extern_name': user.extern_name,
            'last_login': user.last_login,
            'ip_addresses': user.ip_addresses,
            'language': user_data.get('language')
        }
        data.update(extras)

        if include_secrets:
            data['api_key'] = user.api_key
            data['api_keys'] = user.auth_tokens
        return data

    def __json__(self):
        data = {
            'full_name': self.full_name,
            'full_name_or_username': self.full_name_or_username,
            'short_contact': self.short_contact,
            'full_contact': self.full_contact,
        }
        data.update(self.get_api_data())
        return data


class UserApiKeys(Base, BaseModel):
    __tablename__ = 'user_api_keys'
    __table_args__ = (
        Index('uak_api_key_idx', 'api_key'),
        Index('uak_api_key_expires_idx', 'api_key', 'expires'),
        UniqueConstraint('api_key'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    __mapper_args__ = {}

    # ApiKey role
    ROLE_ALL = 'token_role_all'
    ROLE_HTTP = 'token_role_http'
    ROLE_VCS = 'token_role_vcs'
    ROLE_API = 'token_role_api'
    ROLE_FEED = 'token_role_feed'
    ROLES = [ROLE_ALL, ROLE_HTTP, ROLE_VCS, ROLE_API, ROLE_FEED]

    user_api_key_id = Column("user_api_key_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=True, unique=None, default=None)
    api_key = Column("api_key", String(255), nullable=False, unique=True)
    description = Column('description', UnicodeText().with_variant(UnicodeText(1024), 'mysql'))
    expires = Column('expires', Float(53), nullable=False)
    role = Column('role', String(255), nullable=True)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)

    user = relationship('User', lazy='joined')

    @classmethod
    def _get_role_name(cls, role):
        return {
            cls.ROLE_ALL: _('all'),
            cls.ROLE_HTTP: _('http/web interface'),
            cls.ROLE_VCS: _('vcs (git/hg/svn protocol)'),
            cls.ROLE_API: _('api calls'),
            cls.ROLE_FEED: _('feed access'),
        }.get(role, role)

    @property
    def expired(self):
        if self.expires == -1:
            return False
        return time.time() > self.expires

    @property
    def role_humanized(self):
        return self._get_role_name(self.role)


class UserEmailMap(Base, BaseModel):
    __tablename__ = 'user_email_map'
    __table_args__ = (
        Index('uem_email_idx', 'email'),
        UniqueConstraint('email'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    __mapper_args__ = {}

    email_id = Column("email_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=True, unique=None, default=None)
    _email = Column("email", String(255), nullable=True, unique=False, default=None)
    user = relationship('User', lazy='joined')

    @validates('_email')
    def validate_email(self, key, email):
        # check if this email is not main one
        main_email = Session().query(User).filter(User.email == email).scalar()
        if main_email is not None:
            raise AttributeError('email %s is present is user table' % email)
        return email

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, val):
        self._email = val.lower() if val else None


class UserIpMap(Base, BaseModel):
    __tablename__ = 'user_ip_map'
    __table_args__ = (
        UniqueConstraint('user_id', 'ip_addr'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    __mapper_args__ = {}

    ip_id = Column("ip_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=True, unique=None, default=None)
    ip_addr = Column("ip_addr", String(255), nullable=True, unique=False, default=None)
    active = Column("active", Boolean(), nullable=True, unique=None, default=True)
    description = Column("description", String(10000), nullable=True, unique=None, default=None)
    user = relationship('User', lazy='joined')

    @classmethod
    def _get_ip_range(cls, ip_addr):
        net = ipaddress.ip_network(ip_addr, strict=False)
        return [str(net.network_address), str(net.broadcast_address)]

    def __json__(self):
        return {
          'ip_addr': self.ip_addr,
          'ip_range': self._get_ip_range(self.ip_addr),
        }

    def __unicode__(self):
        return u"<%s('user_id:%s=>%s')>" % (self.__class__.__name__,
                                            self.user_id, self.ip_addr)

class UserLog(Base, BaseModel):
    __tablename__ = 'user_logs'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    user_log_id = Column("user_log_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=True, unique=None, default=None)
    username = Column("username", String(255), nullable=True, unique=None, default=None)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=True)
    repository_name = Column("repository_name", String(255), nullable=True, unique=None, default=None)
    user_ip = Column("user_ip", String(255), nullable=True, unique=None, default=None)
    action = Column("action", Text().with_variant(Text(1200000), 'mysql'), nullable=True, unique=None, default=None)
    action_date = Column("action_date", DateTime(timezone=False), nullable=True, unique=None, default=None)

    def __unicode__(self):
        return u"<%s('id:%s:%s')>" % (self.__class__.__name__,
                                      self.repository_name,
                                      self.action)

    @property
    def action_as_day(self):
        return datetime.date(*self.action_date.timetuple()[:3])

    user = relationship('User')
    repository = relationship('Repository', cascade='')


class UserGroup(Base, BaseModel):
    __tablename__ = 'users_groups'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )

    users_group_id = Column("users_group_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_name = Column("users_group_name", String(255), nullable=False, unique=True, default=None)
    user_group_description = Column("user_group_description", String(10000), nullable=True, unique=None, default=None)
    users_group_active = Column("users_group_active", Boolean(), nullable=True, unique=None, default=None)
    inherit_default_permissions = Column("users_group_inherit_default_permissions", Boolean(), nullable=False, unique=None, default=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=False, default=None)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    _group_data = Column("group_data", LargeBinary(), nullable=True)  # JSON data

    members = relationship('UserGroupMember', cascade="all, delete, delete-orphan", lazy="joined")
    users_group_to_perm = relationship('UserGroupToPerm', cascade='all')
    users_group_repo_to_perm = relationship('UserGroupRepoToPerm', cascade='all')
    users_group_repo_group_to_perm = relationship('UserGroupRepoGroupToPerm', cascade='all')
    user_user_group_to_perm = relationship('UserUserGroupToPerm', cascade='all')
    user_group_user_group_to_perm = relationship('UserGroupUserGroupToPerm ', primaryjoin="UserGroupUserGroupToPerm.target_user_group_id==UserGroup.users_group_id", cascade='all')

    user = relationship('User')

    @hybrid_property
    def group_data(self):
        if not self._group_data:
            return {}

        try:
            return json.loads(self._group_data)
        except TypeError:
            return {}

    @group_data.setter
    def group_data(self, val):
        try:
            self._group_data = json.dumps(val)
        except Exception:
            log.error(traceback.format_exc())

    def __unicode__(self):
        return u"<%s('id:%s:%s')>" % (self.__class__.__name__,
                                      self.users_group_id,
                                      self.users_group_name)

    @classmethod
    def get_by_group_name(cls, group_name, cache=False,
                          case_insensitive=False):
        if case_insensitive:
            q = cls.query().filter(func.lower(cls.users_group_name) ==
                                   func.lower(group_name))

        else:
            q = cls.query().filter(cls.users_group_name == group_name)
        if cache:
            q = q.options(FromCache(
                            "sql_cache_short",
                            "get_group_%s" % _hash_key(group_name)))
        return q.scalar()

    @classmethod
    def get(cls, user_group_id, cache=False):
        user_group = cls.query()
        if cache:
            user_group = user_group.options(FromCache("sql_cache_short",
                                    "get_users_group_%s" % user_group_id))
        return user_group.get(user_group_id)

    def permissions(self, with_admins=True, with_owner=True):
        q = UserUserGroupToPerm.query().filter(UserUserGroupToPerm.user_group == self)
        q = q.options(joinedload(UserUserGroupToPerm.user_group),
                      joinedload(UserUserGroupToPerm.user),
                      joinedload(UserUserGroupToPerm.permission),)

        # get owners and admins and permissions. We do a trick of re-writing
        # objects from sqlalchemy to named-tuples due to sqlalchemy session
        # has a global reference and changing one object propagates to all
        # others. This means if admin is also an owner admin_row that change
        # would propagate to both objects
        perm_rows = []
        for _usr in q.all():
            usr = AttributeDict(_usr.user.get_dict())
            usr.permission = _usr.permission.permission_name
            perm_rows.append(usr)

        # filter the perm rows by 'default' first and then sort them by
        # admin,write,read,none permissions sorted again alphabetically in
        # each group
        perm_rows = sorted(perm_rows, key=display_sort)

        _admin_perm = 'usergroup.admin'
        owner_row = []
        if with_owner:
            usr = AttributeDict(self.user.get_dict())
            usr.owner_row = True
            usr.permission = _admin_perm
            owner_row.append(usr)

        super_admin_rows = []
        if with_admins:
            for usr in User.get_all_super_admins():
                # if this admin is also owner, don't double the record
                if usr.user_id == owner_row[0].user_id:
                    owner_row[0].admin_row = True
                else:
                    usr = AttributeDict(usr.get_dict())
                    usr.admin_row = True
                    usr.permission = _admin_perm
                    super_admin_rows.append(usr)

        return super_admin_rows + owner_row + perm_rows

    def permission_user_groups(self):
        q = UserGroupUserGroupToPerm.query().filter(UserGroupUserGroupToPerm.target_user_group == self)
        q = q.options(joinedload(UserGroupUserGroupToPerm.user_group),
                      joinedload(UserGroupUserGroupToPerm.target_user_group),
                      joinedload(UserGroupUserGroupToPerm.permission),)

        perm_rows = []
        for _user_group in q.all():
            usr = AttributeDict(_user_group.user_group.get_dict())
            usr.permission = _user_group.permission.permission_name
            perm_rows.append(usr)

        return perm_rows

    def _get_default_perms(self, user_group, suffix=''):
        from rhodecode.model.permission import PermissionModel
        return PermissionModel().get_default_perms(user_group.users_group_to_perm, suffix)

    def get_default_perms(self, suffix=''):
        return self._get_default_perms(self, suffix)

    def get_api_data(self, with_group_members=True, include_secrets=False):
        """
        :param include_secrets: See :meth:`User.get_api_data`, this parameter is
           basically forwarded.

        """
        user_group = self

        data = {
            'users_group_id': user_group.users_group_id,
            'group_name': user_group.users_group_name,
            'group_description': user_group.user_group_description,
            'active': user_group.users_group_active,
            'owner': user_group.user.username,
        }
        if with_group_members:
            users = []
            for user in user_group.members:
                user = user.user
                users.append(user.get_api_data(include_secrets=include_secrets))
            data['users'] = users

        return data


class UserGroupMember(Base, BaseModel):
    __tablename__ = 'users_groups_members'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )

    users_group_member_id = Column("users_group_member_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_id = Column("users_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)

    user = relationship('User', lazy='joined')
    users_group = relationship('UserGroup')

    def __init__(self, gr_id='', u_id=''):
        self.users_group_id = gr_id
        self.user_id = u_id


class RepositoryField(Base, BaseModel):
    __tablename__ = 'repositories_fields'
    __table_args__ = (
        UniqueConstraint('repository_id', 'field_key'),  # no-multi field
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    PREFIX = 'ex_'  # prefix used in form to not conflict with already existing fields

    repo_field_id = Column("repo_field_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=False, unique=None, default=None)
    field_key = Column("field_key", String(250))
    field_label = Column("field_label", String(1024), nullable=False)
    field_value = Column("field_value", String(10000), nullable=False)
    field_desc = Column("field_desc", String(1024), nullable=False)
    field_type = Column("field_type", String(255), nullable=False, unique=None)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)

    repository = relationship('Repository')

    @property
    def field_key_prefixed(self):
        return 'ex_%s' % self.field_key

    @classmethod
    def un_prefix_key(cls, key):
        if key.startswith(cls.PREFIX):
            return key[len(cls.PREFIX):]
        return key

    @classmethod
    def get_by_key_name(cls, key, repo):
        row = cls.query()\
                .filter(cls.repository == repo)\
                .filter(cls.field_key == key).scalar()
        return row


class Repository(Base, BaseModel):
    __tablename__ = 'repositories'
    __table_args__ = (
        Index('r_repo_name_idx', 'repo_name', mysql_length=255),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    DEFAULT_CLONE_URI = '{scheme}://{user}@{netloc}/{repo}'
    DEFAULT_CLONE_URI_ID = '{scheme}://{user}@{netloc}/_{repoid}'

    STATE_CREATED = 'repo_state_created'
    STATE_PENDING = 'repo_state_pending'
    STATE_ERROR = 'repo_state_error'

    LOCK_AUTOMATIC = 'lock_auto'
    LOCK_API = 'lock_api'
    LOCK_WEB = 'lock_web'
    LOCK_PULL = 'lock_pull'

    NAME_SEP = URL_SEP

    repo_id = Column(
        "repo_id", Integer(), nullable=False, unique=True, default=None,
        primary_key=True)
    _repo_name = Column(
        "repo_name", Text(), nullable=False, default=None)
    _repo_name_hash = Column(
        "repo_name_hash", String(255), nullable=False, unique=True)
    repo_state = Column("repo_state", String(255), nullable=True)

    clone_uri = Column(
        "clone_uri", EncryptedTextValue(), nullable=True, unique=False,
        default=None)
    repo_type = Column(
        "repo_type", String(255), nullable=False, unique=False, default=None)
    user_id = Column(
        "user_id", Integer(), ForeignKey('users.user_id'), nullable=False,
        unique=False, default=None)
    private = Column(
        "private", Boolean(), nullable=True, unique=None, default=None)
    enable_statistics = Column(
        "statistics", Boolean(), nullable=True, unique=None, default=True)
    enable_downloads = Column(
        "downloads", Boolean(), nullable=True, unique=None, default=True)
    description = Column(
        "description", String(10000), nullable=True, unique=None, default=None)
    created_on = Column(
        'created_on', DateTime(timezone=False), nullable=True, unique=None,
        default=datetime.datetime.now)
    updated_on = Column(
        'updated_on', DateTime(timezone=False), nullable=True, unique=None,
        default=datetime.datetime.now)
    _landing_revision = Column(
        "landing_revision", String(255), nullable=False, unique=False,
        default=None)
    enable_locking = Column(
        "enable_locking", Boolean(), nullable=False, unique=None,
        default=False)
    _locked = Column(
        "locked", String(255), nullable=True, unique=False, default=None)
    _changeset_cache = Column(
        "changeset_cache", LargeBinary(), nullable=True)  # JSON data

    fork_id = Column(
        "fork_id", Integer(), ForeignKey('repositories.repo_id'),
        nullable=True, unique=False, default=None)
    group_id = Column(
        "group_id", Integer(), ForeignKey('groups.group_id'), nullable=True,
        unique=False, default=None)

    user = relationship('User', lazy='joined')
    fork = relationship('Repository', remote_side=repo_id, lazy='joined')
    group = relationship('RepoGroup', lazy='joined')
    repo_to_perm = relationship(
        'UserRepoToPerm', cascade='all',
        order_by='UserRepoToPerm.repo_to_perm_id')
    users_group_to_perm = relationship('UserGroupRepoToPerm', cascade='all')
    stats = relationship('Statistics', cascade='all', uselist=False)

    followers = relationship(
        'UserFollowing',
        primaryjoin='UserFollowing.follows_repo_id==Repository.repo_id',
        cascade='all')
    extra_fields = relationship(
        'RepositoryField', cascade="all, delete, delete-orphan")
    logs = relationship('UserLog')
    comments = relationship(
        'ChangesetComment', cascade="all, delete, delete-orphan")
    pull_requests_source = relationship(
        'PullRequest',
        primaryjoin='PullRequest.source_repo_id==Repository.repo_id',
        cascade="all, delete, delete-orphan")
    pull_requests_target = relationship(
        'PullRequest',
        primaryjoin='PullRequest.target_repo_id==Repository.repo_id',
        cascade="all, delete, delete-orphan")
    ui = relationship('RepoRhodeCodeUi', cascade="all")
    settings = relationship('RepoRhodeCodeSetting', cascade="all")

    def __unicode__(self):
        return u"<%s('%s:%s')>" % (self.__class__.__name__, self.repo_id,
                                   safe_unicode(self.repo_name))

    @hybrid_property
    def landing_rev(self):
        # always should return [rev_type, rev]
        if self._landing_revision:
            _rev_info = self._landing_revision.split(':')
            if len(_rev_info) < 2:
                _rev_info.insert(0, 'rev')
            return [_rev_info[0], _rev_info[1]]
        return [None, None]

    @landing_rev.setter
    def landing_rev(self, val):
        if ':' not in val:
            raise ValueError('value must be delimited with `:` and consist '
                             'of <rev_type>:<rev>, got %s instead' % val)
        self._landing_revision = val

    @hybrid_property
    def locked(self):
        if self._locked:
            user_id, timelocked, reason = self._locked.split(':')
            lock_values = int(user_id), timelocked, reason
        else:
            lock_values = [None, None, None]
        return lock_values

    @locked.setter
    def locked(self, val):
        if val and isinstance(val, (list, tuple)):
            self._locked = ':'.join(map(str, val))
        else:
            self._locked = None

    @hybrid_property
    def changeset_cache(self):
        from rhodecode.lib.vcs.backends.base import EmptyCommit
        dummy = EmptyCommit().__json__()
        if not self._changeset_cache:
            return dummy
        try:
            return json.loads(self._changeset_cache)
        except TypeError:
            return dummy
        except Exception:
            log.error(traceback.format_exc())
            return dummy

    @changeset_cache.setter
    def changeset_cache(self, val):
        try:
            self._changeset_cache = json.dumps(val)
        except Exception:
            log.error(traceback.format_exc())

    @hybrid_property
    def repo_name(self):
        return self._repo_name

    @repo_name.setter
    def repo_name(self, value):
        self._repo_name = value
        self._repo_name_hash = hashlib.sha1(safe_str(value)).hexdigest()

    @classmethod
    def normalize_repo_name(cls, repo_name):
        """
        Normalizes os specific repo_name to the format internally stored inside
        database using URL_SEP

        :param cls:
        :param repo_name:
        """
        return cls.NAME_SEP.join(repo_name.split(os.sep))

    @classmethod
    def get_by_repo_name(cls, repo_name, cache=False, identity_cache=False):
        session = Session()
        q = session.query(cls).filter(cls.repo_name == repo_name)

        if cache:
            if identity_cache:
                val = cls.identity_cache(session, 'repo_name', repo_name)
                if val:
                    return val
            else:
                q = q.options(
                    FromCache("sql_cache_short",
                              "get_repo_by_name_%s" % _hash_key(repo_name)))

        return q.scalar()

    @classmethod
    def get_by_full_path(cls, repo_full_path):
        repo_name = repo_full_path.split(cls.base_path(), 1)[-1]
        repo_name = cls.normalize_repo_name(repo_name)
        return cls.get_by_repo_name(repo_name.strip(URL_SEP))

    @classmethod
    def get_repo_forks(cls, repo_id):
        return cls.query().filter(Repository.fork_id == repo_id)

    @classmethod
    def base_path(cls):
        """
        Returns base path when all repos are stored

        :param cls:
        """
        q = Session().query(RhodeCodeUi)\
            .filter(RhodeCodeUi.ui_key == cls.NAME_SEP)
        q = q.options(FromCache("sql_cache_short", "repository_repo_path"))
        return q.one().ui_value

    @classmethod
    def is_valid(cls, repo_name):
        """
        returns True if given repo name is a valid filesystem repository

        :param cls:
        :param repo_name:
        """
        from rhodecode.lib.utils import is_valid_repo

        return is_valid_repo(repo_name, cls.base_path())

    @classmethod
    def get_all_repos(cls, user_id=Optional(None), group_id=Optional(None),
                      case_insensitive=True):
        q = Repository.query()

        if not isinstance(user_id, Optional):
            q = q.filter(Repository.user_id == user_id)

        if not isinstance(group_id, Optional):
            q = q.filter(Repository.group_id == group_id)

        if case_insensitive:
            q = q.order_by(func.lower(Repository.repo_name))
        else:
            q = q.order_by(Repository.repo_name)
        return q.all()

    @property
    def forks(self):
        """
        Return forks of this repo
        """
        return Repository.get_repo_forks(self.repo_id)

    @property
    def parent(self):
        """
        Returns fork parent
        """
        return self.fork

    @property
    def just_name(self):
        return self.repo_name.split(self.NAME_SEP)[-1]

    @property
    def groups_with_parents(self):
        groups = []
        if self.group is None:
            return groups

        cur_gr = self.group
        groups.insert(0, cur_gr)
        while 1:
            gr = getattr(cur_gr, 'parent_group', None)
            cur_gr = cur_gr.parent_group
            if gr is None:
                break
            groups.insert(0, gr)

        return groups

    @property
    def groups_and_repo(self):
        return self.groups_with_parents, self

    @LazyProperty
    def repo_path(self):
        """
        Returns base full path for that repository means where it actually
        exists on a filesystem
        """
        q = Session().query(RhodeCodeUi).filter(
            RhodeCodeUi.ui_key == self.NAME_SEP)
        q = q.options(FromCache("sql_cache_short", "repository_repo_path"))
        return q.one().ui_value

    @property
    def repo_full_path(self):
        p = [self.repo_path]
        # we need to split the name by / since this is how we store the
        # names in the database, but that eventually needs to be converted
        # into a valid system path
        p += self.repo_name.split(self.NAME_SEP)
        return os.path.join(*map(safe_unicode, p))

    @property
    def cache_keys(self):
        """
        Returns associated cache keys for that repo
        """
        return CacheKey.query()\
            .filter(CacheKey.cache_args == self.repo_name)\
            .order_by(CacheKey.cache_key)\
            .all()

    def get_new_name(self, repo_name):
        """
        returns new full repository name based on assigned group and new new

        :param group_name:
        """
        path_prefix = self.group.full_path_splitted if self.group else []
        return self.NAME_SEP.join(path_prefix + [repo_name])

    @property
    def _config(self):
        """
        Returns db based config object.
        """
        from rhodecode.lib.utils import make_db_config
        return make_db_config(clear_session=False, repo=self)

    def permissions(self, with_admins=True, with_owner=True):
        q = UserRepoToPerm.query().filter(UserRepoToPerm.repository == self)
        q = q.options(joinedload(UserRepoToPerm.repository),
                      joinedload(UserRepoToPerm.user),
                      joinedload(UserRepoToPerm.permission),)

        # get owners and admins and permissions. We do a trick of re-writing
        # objects from sqlalchemy to named-tuples due to sqlalchemy session
        # has a global reference and changing one object propagates to all
        # others. This means if admin is also an owner admin_row that change
        # would propagate to both objects
        perm_rows = []
        for _usr in q.all():
            usr = AttributeDict(_usr.user.get_dict())
            usr.permission = _usr.permission.permission_name
            perm_rows.append(usr)

        # filter the perm rows by 'default' first and then sort them by
        # admin,write,read,none permissions sorted again alphabetically in
        # each group
        perm_rows = sorted(perm_rows, key=display_sort)

        _admin_perm = 'repository.admin'
        owner_row = []
        if with_owner:
            usr = AttributeDict(self.user.get_dict())
            usr.owner_row = True
            usr.permission = _admin_perm
            owner_row.append(usr)

        super_admin_rows = []
        if with_admins:
            for usr in User.get_all_super_admins():
                # if this admin is also owner, don't double the record
                if usr.user_id == owner_row[0].user_id:
                    owner_row[0].admin_row = True
                else:
                    usr = AttributeDict(usr.get_dict())
                    usr.admin_row = True
                    usr.permission = _admin_perm
                    super_admin_rows.append(usr)

        return super_admin_rows + owner_row + perm_rows

    def permission_user_groups(self):
        q = UserGroupRepoToPerm.query().filter(
            UserGroupRepoToPerm.repository == self)
        q = q.options(joinedload(UserGroupRepoToPerm.repository),
                      joinedload(UserGroupRepoToPerm.users_group),
                      joinedload(UserGroupRepoToPerm.permission),)

        perm_rows = []
        for _user_group in q.all():
            usr = AttributeDict(_user_group.users_group.get_dict())
            usr.permission = _user_group.permission.permission_name
            perm_rows.append(usr)

        return perm_rows

    def get_api_data(self, include_secrets=False):
        """
        Common function for generating repo api data

        :param include_secrets: See :meth:`User.get_api_data`.

        """
        # TODO: mikhail: Here there is an anti-pattern, we probably need to
        # move this methods on models level.
        from rhodecode.model.settings import SettingsModel

        repo = self
        _user_id, _time, _reason = self.locked

        data = {
            'repo_id': repo.repo_id,
            'repo_name': repo.repo_name,
            'repo_type': repo.repo_type,
            'clone_uri': repo.clone_uri or '',
            'url': url('summary_home', repo_name=self.repo_name, qualified=True),
            'private': repo.private,
            'created_on': repo.created_on,
            'description': repo.description,
            'landing_rev': repo.landing_rev,
            'owner': repo.user.username,
            'fork_of': repo.fork.repo_name if repo.fork else None,
            'enable_statistics': repo.enable_statistics,
            'enable_locking': repo.enable_locking,
            'enable_downloads': repo.enable_downloads,
            'last_changeset': repo.changeset_cache,
            'locked_by': User.get(_user_id).get_api_data(
                include_secrets=include_secrets) if _user_id else None,
            'locked_date': time_to_datetime(_time) if _time else None,
            'lock_reason': _reason if _reason else None,
        }

        # TODO: mikhail: should be per-repo settings here
        rc_config = SettingsModel().get_all_settings()
        repository_fields = str2bool(
            rc_config.get('rhodecode_repository_fields'))
        if repository_fields:
            for f in self.extra_fields:
                data[f.field_key_prefixed] = f.field_value

        return data

    @classmethod
    def lock(cls, repo, user_id, lock_time=None, lock_reason=None):
        if not lock_time:
            lock_time = time.time()
        if not lock_reason:
            lock_reason = cls.LOCK_AUTOMATIC
        repo.locked = [user_id, lock_time, lock_reason]
        Session().add(repo)
        Session().commit()

    @classmethod
    def unlock(cls, repo):
        repo.locked = None
        Session().add(repo)
        Session().commit()

    @classmethod
    def getlock(cls, repo):
        return repo.locked

    def is_user_lock(self, user_id):
        if self.lock[0]:
            lock_user_id = safe_int(self.lock[0])
            user_id = safe_int(user_id)
            # both are ints, and they are equal
            return all([lock_user_id, user_id]) and lock_user_id == user_id

        return False

    def get_locking_state(self, action, user_id, only_when_enabled=True):
        """
        Checks locking on this repository, if locking is enabled and lock is
        present returns a tuple of make_lock, locked, locked_by.
        make_lock can have 3 states None (do nothing) True, make lock
        False release lock, This value is later propagated to hooks, which
        do the locking. Think about this as signals passed to hooks what to do.

        """
        # TODO: johbo: This is part of the business logic and should be moved
        # into the RepositoryModel.

        if action not in ('push', 'pull'):
            raise ValueError("Invalid action value: %s" % repr(action))

        # defines if locked error should be thrown to user
        currently_locked = False
        # defines if new lock should be made, tri-state
        make_lock = None
        repo = self
        user = User.get(user_id)

        lock_info = repo.locked

        if repo and (repo.enable_locking or not only_when_enabled):
            if action == 'push':
                # check if it's already locked !, if it is compare users
                locked_by_user_id = lock_info[0]
                if user.user_id == locked_by_user_id:
                    log.debug(
                        'Got `push` action from user %s, now unlocking', user)
                    # unlock if we have push from user who locked
                    make_lock = False
                else:
                    # we're not the same user who locked, ban with
                    # code defined in settings (default is 423 HTTP Locked) !
                    log.debug('Repo %s is currently locked by %s', repo, user)
                    currently_locked = True
            elif action == 'pull':
                # [0] user [1] date
                if lock_info[0] and lock_info[1]:
                    log.debug('Repo %s is currently locked by %s', repo, user)
                    currently_locked = True
                else:
                    log.debug('Setting lock on repo %s by %s', repo, user)
                    make_lock = True

        else:
            log.debug('Repository %s do not have locking enabled', repo)

        log.debug('FINAL locking values make_lock:%s,locked:%s,locked_by:%s',
                  make_lock, currently_locked, lock_info)

        from rhodecode.lib.auth import HasRepoPermissionAny
        perm_check = HasRepoPermissionAny('repository.write', 'repository.admin')
        if make_lock and not perm_check(repo_name=repo.repo_name, user=user):
            # if we don't have at least write permission we cannot make a lock
            log.debug('lock state reset back to FALSE due to lack '
                      'of at least read permission')
            make_lock = False

        return make_lock, currently_locked, lock_info

    @property
    def last_db_change(self):
        return self.updated_on

    @property
    def clone_uri_hidden(self):
        clone_uri = self.clone_uri
        if clone_uri:
            import urlobject
            url_obj = urlobject.URLObject(clone_uri)
            if url_obj.password:
                clone_uri = url_obj.with_password('*****')
        return clone_uri

    def clone_url(self, **override):
        qualified_home_url = url('home', qualified=True)

        uri_tmpl = None
        if 'with_id' in override:
            uri_tmpl = self.DEFAULT_CLONE_URI_ID
            del override['with_id']

        if 'uri_tmpl' in override:
            uri_tmpl = override['uri_tmpl']
            del override['uri_tmpl']

        # we didn't override our tmpl from **overrides
        if not uri_tmpl:
            uri_tmpl = self.DEFAULT_CLONE_URI
            try:
                from pylons import tmpl_context as c
                uri_tmpl = c.clone_uri_tmpl
            except Exception:
                # in any case if we call this outside of request context,
                # ie, not having tmpl_context set up
                pass

        return get_clone_url(uri_tmpl=uri_tmpl,
                             qualifed_home_url=qualified_home_url,
                             repo_name=self.repo_name,
                             repo_id=self.repo_id, **override)

    def set_state(self, state):
        self.repo_state = state
        Session().add(self)
    #==========================================================================
    # SCM PROPERTIES
    #==========================================================================

    def get_commit(self, commit_id=None, commit_idx=None, pre_load=None):
        return get_commit_safe(
            self.scm_instance(), commit_id, commit_idx, pre_load=pre_load)

    def get_changeset(self, rev=None, pre_load=None):
        warnings.warn("Use get_commit", DeprecationWarning)
        commit_id = None
        commit_idx = None
        if isinstance(rev, basestring):
            commit_id = rev
        else:
            commit_idx = rev
        return self.get_commit(commit_id=commit_id, commit_idx=commit_idx,
                               pre_load=pre_load)

    def get_landing_commit(self):
        """
        Returns landing commit, or if that doesn't exist returns the tip
        """
        _rev_type, _rev = self.landing_rev
        commit = self.get_commit(_rev)
        if isinstance(commit, EmptyCommit):
            return self.get_commit()
        return commit

    def update_commit_cache(self, cs_cache=None, config=None):
        """
        Update cache of last changeset for repository, keys should be::

            short_id
            raw_id
            revision
            parents
            message
            date
            author

        :param cs_cache:
        """
        from rhodecode.lib.vcs.backends.base import BaseChangeset
        if cs_cache is None:
            # use no-cache version here
            scm_repo = self.scm_instance(cache=False, config=config)
            if scm_repo:
                cs_cache = scm_repo.get_commit(
                    pre_load=["author", "date", "message", "parents"])
            else:
                cs_cache = EmptyCommit()

        if isinstance(cs_cache, BaseChangeset):
            cs_cache = cs_cache.__json__()

        def is_outdated(new_cs_cache):
            if (new_cs_cache['raw_id'] != self.changeset_cache['raw_id'] or
                new_cs_cache['revision'] != self.changeset_cache['revision']):
                return True
            return False

        # check if we have maybe already latest cached revision
        if is_outdated(cs_cache) or not self.changeset_cache:
            _default = datetime.datetime.fromtimestamp(0)
            last_change = cs_cache.get('date') or _default
            log.debug('updated repo %s with new cs cache %s',
                      self.repo_name, cs_cache)
            self.updated_on = last_change
            self.changeset_cache = cs_cache
            Session().add(self)
            Session().commit()
        else:
            log.debug('Skipping update_commit_cache for repo:`%s` '
                      'commit already with latest changes', self.repo_name)

    @property
    def tip(self):
        return self.get_commit('tip')

    @property
    def author(self):
        return self.tip.author

    @property
    def last_change(self):
        return self.scm_instance().last_change

    def get_comments(self, revisions=None):
        """
        Returns comments for this repository grouped by revisions

        :param revisions: filter query by revisions only
        """
        cmts = ChangesetComment.query()\
            .filter(ChangesetComment.repo == self)
        if revisions:
            cmts = cmts.filter(ChangesetComment.revision.in_(revisions))
        grouped = collections.defaultdict(list)
        for cmt in cmts.all():
            grouped[cmt.revision].append(cmt)
        return grouped

    def statuses(self, revisions=None):
        """
        Returns statuses for this repository

        :param revisions: list of revisions to get statuses for
        """
        statuses = ChangesetStatus.query()\
            .filter(ChangesetStatus.repo == self)\
            .filter(ChangesetStatus.version == 0)

        if revisions:
            # Try doing the filtering in chunks to avoid hitting limits
            size = 500
            status_results = []
            for chunk in xrange(0, len(revisions), size):
                status_results += statuses.filter(
                    ChangesetStatus.revision.in_(
                        revisions[chunk: chunk+size])
                ).all()
        else:
            status_results = statuses.all()

        grouped = {}

        # maybe we have open new pullrequest without a status?
        stat = ChangesetStatus.STATUS_UNDER_REVIEW
        status_lbl = ChangesetStatus.get_status_lbl(stat)
        for pr in PullRequest.query().filter(PullRequest.source_repo == self).all():
            for rev in pr.revisions:
                pr_id = pr.pull_request_id
                pr_repo = pr.target_repo.repo_name
                grouped[rev] = [stat, status_lbl, pr_id, pr_repo]

        for stat in status_results:
            pr_id = pr_repo = None
            if stat.pull_request:
                pr_id = stat.pull_request.pull_request_id
                pr_repo = stat.pull_request.target_repo.repo_name
            grouped[stat.revision] = [str(stat.status), stat.status_lbl,
                                      pr_id, pr_repo]
        return grouped

    # ==========================================================================
    # SCM CACHE INSTANCE
    # ==========================================================================

    def scm_instance(self, **kwargs):
        import rhodecode

        # Passing a config will not hit the cache currently only used
        # for repo2dbmapper
        config = kwargs.pop('config', None)
        cache = kwargs.pop('cache', None)
        full_cache = str2bool(rhodecode.CONFIG.get('vcs_full_cache'))
        # if cache is NOT defined use default global, else we have a full
        # control over cache behaviour
        if cache is None and full_cache and not config:
            return self._get_instance_cached()
        return self._get_instance(cache=bool(cache), config=config)

    def _get_instance_cached(self):
        @cache_region('long_term')
        def _get_repo(cache_key):
            return self._get_instance()

        invalidator_context = CacheKey.repo_context_cache(
            _get_repo, self.repo_name, None)

        with invalidator_context as context:
            context.invalidate()
            repo = context.compute()

        return repo

    def _get_instance(self, cache=True, config=None):
        repo_full_path = self.repo_full_path
        try:
            vcs_alias = get_scm(repo_full_path)[0]
            log.debug(
                'Creating instance of %s repository from %s',
                vcs_alias, repo_full_path)
            backend = get_backend(vcs_alias)
        except VCSError:
            log.exception(
                'Perhaps this repository is in db and not in '
                'filesystem run rescan repositories with '
                '"destroy old data" option from admin panel')
            return

        config = config or self._config
        custom_wire = {
            'cache': cache  # controls the vcs.remote cache
        }
        repo = backend(
            safe_str(repo_full_path), config=config, create=False,
            with_wire=custom_wire)

        return repo

    def __json__(self):
        return {'landing_rev': self.landing_rev}

    def get_dict(self):

        # Since we transformed `repo_name` to a hybrid property, we need to
        # keep compatibility with the code which uses `repo_name` field.

        result = super(Repository, self).get_dict()
        result['repo_name'] = result.pop('_repo_name', None)
        return result


class RepoGroup(Base, BaseModel):
    __tablename__ = 'groups'
    __table_args__ = (
        UniqueConstraint('group_name', 'group_parent_id'),
        CheckConstraint('group_id != group_parent_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    __mapper_args__ = {'order_by': 'group_name'}

    CHOICES_SEPARATOR = '/'  # used to generate select2 choices for nested groups

    group_id = Column("group_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    group_name = Column("group_name", String(255), nullable=False, unique=True, default=None)
    group_parent_id = Column("group_parent_id", Integer(), ForeignKey('groups.group_id'), nullable=True, unique=None, default=None)
    group_description = Column("group_description", String(10000), nullable=True, unique=None, default=None)
    enable_locking = Column("enable_locking", Boolean(), nullable=False, unique=None, default=False)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=False, default=None)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)

    repo_group_to_perm = relationship('UserRepoGroupToPerm', cascade='all', order_by='UserRepoGroupToPerm.group_to_perm_id')
    users_group_to_perm = relationship('UserGroupRepoGroupToPerm', cascade='all')
    parent_group = relationship('RepoGroup', remote_side=group_id)
    user = relationship('User')

    def __init__(self, group_name='', parent_group=None):
        self.group_name = group_name
        self.parent_group = parent_group

    def __unicode__(self):
        return u"<%s('id:%s:%s')>" % (self.__class__.__name__, self.group_id,
                                      self.group_name)

    @classmethod
    def _generate_choice(cls, repo_group):
        from webhelpers.html import literal as _literal
        _name = lambda k: _literal(cls.CHOICES_SEPARATOR.join(k))
        return repo_group.group_id, _name(repo_group.full_path_splitted)

    @classmethod
    def groups_choices(cls, groups=None, show_empty_group=True):
        if not groups:
            groups = cls.query().all()

        repo_groups = []
        if show_empty_group:
            repo_groups = [('-1', u'-- %s --' % _('No parent'))]

        repo_groups.extend([cls._generate_choice(x) for x in groups])

        repo_groups = sorted(
            repo_groups, key=lambda t: t[1].split(cls.CHOICES_SEPARATOR)[0])
        return repo_groups

    @classmethod
    def url_sep(cls):
        return URL_SEP

    @classmethod
    def get_by_group_name(cls, group_name, cache=False, case_insensitive=False):
        if case_insensitive:
            gr = cls.query().filter(func.lower(cls.group_name)
                                    == func.lower(group_name))
        else:
            gr = cls.query().filter(cls.group_name == group_name)
        if cache:
            gr = gr.options(FromCache(
                            "sql_cache_short",
                            "get_group_%s" % _hash_key(group_name)))
        return gr.scalar()

    @classmethod
    def get_all_repo_groups(cls, user_id=Optional(None), group_id=Optional(None),
                            case_insensitive=True):
        q = RepoGroup.query()

        if not isinstance(user_id, Optional):
            q = q.filter(RepoGroup.user_id == user_id)

        if not isinstance(group_id, Optional):
            q = q.filter(RepoGroup.group_parent_id == group_id)

        if case_insensitive:
            q = q.order_by(func.lower(RepoGroup.group_name))
        else:
            q = q.order_by(RepoGroup.group_name)
        return q.all()

    @property
    def parents(self):
        parents_recursion_limit = 10
        groups = []
        if self.parent_group is None:
            return groups
        cur_gr = self.parent_group
        groups.insert(0, cur_gr)
        cnt = 0
        while 1:
            cnt += 1
            gr = getattr(cur_gr, 'parent_group', None)
            cur_gr = cur_gr.parent_group
            if gr is None:
                break
            if cnt == parents_recursion_limit:
                # this will prevent accidental infinit loops
                log.error(('more than %s parents found for group %s, stopping '
                           'recursive parent fetching' % (parents_recursion_limit, self)))
                break

            groups.insert(0, gr)
        return groups

    @property
    def children(self):
        return RepoGroup.query().filter(RepoGroup.parent_group == self)

    @property
    def name(self):
        return self.group_name.split(RepoGroup.url_sep())[-1]

    @property
    def full_path(self):
        return self.group_name

    @property
    def full_path_splitted(self):
        return self.group_name.split(RepoGroup.url_sep())

    @property
    def repositories(self):
        return Repository.query()\
                .filter(Repository.group == self)\
                .order_by(Repository.repo_name)

    @property
    def repositories_recursive_count(self):
        cnt = self.repositories.count()

        def children_count(group):
            cnt = 0
            for child in group.children:
                cnt += child.repositories.count()
                cnt += children_count(child)
            return cnt

        return cnt + children_count(self)

    def _recursive_objects(self, include_repos=True):
        all_ = []

        def _get_members(root_gr):
            if include_repos:
                for r in root_gr.repositories:
                    all_.append(r)
            childs = root_gr.children.all()
            if childs:
                for gr in childs:
                    all_.append(gr)
                    _get_members(gr)

        _get_members(self)
        return [self] + all_

    def recursive_groups_and_repos(self):
        """
        Recursive return all groups, with repositories in those groups
        """
        return self._recursive_objects()

    def recursive_groups(self):
        """
        Returns all children groups for this group including children of children
        """
        return self._recursive_objects(include_repos=False)

    def get_new_name(self, group_name):
        """
        returns new full group name based on parent and new name

        :param group_name:
        """
        path_prefix = (self.parent_group.full_path_splitted if
                       self.parent_group else [])
        return RepoGroup.url_sep().join(path_prefix + [group_name])

    def permissions(self, with_admins=True, with_owner=True):
        q = UserRepoGroupToPerm.query().filter(UserRepoGroupToPerm.group == self)
        q = q.options(joinedload(UserRepoGroupToPerm.group),
                      joinedload(UserRepoGroupToPerm.user),
                      joinedload(UserRepoGroupToPerm.permission),)

        # get owners and admins and permissions. We do a trick of re-writing
        # objects from sqlalchemy to named-tuples due to sqlalchemy session
        # has a global reference and changing one object propagates to all
        # others. This means if admin is also an owner admin_row that change
        # would propagate to both objects
        perm_rows = []
        for _usr in q.all():
            usr = AttributeDict(_usr.user.get_dict())
            usr.permission = _usr.permission.permission_name
            perm_rows.append(usr)

        # filter the perm rows by 'default' first and then sort them by
        # admin,write,read,none permissions sorted again alphabetically in
        # each group
        perm_rows = sorted(perm_rows, key=display_sort)

        _admin_perm = 'group.admin'
        owner_row = []
        if with_owner:
            usr = AttributeDict(self.user.get_dict())
            usr.owner_row = True
            usr.permission = _admin_perm
            owner_row.append(usr)

        super_admin_rows = []
        if with_admins:
            for usr in User.get_all_super_admins():
                # if this admin is also owner, don't double the record
                if usr.user_id == owner_row[0].user_id:
                    owner_row[0].admin_row = True
                else:
                    usr = AttributeDict(usr.get_dict())
                    usr.admin_row = True
                    usr.permission = _admin_perm
                    super_admin_rows.append(usr)

        return super_admin_rows + owner_row + perm_rows

    def permission_user_groups(self):
        q = UserGroupRepoGroupToPerm.query().filter(UserGroupRepoGroupToPerm.group == self)
        q = q.options(joinedload(UserGroupRepoGroupToPerm.group),
                      joinedload(UserGroupRepoGroupToPerm.users_group),
                      joinedload(UserGroupRepoGroupToPerm.permission),)

        perm_rows = []
        for _user_group in q.all():
            usr = AttributeDict(_user_group.users_group.get_dict())
            usr.permission = _user_group.permission.permission_name
            perm_rows.append(usr)

        return perm_rows

    def get_api_data(self):
        """
        Common function for generating api data

        """
        group = self
        data = {
            'group_id': group.group_id,
            'group_name': group.group_name,
            'group_description': group.group_description,
            'parent_group': group.parent_group.group_name if group.parent_group else None,
            'repositories': [x.repo_name for x in group.repositories],
            'owner': group.user.username,
        }
        return data


class Permission(Base, BaseModel):
    __tablename__ = 'permissions'
    __table_args__ = (
        Index('p_perm_name_idx', 'permission_name'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    PERMS = [
        ('hg.admin', _('RhodeCode Super Administrator')),

        ('repository.none', _('Repository no access')),
        ('repository.read', _('Repository read access')),
        ('repository.write', _('Repository write access')),
        ('repository.admin', _('Repository admin access')),

        ('group.none', _('Repository group no access')),
        ('group.read', _('Repository group read access')),
        ('group.write', _('Repository group write access')),
        ('group.admin', _('Repository group admin access')),

        ('usergroup.none', _('User group no access')),
        ('usergroup.read', _('User group read access')),
        ('usergroup.write', _('User group write access')),
        ('usergroup.admin', _('User group admin access')),

        ('hg.repogroup.create.false', _('Repository Group creation disabled')),
        ('hg.repogroup.create.true', _('Repository Group creation enabled')),

        ('hg.usergroup.create.false', _('User Group creation disabled')),
        ('hg.usergroup.create.true', _('User Group creation enabled')),

        ('hg.create.none', _('Repository creation disabled')),
        ('hg.create.repository', _('Repository creation enabled')),
        ('hg.create.write_on_repogroup.true', _('Repository creation enabled with write permission to a repository group')),
        ('hg.create.write_on_repogroup.false', _('Repository creation disabled with write permission to a repository group')),

        ('hg.fork.none', _('Repository forking disabled')),
        ('hg.fork.repository', _('Repository forking enabled')),

        ('hg.register.none', _('Registration disabled')),
        ('hg.register.manual_activate', _('User Registration with manual account activation')),
        ('hg.register.auto_activate', _('User Registration with automatic account activation')),

        ('hg.extern_activate.manual', _('Manual activation of external account')),
        ('hg.extern_activate.auto', _('Automatic activation of external account')),

        ('hg.inherit_default_perms.false', _('Inherit object permissions from default user disabled')),
        ('hg.inherit_default_perms.true', _('Inherit object permissions from default user enabled')),
    ]

    # definition of system default permissions for DEFAULT user
    DEFAULT_USER_PERMISSIONS = [
        'repository.read',
        'group.read',
        'usergroup.read',
        'hg.create.repository',
        'hg.repogroup.create.false',
        'hg.usergroup.create.false',
        'hg.create.write_on_repogroup.true',
        'hg.fork.repository',
        'hg.register.manual_activate',
        'hg.extern_activate.auto',
        'hg.inherit_default_perms.true',
    ]

    # defines which permissions are more important higher the more important
    # Weight defines which permissions are more important.
    # The higher number the more important.
    PERM_WEIGHTS = {
        'repository.none': 0,
        'repository.read': 1,
        'repository.write': 3,
        'repository.admin': 4,

        'group.none': 0,
        'group.read': 1,
        'group.write': 3,
        'group.admin': 4,

        'usergroup.none': 0,
        'usergroup.read': 1,
        'usergroup.write': 3,
        'usergroup.admin': 4,

        'hg.repogroup.create.false': 0,
        'hg.repogroup.create.true': 1,

        'hg.usergroup.create.false': 0,
        'hg.usergroup.create.true': 1,

        'hg.fork.none': 0,
        'hg.fork.repository': 1,
        'hg.create.none': 0,
        'hg.create.repository': 1
    }

    permission_id = Column("permission_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    permission_name = Column("permission_name", String(255), nullable=True, unique=None, default=None)
    permission_longname = Column("permission_longname", String(255), nullable=True, unique=None, default=None)

    def __unicode__(self):
        return u"<%s('%s:%s')>" % (
            self.__class__.__name__, self.permission_id, self.permission_name
        )

    @classmethod
    def get_by_key(cls, key):
        return cls.query().filter(cls.permission_name == key).scalar()

    @classmethod
    def get_default_repo_perms(cls, user_id, repo_id=None):
        q = Session().query(UserRepoToPerm, Repository, Permission)\
            .join((Permission, UserRepoToPerm.permission_id == Permission.permission_id))\
            .join((Repository, UserRepoToPerm.repository_id == Repository.repo_id))\
            .filter(UserRepoToPerm.user_id == user_id)
        if repo_id:
            q = q.filter(UserRepoToPerm.repository_id == repo_id)
        return q.all()

    @classmethod
    def get_default_repo_perms_from_user_group(cls, user_id, repo_id=None):
        q = Session().query(UserGroupRepoToPerm, Repository, Permission)\
            .join(
                Permission,
                UserGroupRepoToPerm.permission_id == Permission.permission_id)\
            .join(
                Repository,
                UserGroupRepoToPerm.repository_id == Repository.repo_id)\
            .join(
                UserGroup,
                UserGroupRepoToPerm.users_group_id ==
                UserGroup.users_group_id)\
            .join(
                UserGroupMember,
                UserGroupRepoToPerm.users_group_id ==
                UserGroupMember.users_group_id)\
            .filter(
                UserGroupMember.user_id == user_id,
                UserGroup.users_group_active == true())
        if repo_id:
            q = q.filter(UserGroupRepoToPerm.repository_id == repo_id)
        return q.all()

    @classmethod
    def get_default_group_perms(cls, user_id, repo_group_id=None):
        q = Session().query(UserRepoGroupToPerm, RepoGroup, Permission)\
            .join((Permission, UserRepoGroupToPerm.permission_id == Permission.permission_id))\
            .join((RepoGroup, UserRepoGroupToPerm.group_id == RepoGroup.group_id))\
            .filter(UserRepoGroupToPerm.user_id == user_id)
        if repo_group_id:
            q = q.filter(UserRepoGroupToPerm.group_id == repo_group_id)
        return q.all()

    @classmethod
    def get_default_group_perms_from_user_group(
            cls, user_id, repo_group_id=None):
        q = Session().query(UserGroupRepoGroupToPerm, RepoGroup, Permission)\
            .join(
                Permission,
                UserGroupRepoGroupToPerm.permission_id ==
                Permission.permission_id)\
            .join(
                RepoGroup,
                UserGroupRepoGroupToPerm.group_id == RepoGroup.group_id)\
            .join(
                UserGroup,
                UserGroupRepoGroupToPerm.users_group_id ==
                UserGroup.users_group_id)\
            .join(
                UserGroupMember,
                UserGroupRepoGroupToPerm.users_group_id ==
                UserGroupMember.users_group_id)\
            .filter(
                UserGroupMember.user_id == user_id,
                UserGroup.users_group_active == true())
        if repo_group_id:
            q = q.filter(UserGroupRepoGroupToPerm.group_id == repo_group_id)
        return q.all()

    @classmethod
    def get_default_user_group_perms(cls, user_id, user_group_id=None):
        q = Session().query(UserUserGroupToPerm, UserGroup, Permission)\
            .join((Permission, UserUserGroupToPerm.permission_id == Permission.permission_id))\
            .join((UserGroup, UserUserGroupToPerm.user_group_id == UserGroup.users_group_id))\
            .filter(UserUserGroupToPerm.user_id == user_id)
        if user_group_id:
            q = q.filter(UserUserGroupToPerm.user_group_id == user_group_id)
        return q.all()

    @classmethod
    def get_default_user_group_perms_from_user_group(
            cls, user_id, user_group_id=None):
        TargetUserGroup = aliased(UserGroup, name='target_user_group')
        q = Session().query(UserGroupUserGroupToPerm, UserGroup, Permission)\
            .join(
                Permission,
                UserGroupUserGroupToPerm.permission_id ==
                Permission.permission_id)\
            .join(
                TargetUserGroup,
                UserGroupUserGroupToPerm.target_user_group_id ==
                TargetUserGroup.users_group_id)\
            .join(
                UserGroup,
                UserGroupUserGroupToPerm.user_group_id ==
                UserGroup.users_group_id)\
            .join(
                UserGroupMember,
                UserGroupUserGroupToPerm.user_group_id ==
                UserGroupMember.users_group_id)\
            .filter(
                UserGroupMember.user_id == user_id,
                UserGroup.users_group_active == true())
        if user_group_id:
            q = q.filter(
                UserGroupUserGroupToPerm.user_group_id == user_group_id)

        return q.all()


class UserRepoToPerm(Base, BaseModel):
    __tablename__ = 'repo_to_perm'
    __table_args__ = (
        UniqueConstraint('user_id', 'repository_id', 'permission_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    repo_to_perm_id = Column("repo_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=False, unique=None, default=None)

    user = relationship('User')
    repository = relationship('Repository')
    permission = relationship('Permission')

    @classmethod
    def create(cls, user, repository, permission):
        n = cls()
        n.user = user
        n.repository = repository
        n.permission = permission
        Session().add(n)
        return n

    def __unicode__(self):
        return u'<%s => %s >' % (self.user, self.repository)


class UserUserGroupToPerm(Base, BaseModel):
    __tablename__ = 'user_user_group_to_perm'
    __table_args__ = (
        UniqueConstraint('user_id', 'user_group_id', 'permission_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    user_user_group_to_perm_id = Column("user_user_group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)
    user_group_id = Column("user_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)

    user = relationship('User')
    user_group = relationship('UserGroup')
    permission = relationship('Permission')

    @classmethod
    def create(cls, user, user_group, permission):
        n = cls()
        n.user = user
        n.user_group = user_group
        n.permission = permission
        Session().add(n)
        return n

    def __unicode__(self):
        return u'<%s => %s >' % (self.user, self.user_group)


class UserToPerm(Base, BaseModel):
    __tablename__ = 'user_to_perm'
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    user_to_perm_id = Column("user_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)

    user = relationship('User')
    permission = relationship('Permission', lazy='joined')

    def __unicode__(self):
        return u'<%s => %s >' % (self.user, self.permission)


class UserGroupRepoToPerm(Base, BaseModel):
    __tablename__ = 'users_group_repo_to_perm'
    __table_args__ = (
        UniqueConstraint('repository_id', 'users_group_id', 'permission_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    users_group_to_perm_id = Column("users_group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_id = Column("users_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=False, unique=None, default=None)

    users_group = relationship('UserGroup')
    permission = relationship('Permission')
    repository = relationship('Repository')

    @classmethod
    def create(cls, users_group, repository, permission):
        n = cls()
        n.users_group = users_group
        n.repository = repository
        n.permission = permission
        Session().add(n)
        return n

    def __unicode__(self):
        return u'<UserGroupRepoToPerm:%s => %s >' % (self.users_group, self.repository)


class UserGroupUserGroupToPerm(Base, BaseModel):
    __tablename__ = 'user_group_user_group_to_perm'
    __table_args__ = (
        UniqueConstraint('target_user_group_id', 'user_group_id', 'permission_id'),
        CheckConstraint('target_user_group_id != user_group_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    user_group_user_group_to_perm_id = Column("user_group_user_group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    target_user_group_id = Column("target_user_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)
    user_group_id = Column("user_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)

    target_user_group = relationship('UserGroup', primaryjoin='UserGroupUserGroupToPerm.target_user_group_id==UserGroup.users_group_id')
    user_group = relationship('UserGroup', primaryjoin='UserGroupUserGroupToPerm.user_group_id==UserGroup.users_group_id')
    permission = relationship('Permission')

    @classmethod
    def create(cls, target_user_group, user_group, permission):
        n = cls()
        n.target_user_group = target_user_group
        n.user_group = user_group
        n.permission = permission
        Session().add(n)
        return n

    def __unicode__(self):
        return u'<UserGroupUserGroup:%s => %s >' % (self.target_user_group, self.user_group)


class UserGroupToPerm(Base, BaseModel):
    __tablename__ = 'users_group_to_perm'
    __table_args__ = (
        UniqueConstraint('users_group_id', 'permission_id',),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    users_group_to_perm_id = Column("users_group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_id = Column("users_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)

    users_group = relationship('UserGroup')
    permission = relationship('Permission')


class UserRepoGroupToPerm(Base, BaseModel):
    __tablename__ = 'user_repo_group_to_perm'
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', 'permission_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    group_to_perm_id = Column("group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    group_id = Column("group_id", Integer(), ForeignKey('groups.group_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)

    user = relationship('User')
    group = relationship('RepoGroup')
    permission = relationship('Permission')

    @classmethod
    def create(cls, user, repository_group, permission):
        n = cls()
        n.user = user
        n.group = repository_group
        n.permission = permission
        Session().add(n)
        return n


class UserGroupRepoGroupToPerm(Base, BaseModel):
    __tablename__ = 'users_group_repo_group_to_perm'
    __table_args__ = (
        UniqueConstraint('users_group_id', 'group_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    users_group_repo_group_to_perm_id = Column("users_group_repo_group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_id = Column("users_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    group_id = Column("group_id", Integer(), ForeignKey('groups.group_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)

    users_group = relationship('UserGroup')
    permission = relationship('Permission')
    group = relationship('RepoGroup')

    @classmethod
    def create(cls, user_group, repository_group, permission):
        n = cls()
        n.users_group = user_group
        n.group = repository_group
        n.permission = permission
        Session().add(n)
        return n

    def __unicode__(self):
        return u'<UserGroupRepoGroupToPerm:%s => %s >' % (self.users_group, self.group)


class Statistics(Base, BaseModel):
    __tablename__ = 'statistics'
    __table_args__ = (
         UniqueConstraint('repository_id'),
         {'extend_existing': True, 'mysql_engine': 'InnoDB',
          'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    stat_id = Column("stat_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=False, unique=True, default=None)
    stat_on_revision = Column("stat_on_revision", Integer(), nullable=False)
    commit_activity = Column("commit_activity", LargeBinary(1000000), nullable=False)#JSON data
    commit_activity_combined = Column("commit_activity_combined", LargeBinary(), nullable=False)#JSON data
    languages = Column("languages", LargeBinary(1000000), nullable=False)#JSON data

    repository = relationship('Repository', single_parent=True)


class UserFollowing(Base, BaseModel):
    __tablename__ = 'user_followings'
    __table_args__ = (
        UniqueConstraint('user_id', 'follows_repository_id'),
        UniqueConstraint('user_id', 'follows_user_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    user_following_id = Column("user_following_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    follows_repo_id = Column("follows_repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=True, unique=None, default=None)
    follows_user_id = Column("follows_user_id", Integer(), ForeignKey('users.user_id'), nullable=True, unique=None, default=None)
    follows_from = Column('follows_from', DateTime(timezone=False), nullable=True, unique=None, default=datetime.datetime.now)

    user = relationship('User', primaryjoin='User.user_id==UserFollowing.user_id')

    follows_user = relationship('User', primaryjoin='User.user_id==UserFollowing.follows_user_id')
    follows_repository = relationship('Repository', order_by='Repository.repo_name')

    @classmethod
    def get_repo_followers(cls, repo_id):
        return cls.query().filter(cls.follows_repo_id == repo_id)


class CacheKey(Base, BaseModel):
    __tablename__ = 'cache_invalidation'
    __table_args__ = (
        UniqueConstraint('cache_key'),
        Index('key_idx', 'cache_key'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    CACHE_TYPE_ATOM = 'ATOM'
    CACHE_TYPE_RSS = 'RSS'
    CACHE_TYPE_README = 'README'

    cache_id = Column("cache_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    cache_key = Column("cache_key", String(255), nullable=True, unique=None, default=None)
    cache_args = Column("cache_args", String(255), nullable=True, unique=None, default=None)
    cache_active = Column("cache_active", Boolean(), nullable=True, unique=None, default=False)

    def __init__(self, cache_key, cache_args=''):
        self.cache_key = cache_key
        self.cache_args = cache_args
        self.cache_active = False

    def __unicode__(self):
        return u"<%s('%s:%s[%s]')>" % (
            self.__class__.__name__,
            self.cache_id, self.cache_key, self.cache_active)

    def _cache_key_partition(self):
        prefix, repo_name, suffix = self.cache_key.partition(self.cache_args)
        return prefix, repo_name, suffix

    def get_prefix(self):
        """
        Try to extract prefix from existing cache key. The key could consist
        of prefix, repo_name, suffix
        """
        # this returns prefix, repo_name, suffix
        return self._cache_key_partition()[0]

    def get_suffix(self):
        """
        get suffix that might have been used in _get_cache_key to
        generate self.cache_key. Only used for informational purposes
        in repo_edit.html.
        """
        # prefix, repo_name, suffix
        return self._cache_key_partition()[2]

    @classmethod
    def delete_all_cache(cls):
        """
        Delete all cache keys from database.
        Should only be run when all instances are down and all entries
        thus stale.
        """
        cls.query().delete()
        Session().commit()

    @classmethod
    def get_cache_key(cls, repo_name, cache_type):
        """

        Generate a cache key for this process of RhodeCode instance.
        Prefix most likely will be process id or maybe explicitly set
        instance_id from .ini file.
        """
        import rhodecode
        prefix = safe_unicode(rhodecode.CONFIG.get('instance_id') or '')

        repo_as_unicode = safe_unicode(repo_name)
        key = u'{}_{}'.format(repo_as_unicode, cache_type) \
            if cache_type else repo_as_unicode

        return u'{}{}'.format(prefix, key)

    @classmethod
    def set_invalidate(cls, repo_name, delete=False):
        """
        Mark all caches of a repo as invalid in the database.
        """

        try:
            qry = Session().query(cls).filter(cls.cache_args == repo_name)
            if delete:
                log.debug('cache objects deleted for repo %s',
                          safe_str(repo_name))
                qry.delete()
            else:
                log.debug('cache objects marked as invalid for repo %s',
                          safe_str(repo_name))
                qry.update({"cache_active": False})

            Session().commit()
        except Exception:
            log.exception(
                'Cache key invalidation failed for repository %s',
                safe_str(repo_name))
            Session().rollback()

    @classmethod
    def get_active_cache(cls, cache_key):
        inv_obj = cls.query().filter(cls.cache_key == cache_key).scalar()
        if inv_obj:
            return inv_obj
        return None

    @classmethod
    def repo_context_cache(cls, compute_func, repo_name, cache_type):
        """
        @cache_region('long_term')
        def _heavy_calculation(cache_key):
            return 'result'

        cache_context = CacheKey.repo_context_cache(
            _heavy_calculation, repo_name, cache_type)

        with cache_context as context:
            context.invalidate()
            computed = context.compute()

        assert computed == 'result'
        """
        from rhodecode.lib import caches
        return caches.InvalidationContext(compute_func, repo_name, cache_type)


class ChangesetComment(Base, BaseModel):
    __tablename__ = 'changeset_comments'
    __table_args__ = (
        Index('cc_revision_idx', 'revision'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )

    COMMENT_OUTDATED = u'comment_outdated'

    comment_id = Column('comment_id', Integer(), nullable=False, primary_key=True)
    repo_id = Column('repo_id', Integer(), ForeignKey('repositories.repo_id'), nullable=False)
    revision = Column('revision', String(40), nullable=True)
    pull_request_id = Column("pull_request_id", Integer(), ForeignKey('pull_requests.pull_request_id'), nullable=True)
    pull_request_version_id = Column("pull_request_version_id", Integer(), ForeignKey('pull_request_versions.pull_request_version_id'), nullable=True)
    line_no = Column('line_no', Unicode(10), nullable=True)
    hl_lines = Column('hl_lines', Unicode(512), nullable=True)
    f_path = Column('f_path', Unicode(1000), nullable=True)
    user_id = Column('user_id', Integer(), ForeignKey('users.user_id'), nullable=False)
    text = Column('text', UnicodeText().with_variant(UnicodeText(25000), 'mysql'), nullable=False)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    modified_at = Column('modified_at', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    renderer = Column('renderer', Unicode(64), nullable=True)
    display_state = Column('display_state',  Unicode(128), nullable=True)

    author = relationship('User', lazy='joined')
    repo = relationship('Repository')
    status_change = relationship('ChangesetStatus', cascade="all, delete, delete-orphan")
    pull_request = relationship('PullRequest', lazy='joined')
    pull_request_version = relationship('PullRequestVersion')

    @classmethod
    def get_users(cls, revision=None, pull_request_id=None):
        """
        Returns user associated with this ChangesetComment. ie those
        who actually commented

        :param cls:
        :param revision:
        """
        q = Session().query(User)\
                .join(ChangesetComment.author)
        if revision:
            q = q.filter(cls.revision == revision)
        elif pull_request_id:
            q = q.filter(cls.pull_request_id == pull_request_id)
        return q.all()

    def render(self, mentions=False):
        from rhodecode.lib import helpers as h
        return h.render(self.text, renderer=self.renderer, mentions=mentions)

    def __repr__(self):
        if self.comment_id:
            return '<DB:ChangesetComment #%s>' % self.comment_id
        else:
            return '<DB:ChangesetComment at %#x>' % id(self)


class ChangesetStatus(Base, BaseModel):
    __tablename__ = 'changeset_statuses'
    __table_args__ = (
        Index('cs_revision_idx', 'revision'),
        Index('cs_version_idx', 'version'),
        UniqueConstraint('repo_id', 'revision', 'version'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    STATUS_NOT_REVIEWED = DEFAULT = 'not_reviewed'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_UNDER_REVIEW = 'under_review'

    STATUSES = [
        (STATUS_NOT_REVIEWED, _("Not Reviewed")),  # (no icon) and default
        (STATUS_APPROVED, _("Approved")),
        (STATUS_REJECTED, _("Rejected")),
        (STATUS_UNDER_REVIEW, _("Under Review")),
    ]

    changeset_status_id = Column('changeset_status_id', Integer(), nullable=False, primary_key=True)
    repo_id = Column('repo_id', Integer(), ForeignKey('repositories.repo_id'), nullable=False)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None)
    revision = Column('revision', String(40), nullable=False)
    status = Column('status', String(128), nullable=False, default=DEFAULT)
    changeset_comment_id = Column('changeset_comment_id', Integer(), ForeignKey('changeset_comments.comment_id'))
    modified_at = Column('modified_at', DateTime(), nullable=False, default=datetime.datetime.now)
    version = Column('version', Integer(), nullable=False, default=0)
    pull_request_id = Column("pull_request_id", Integer(), ForeignKey('pull_requests.pull_request_id'), nullable=True)

    author = relationship('User', lazy='joined')
    repo = relationship('Repository')
    comment = relationship('ChangesetComment', lazy='joined')
    pull_request = relationship('PullRequest', lazy='joined')

    def __unicode__(self):
        return u"<%s('%s[%s]:%s')>" % (
            self.__class__.__name__,
            self.status, self.version, self.author
        )

    @classmethod
    def get_status_lbl(cls, value):
        return dict(cls.STATUSES).get(value)

    @property
    def status_lbl(self):
        return ChangesetStatus.get_status_lbl(self.status)


class _PullRequestBase(BaseModel):
    """
    Common attributes of pull request and version entries.
    """

    # .status values
    STATUS_NEW = u'new'
    STATUS_OPEN = u'open'
    STATUS_CLOSED = u'closed'

    title = Column('title', Unicode(255), nullable=True)
    description = Column(
        'description', UnicodeText().with_variant(UnicodeText(10240), 'mysql'),
        nullable=True)
    # new/open/closed status of pull request (not approve/reject/etc)
    status = Column('status', Unicode(255), nullable=False, default=STATUS_NEW)
    created_on = Column(
        'created_on', DateTime(timezone=False), nullable=False,
        default=datetime.datetime.now)
    updated_on = Column(
        'updated_on', DateTime(timezone=False), nullable=False,
        default=datetime.datetime.now)

    @declared_attr
    def user_id(cls):
        return Column(
            "user_id", Integer(), ForeignKey('users.user_id'), nullable=False,
            unique=None)

    # 500 revisions max
    _revisions = Column(
        'revisions', UnicodeText().with_variant(UnicodeText(20500), 'mysql'))

    @declared_attr
    def source_repo_id(cls):
        # TODO: dan: rename column to source_repo_id
        return Column(
            'org_repo_id', Integer(), ForeignKey('repositories.repo_id'),
            nullable=False)

    source_ref = Column('org_ref', Unicode(255), nullable=False)

    @declared_attr
    def target_repo_id(cls):
        # TODO: dan: rename column to target_repo_id
        return Column(
            'other_repo_id', Integer(), ForeignKey('repositories.repo_id'),
            nullable=False)

    target_ref = Column('other_ref', Unicode(255), nullable=False)

    # TODO: dan: rename column to last_merge_source_rev
    _last_merge_source_rev = Column(
        'last_merge_org_rev', String(40), nullable=True)
    # TODO: dan: rename column to last_merge_target_rev
    _last_merge_target_rev = Column(
        'last_merge_other_rev', String(40), nullable=True)
    _last_merge_status = Column('merge_status', Integer(), nullable=True)
    merge_rev = Column('merge_rev', String(40), nullable=True)

    @hybrid_property
    def revisions(self):
        return self._revisions.split(':') if self._revisions else []

    @revisions.setter
    def revisions(self, val):
        self._revisions = ':'.join(val)

    @declared_attr
    def author(cls):
        return relationship('User', lazy='joined')

    @declared_attr
    def source_repo(cls):
        return relationship(
            'Repository',
            primaryjoin='%s.source_repo_id==Repository.repo_id' % cls.__name__)

    @property
    def source_ref_parts(self):
        refs = self.source_ref.split(':')
        return Reference(refs[0], refs[1], refs[2])

    @declared_attr
    def target_repo(cls):
        return relationship(
            'Repository',
            primaryjoin='%s.target_repo_id==Repository.repo_id' % cls.__name__)

    @property
    def target_ref_parts(self):
        refs = self.target_ref.split(':')
        return Reference(refs[0], refs[1], refs[2])


class PullRequest(Base, _PullRequestBase):
    __tablename__ = 'pull_requests'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )

    pull_request_id = Column(
        'pull_request_id', Integer(), nullable=False, primary_key=True)

    def __repr__(self):
        if self.pull_request_id:
            return '<DB:PullRequest #%s>' % self.pull_request_id
        else:
            return '<DB:PullRequest at %#x>' % id(self)

    reviewers = relationship('PullRequestReviewers',
                             cascade="all, delete, delete-orphan")
    statuses = relationship('ChangesetStatus')
    comments = relationship('ChangesetComment',
                            cascade="all, delete, delete-orphan")
    versions = relationship('PullRequestVersion',
                            cascade="all, delete, delete-orphan")

    def is_closed(self):
        return self.status == self.STATUS_CLOSED

    def get_api_data(self):
        from rhodecode.model.pull_request import PullRequestModel
        pull_request = self
        merge_status = PullRequestModel().merge_status(pull_request)
        data = {
            'pull_request_id': pull_request.pull_request_id,
            'url': url('pullrequest_show', repo_name=self.target_repo.repo_name,
                                       pull_request_id=self.pull_request_id,
                                       qualified=True),
            'title': pull_request.title,
            'description': pull_request.description,
            'status': pull_request.status,
            'created_on': pull_request.created_on,
            'updated_on': pull_request.updated_on,
            'commit_ids': pull_request.revisions,
            'review_status': pull_request.calculated_review_status(),
            'mergeable': {
                'status': merge_status[0],
                'message': unicode(merge_status[1]),
            },
            'source': {
                'clone_url': pull_request.source_repo.clone_url(),
                'repository': pull_request.source_repo.repo_name,
                'reference': {
                    'name': pull_request.source_ref_parts.name,
                    'type': pull_request.source_ref_parts.type,
                    'commit_id': pull_request.source_ref_parts.commit_id,
                },
            },
            'target': {
                'clone_url': pull_request.target_repo.clone_url(),
                'repository': pull_request.target_repo.repo_name,
                'reference': {
                    'name': pull_request.target_ref_parts.name,
                    'type': pull_request.target_ref_parts.type,
                    'commit_id': pull_request.target_ref_parts.commit_id,
                },
            },
            'author': pull_request.author.get_api_data(include_secrets=False,
                                                       details='basic'),
            'reviewers': [
                {
                    'user': reviewer.get_api_data(include_secrets=False,
                                                  details='basic'),
                    'review_status': st[0][1].status if st else 'not_reviewed',
                }
                for reviewer, st in pull_request.reviewers_statuses()
            ]
        }

        return data

    def __json__(self):
        return {
            'revisions': self.revisions,
        }

    def calculated_review_status(self):
        # TODO: anderson: 13.05.15 Used only on templates/my_account_pullrequests.html
        # because it's tricky on how to use ChangesetStatusModel from there
        warnings.warn("Use calculated_review_status from ChangesetStatusModel", DeprecationWarning)
        from rhodecode.model.changeset_status import ChangesetStatusModel
        return ChangesetStatusModel().calculated_review_status(self)

    def reviewers_statuses(self):
        warnings.warn("Use reviewers_statuses from ChangesetStatusModel", DeprecationWarning)
        from rhodecode.model.changeset_status import ChangesetStatusModel
        return ChangesetStatusModel().reviewers_statuses(self)


class PullRequestVersion(Base, _PullRequestBase):
    __tablename__ = 'pull_request_versions'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )

    pull_request_version_id = Column(
        'pull_request_version_id', Integer(), nullable=False, primary_key=True)
    pull_request_id = Column(
        'pull_request_id', Integer(),
        ForeignKey('pull_requests.pull_request_id'), nullable=False)
    pull_request = relationship('PullRequest')

    def __repr__(self):
        if self.pull_request_version_id:
            return '<DB:PullRequestVersion #%s>' % self.pull_request_version_id
        else:
            return '<DB:PullRequestVersion at %#x>' % id(self)


class PullRequestReviewers(Base, BaseModel):
    __tablename__ = 'pull_request_reviewers'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )

    def __init__(self, user=None, pull_request=None):
        self.user = user
        self.pull_request = pull_request

    pull_requests_reviewers_id = Column(
        'pull_requests_reviewers_id', Integer(), nullable=False,
        primary_key=True)
    pull_request_id = Column(
        "pull_request_id", Integer(),
        ForeignKey('pull_requests.pull_request_id'), nullable=False)
    user_id = Column(
        "user_id", Integer(), ForeignKey('users.user_id'), nullable=True)

    user = relationship('User')
    pull_request = relationship('PullRequest')


class Notification(Base, BaseModel):
    __tablename__ = 'notifications'
    __table_args__ = (
        Index('notification_type_idx', 'type'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )

    TYPE_CHANGESET_COMMENT = u'cs_comment'
    TYPE_MESSAGE = u'message'
    TYPE_MENTION = u'mention'
    TYPE_REGISTRATION = u'registration'
    TYPE_PULL_REQUEST = u'pull_request'
    TYPE_PULL_REQUEST_COMMENT = u'pull_request_comment'

    notification_id = Column('notification_id', Integer(), nullable=False, primary_key=True)
    subject = Column('subject', Unicode(512), nullable=True)
    body = Column('body', UnicodeText().with_variant(UnicodeText(50000), 'mysql'), nullable=True)
    created_by = Column("created_by", Integer(), ForeignKey('users.user_id'), nullable=True)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    type_ = Column('type', Unicode(255))

    created_by_user = relationship('User')
    notifications_to_users = relationship('UserNotification', lazy='joined',
                                          cascade="all, delete, delete-orphan")

    @property
    def recipients(self):
        return [x.user for x in UserNotification.query()\
                .filter(UserNotification.notification == self)\
                .order_by(UserNotification.user_id.asc()).all()]

    @classmethod
    def create(cls, created_by, subject, body, recipients, type_=None):
        if type_ is None:
            type_ = Notification.TYPE_MESSAGE

        notification = cls()
        notification.created_by_user = created_by
        notification.subject = subject
        notification.body = body
        notification.type_ = type_
        notification.created_on = datetime.datetime.now()

        for u in recipients:
            assoc = UserNotification()
            assoc.notification = notification

            # if created_by is inside recipients mark his notification
            # as read
            if u.user_id == created_by.user_id:
                assoc.read = True

            u.notifications.append(assoc)
        Session().add(notification)

        return notification

    @property
    def description(self):
        from rhodecode.model.notification import NotificationModel
        return NotificationModel().make_description(self)


class UserNotification(Base, BaseModel):
    __tablename__ = 'user_to_notification'
    __table_args__ = (
        UniqueConstraint('user_id', 'notification_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    user_id = Column('user_id', Integer(), ForeignKey('users.user_id'), primary_key=True)
    notification_id = Column("notification_id", Integer(), ForeignKey('notifications.notification_id'), primary_key=True)
    read = Column('read', Boolean, default=False)
    sent_on = Column('sent_on', DateTime(timezone=False), nullable=True, unique=None)

    user = relationship('User', lazy="joined")
    notification = relationship('Notification', lazy="joined",
                                order_by=lambda: Notification.created_on.desc(),)

    def mark_as_read(self):
        self.read = True
        Session().add(self)


class Gist(Base, BaseModel):
    __tablename__ = 'gists'
    __table_args__ = (
        Index('g_gist_access_id_idx', 'gist_access_id'),
        Index('g_created_on_idx', 'created_on'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )
    GIST_PUBLIC = u'public'
    GIST_PRIVATE = u'private'
    DEFAULT_FILENAME = u'gistfile1.txt'

    ACL_LEVEL_PUBLIC = u'acl_public'
    ACL_LEVEL_PRIVATE = u'acl_private'

    gist_id = Column('gist_id', Integer(), primary_key=True)
    gist_access_id = Column('gist_access_id', Unicode(250))
    gist_description = Column('gist_description', UnicodeText().with_variant(UnicodeText(1024), 'mysql'))
    gist_owner = Column('user_id', Integer(), ForeignKey('users.user_id'), nullable=True)
    gist_expires = Column('gist_expires', Float(53), nullable=False)
    gist_type = Column('gist_type', Unicode(128), nullable=False)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    modified_at = Column('modified_at', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    acl_level = Column('acl_level', Unicode(128), nullable=True)

    owner = relationship('User')

    def __repr__(self):
        return '<Gist:[%s]%s>' % (self.gist_type, self.gist_access_id)

    @classmethod
    def get_or_404(cls, id_):
        res = cls.query().filter(cls.gist_access_id == id_).scalar()
        if not res:
            raise HTTPNotFound
        return res

    @classmethod
    def get_by_access_id(cls, gist_access_id):
        return cls.query().filter(cls.gist_access_id == gist_access_id).scalar()

    def gist_url(self):
        import rhodecode
        alias_url = rhodecode.CONFIG.get('gist_alias_url')
        if alias_url:
            return alias_url.replace('{gistid}', self.gist_access_id)

        return url('gist', gist_id=self.gist_access_id, qualified=True)

    @classmethod
    def base_path(cls):
        """
        Returns base path when all gists are stored

        :param cls:
        """
        from rhodecode.model.gist import GIST_STORE_LOC
        q = Session().query(RhodeCodeUi)\
            .filter(RhodeCodeUi.ui_key == URL_SEP)
        q = q.options(FromCache("sql_cache_short", "repository_repo_path"))
        return os.path.join(q.one().ui_value, GIST_STORE_LOC)

    def get_api_data(self):
        """
        Common function for generating gist related data for API
        """
        gist = self
        data = {
            'gist_id': gist.gist_id,
            'type': gist.gist_type,
            'access_id': gist.gist_access_id,
            'description': gist.gist_description,
            'url': gist.gist_url(),
            'expires': gist.gist_expires,
            'created_on': gist.created_on,
            'modified_at': gist.modified_at,
            'content': None,
            'acl_level': gist.acl_level,
        }
        return data

    def __json__(self):
        data = dict(
        )
        data.update(self.get_api_data())
        return data
    # SCM functions

    def scm_instance(self, **kwargs):
        from rhodecode.lib.vcs import get_repo
        base_path = self.base_path()
        return get_repo(os.path.join(*map(safe_str,
                                          [base_path, self.gist_access_id])))


class DbMigrateVersion(Base, BaseModel):
    __tablename__ = 'db_migrate_version'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    repository_id = Column('repository_id', String(250), primary_key=True)
    repository_path = Column('repository_path', Text)
    version = Column('version', Integer)


class ExternalIdentity(Base, BaseModel):
    __tablename__ = 'external_identities'
    __table_args__ = (
        Index('local_user_id_idx', 'local_user_id'),
        Index('external_id_idx', 'external_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'})

    external_id = Column('external_id', Unicode(255), default=u'',
                         primary_key=True)
    external_username = Column('external_username', Unicode(1024), default=u'')
    local_user_id = Column('local_user_id', Integer(),
                           ForeignKey('users.user_id'), primary_key=True)
    provider_name = Column('provider_name', Unicode(255), default=u'',
                           primary_key=True)
    access_token = Column('access_token', String(1024), default=u'')
    alt_token = Column('alt_token', String(1024), default=u'')
    token_secret = Column('token_secret', String(1024), default=u'')

    @classmethod
    def by_external_id_and_provider(cls, external_id, provider_name,
                                    local_user_id=None):
        """
        Returns ExternalIdentity instance based on search params

        :param external_id:
        :param provider_name:
        :return: ExternalIdentity
        """
        query = cls.query()
        query = query.filter(cls.external_id == external_id)
        query = query.filter(cls.provider_name == provider_name)
        if local_user_id:
            query = query.filter(cls.local_user_id == local_user_id)
        return query.first()

    @classmethod
    def user_by_external_id_and_provider(cls, external_id, provider_name):
        """
        Returns User instance based on search params

        :param external_id:
        :param provider_name:
        :return: User
        """
        query = User.query()
        query = query.filter(cls.external_id == external_id)
        query = query.filter(cls.provider_name == provider_name)
        query = query.filter(User.user_id == cls.local_user_id)
        return query.first()

    @classmethod
    def by_local_user_id(cls, local_user_id):
        """
        Returns all tokens for user

        :param local_user_id:
        :return: ExternalIdentity
        """
        query = cls.query()
        query = query.filter(cls.local_user_id == local_user_id)
        return query


class Integration(Base, BaseModel):
    __tablename__ = 'integrations'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True}
    )

    integration_id = Column('integration_id', Integer(), primary_key=True)
    integration_type = Column('integration_type', String(255))
    enabled = Column("enabled", Boolean(), nullable=False)
    name = Column('name', String(255), nullable=False)
    settings_json = Column('settings_json',
        UnicodeText().with_variant(UnicodeText(16384), 'mysql'))
    repo_id = Column(
        "repo_id", Integer(), ForeignKey('repositories.repo_id'),
        nullable=True, unique=None, default=None)
    repo = relationship('Repository', lazy='joined')

    @hybrid_property
    def settings(self):
        data = json.loads(self.settings_json or '{}')
        return data

    @settings.setter
    def settings(self, dct):
        self.settings_json = json.dumps(dct, indent=2)

    def __repr__(self):
        if self.repo:
            scope = 'repo=%r' % self.repo
        else:
            scope = 'global'

        return '<Integration(%r, %r)>' % (self.integration_type, scope)

    def settings_as_dict(self):
        return json.loads(self.settings_json)
