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
from sqlalchemy.exc import OperationalError
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

#==============================================================================
# BASE CLASSES
#==============================================================================

_hash_key = lambda k: md5_safe(k)


# this is propagated from .ini file beaker.session.secret
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


class EncryptedValue(TypeDecorator):
    """
    Special column for encrypted data, use like::

        value = Column("encrypted_value", EncryptedValue(40), nullable=False)

    This column is intelligent so if value is in unencrypted form it return
    unencrypted form, but on save it always encrypts
    """
    impl = String

    def process_bind_param(self, value, dialect):
        if not value:
            return value
        if value.startswith('enc$aes$'):
            # protect against double encrypting if someone manually starts doing
            raise ValueError('value needs to be in unencrypted format, ie. '
                             'not starting with enc$aes$')
        return 'enc$aes$%s' % AESCipher(ENCRYPTION_KEY).encrypt(value)

    def process_result_value(self, value, dialect):
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

            # at that stage we know it's our encryption
            decrypted_data = AESCipher(ENCRYPTION_KEY).decrypt(parts[2])
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
        self.app_settings_value = val
        self.app_settings_type = type

    @validates('_app_settings_value')
    def validate_settings_value(self, key, val):
        assert type(val) == unicode
        return val

    @hybrid_property
    def app_settings_value(self):
        v = self._app_settings_value
        _type = self.app_settings_type
        converter = self.SETTINGS_TYPES.get(_type) or self.SETTINGS_TYPES['unicode']
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
        if val not in self.SETTINGS_TYPES:
            raise Exception('type must be one of %s got %s'
                            % (self.SETTINGS_TYPES.keys(), val))
        self._app_settings_type = val

    def __unicode__(self):
        return u"<%s('%s:%s[%s]')>" % (
            self.__class__.__name__,
            self.app_settings_name, self.app_settings_value, self.app_settings_type
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

    ui_id = Column("ui_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    ui_section = Column("ui_section", String(255), nullable=True, unique=None, default=None)
    ui_key = Column("ui_key", String(255), nullable=True, unique=None, default=None)
    ui_value = Column("ui_value", String(255), nullable=True, unique=None, default=None)
    ui_active = Column("ui_active", Boolean(), nullable=True, unique=None, default=True)

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

    # TODO: Move it to some common place with RhodeCodeSetting
    SETTINGS_TYPES = {
        'str': safe_str,
        'int': safe_int,
        'unicode': safe_unicode,
        'bool': str2bool,
        'list': functools.partial(aslist, sep=',')
    }

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
        self.app_settings_value = val
        self.app_settings_type = type

    @validates('_app_settings_value')
    def validate_settings_value(self, key, val):
        assert type(val) == unicode
        return val

    @hybrid_property
    def app_settings_value(self):
        v = self._app_settings_value
        type_ = self.app_settings_type
        converter = (
            self.SETTINGS_TYPES.get(type_) or self.SETTINGS_TYPES['unicode'])
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
        if val not in self.SETTINGS_TYPES:
            raise Exception('type must be one of %s got %s'
                            % (self.SETTINGS_TYPES.keys(), val))
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

    group_member = relationship('UserGroupMember', cascade='all')

    notifications = relationship('UserNotification', cascade='all')
    # notifications assigned to this user
    user_created_notifications = relationship('Notification', cascade='all')
    # comments created by this user
    user_comments = relationship('ChangesetComment', cascade='all')
    user_emails = relationship('UserEmailMap', cascade='all')
    user_ip_map = relationship('UserIpMap', cascade='all')
    user_auth_tokens = relationship('UserApiKeys', cascade='all')
    # gists
    user_gists = relationship('Gist', cascade='all')
    # user pull requests
    user_pull_requests = relationship('PullRequest', cascade='all')

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
    def full_contact(self):
        return '%s %s <%s>' % (self.firstname, self.lastname, self.email)

    @property
    def short_contact(self):
        return '%s %s' % (self.firstname, self.lastname)

    @property
    def is_admin(self):
        return self.admin

    @classmethod
    def get_by_username(cls, username, case_insensitive=False, cache=False):
        if case_insensitive:
            q = cls.query().filter(func.lower(cls.username) == func.lower(username))
        else:
            q = cls.query().filter(cls.username == username)

        if cache:
            q = q.options(FromCache(
                            "sql_cache_short",
                            "get_user_%s" % _hash_key(username)))
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
    def get_first_admin(cls):
        user = User.query().filter(User.admin == True).first()
        if user is None:
            raise Exception('Missing administrative account!')
        return user

    @classmethod
    def get_default_user(cls, cache=False):
        user = User.get_by_username(User.DEFAULT_USER, cache=cache)
        if user is None:
            raise Exception('Missing default account!')
        return user


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

    @classmethod
    def get_by_key_name(cls, key, repo):
        row = cls.query()\
                .filter(cls.repository == repo)\
                .filter(cls.field_key == key).scalar()
        return row


class Repository(Base, BaseModel):
    __tablename__ = 'repositories'
    __table_args__ = (
        UniqueConstraint('repo_name'),
        Index('r_repo_name_idx', 'repo_name'),
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

    repo_id = Column("repo_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    repo_name = Column("repo_name", String(255), nullable=False, unique=True, default=None)
    repo_state = Column("repo_state", String(255), nullable=True)

    clone_uri = Column("clone_uri", EncryptedValue(255), nullable=True, unique=False, default=None)
    repo_type = Column("repo_type", String(255), nullable=False, unique=False, default=None)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=False, default=None)
    private = Column("private", Boolean(), nullable=True, unique=None, default=None)
    enable_statistics = Column("statistics", Boolean(), nullable=True, unique=None, default=True)
    enable_downloads = Column("downloads", Boolean(), nullable=True, unique=None, default=True)
    description = Column("description", String(10000), nullable=True, unique=None, default=None)
    created_on = Column('created_on', DateTime(timezone=False), nullable=True, unique=None, default=datetime.datetime.now)
    updated_on = Column('updated_on', DateTime(timezone=False), nullable=True, unique=None, default=datetime.datetime.now)
    _landing_revision = Column("landing_revision", String(255), nullable=False, unique=False, default=None)
    enable_locking = Column("enable_locking", Boolean(), nullable=False, unique=None, default=False)
    _locked = Column("locked", String(255), nullable=True, unique=False, default=None)
    _changeset_cache = Column("changeset_cache", LargeBinary(), nullable=True) #JSON data

    fork_id = Column("fork_id", Integer(), ForeignKey('repositories.repo_id'), nullable=True, unique=False, default=None)
    group_id = Column("group_id", Integer(), ForeignKey('groups.group_id'), nullable=True, unique=False, default=None)

    user = relationship('User')
    fork = relationship('Repository', remote_side=repo_id)
    group = relationship('RepoGroup')
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
    pull_requests_org = relationship(
        'PullRequest',
        primaryjoin='PullRequest.org_repo_id==Repository.repo_id',
        cascade="all, delete, delete-orphan")
    pull_requests_other = relationship(
        'PullRequest',
        primaryjoin='PullRequest.other_repo_id==Repository.repo_id',
        cascade="all, delete, delete-orphan")
    ui = relationship('RepoRhodeCodeUi', cascade="all")
    settings = relationship('RepoRhodeCodeSetting', cascade="all")

    def __unicode__(self):
        return u"<%s('%s:%s')>" % (self.__class__.__name__, self.repo_id,
                                   safe_unicode(self.repo_name))

    @classmethod
    def get_by_repo_name(cls, repo_name):
        q = Session().query(cls).filter(cls.repo_name == repo_name)
        q = q.options(joinedload(Repository.fork))\
            .options(joinedload(Repository.user))\
            .options(joinedload(Repository.group))
        return q.scalar()


class RepoGroup(Base, BaseModel):
    __tablename__ = 'groups'
    __table_args__ = (
        UniqueConstraint('group_name', 'group_parent_id'),
        CheckConstraint('group_id != group_parent_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    __mapper_args__ = {'order_by': 'group_name'}

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


class CacheKey(Base, BaseModel):
    __tablename__ = 'cache_invalidation'
    __table_args__ = (
        UniqueConstraint('cache_key'),
        Index('key_idx', 'cache_key'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    cache_id = Column("cache_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    cache_key = Column("cache_key", String(255), nullable=True, unique=None, default=None)
    cache_args = Column("cache_args", String(255), nullable=True, unique=None, default=None)
    cache_active = Column("cache_active", Boolean(), nullable=True, unique=None, default=False)

    def __init__(self, cache_key, cache_args=''):
        self.cache_key = cache_key
        self.cache_args = cache_args
        self.cache_active = False


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


class _PullRequestBase(BaseModel):
    """
    Common attributes of pull request and version entries.
    """

    STATUS_NEW = u'new'
    STATUS_OPEN = u'open'
    STATUS_CLOSED = u'closed'

    title = Column('title', Unicode(255), nullable=True)
    description = Column(
        'description', UnicodeText().with_variant(UnicodeText(10240), 'mysql'),
        nullable=True)

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

    _revisions = Column(
        'revisions', UnicodeText().with_variant(UnicodeText(20500), 'mysql'))

    @declared_attr
    def org_repo_id(cls):
        return Column(
            'org_repo_id', Integer(), ForeignKey('repositories.repo_id'),
            nullable=False)

    org_ref = Column('org_ref', Unicode(255), nullable=False)

    @declared_attr
    def other_repo_id(cls):
        return Column(
            'other_repo_id', Integer(), ForeignKey('repositories.repo_id'),
            nullable=False)

    other_ref = Column('other_ref', Unicode(255), nullable=False)
    _last_merge_org_rev = Column(
        'last_merge_org_rev', String(40), nullable=True)
    _last_merge_other_rev = Column(
        'last_merge_other_rev', String(40), nullable=True)
    _last_merge_status = Column('merge_status', Integer(), nullable=True)
    merge_rev = Column('merge_rev', String(40), nullable=True)

    @declared_attr
    def author(cls):
        return relationship('User', lazy='joined')

    @declared_attr
    def source_repo(cls):
        return relationship(
            'Repository',
            primaryjoin='%s.org_repo_id==Repository.repo_id' % cls.__name__)

    @declared_attr
    def target_repo(cls):
        return relationship(
            'Repository',
            primaryjoin='%s.other_repo_id==Repository.repo_id' % cls.__name__)


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


class DbMigrateVersion(Base, BaseModel):
    __tablename__ = 'db_migrate_version'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8', 'sqlite_autoincrement': True},
    )
    repository_id = Column('repository_id', String(250), primary_key=True)
    repository_path = Column('repository_path', Text)
    version = Column('version', Integer)
