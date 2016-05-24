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
import time
import logging
import datetime
import traceback
import hashlib
import collections

from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, joinedload, class_mapper, validates
from sqlalchemy.exc import DatabaseError
from beaker.cache import cache_region, region_invalidate
from webob.exc import HTTPNotFound

from pylons.i18n.translation import lazy_ugettext as _

from rhodecode.lib.vcs import get_backend
from rhodecode.lib.vcs.utils.helpers import get_scm
from rhodecode.lib.vcs.exceptions import VCSError
from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.utils2 import str2bool, safe_str, get_commit_safe, \
    safe_unicode, remove_suffix, remove_prefix
from rhodecode.lib.ext_json import json
from rhodecode.lib.caching_query import FromCache

from rhodecode.model.meta import Base, Session

URL_SEP = '/'
log = logging.getLogger(__name__)

#==============================================================================
# BASE CLASSES
#==============================================================================

_hash_key = lambda k: hashlib.md5(safe_str(k)).hexdigest()


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
        """return list with keys and values tupples corresponding
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
            return safe_str(self.__unicode__())
        return '<DB:%s>' % (self.__class__.__name__)


class RhodeCodeSetting(Base, BaseModel):
    __tablename__ = 'rhodecode_settings'
    __table_args__ = (
        UniqueConstraint('app_settings_name'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
    )
    app_settings_id = Column("app_settings_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    app_settings_name = Column("app_settings_name", String(255), nullable=True, unique=None, default=None)
    _app_settings_value = Column("app_settings_value", String(255), nullable=True, unique=None, default=None)

    def __init__(self, k='', v=''):
        self.app_settings_name = k
        self.app_settings_value = v

    @validates('_app_settings_value')
    def validate_settings_value(self, key, val):
        assert type(val) == unicode
        return val

    @hybrid_property
    def app_settings_value(self):
        v = self._app_settings_value
        if self.app_settings_name in ["ldap_active",
                                      "default_repo_enable_statistics",
                                      "default_repo_enable_locking",
                                      "default_repo_private",
                                      "default_repo_enable_downloads"]:
            v = str2bool(v)
        return v

    @app_settings_value.setter
    def app_settings_value(self, val):
        """
        Setter that will always make sure we use unicode in app_settings_value

        :param val:
        """
        self._app_settings_value = safe_unicode(val)

    def __unicode__(self):
        return u"<%s('%s:%s')>" % (
            self.__class__.__name__,
            self.app_settings_name, self.app_settings_value
        )


class RhodeCodeUi(Base, BaseModel):
    __tablename__ = 'rhodecode_ui'
    __table_args__ = (
        UniqueConstraint('ui_key'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
    )

    HOOK_REPO_SIZE = 'changegroup.repo_size'
    HOOK_PUSH = 'changegroup.push_logger'
    HOOK_PRE_PUSH = 'prechangegroup.pre_push'
    HOOK_PULL = 'outgoing.pull_logger'
    HOOK_PRE_PULL = 'preoutgoing.pre_pull'

    ui_id = Column("ui_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    ui_section = Column("ui_section", String(255), nullable=True, unique=None, default=None)
    ui_key = Column("ui_key", String(255), nullable=True, unique=None, default=None)
    ui_value = Column("ui_value", String(255), nullable=True, unique=None, default=None)
    ui_active = Column("ui_active", Boolean(), nullable=True, unique=None, default=True)



class User(Base, BaseModel):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('username'), UniqueConstraint('email'),
        Index('u_username_idx', 'username'),
        Index('u_email_idx', 'email'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
    )
    DEFAULT_USER = 'default'
    DEFAULT_PERMISSIONS = [
        'hg.register.manual_activate', 'hg.create.repository',
        'hg.fork.repository', 'repository.read', 'group.read'
    ]
    user_id = Column("user_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    username = Column("username", String(255), nullable=True, unique=None, default=None)
    password = Column("password", String(255), nullable=True, unique=None, default=None)
    active = Column("active", Boolean(), nullable=True, unique=None, default=True)
    admin = Column("admin", Boolean(), nullable=True, unique=None, default=False)
    name = Column("firstname", String(255), nullable=True, unique=None, default=None)
    lastname = Column("lastname", String(255), nullable=True, unique=None, default=None)
    _email = Column("email", String(255), nullable=True, unique=None, default=None)
    last_login = Column("last_login", DateTime(timezone=False), nullable=True, unique=None, default=None)
    ldap_dn = Column("ldap_dn", String(255), nullable=True, unique=None, default=None)
    api_key = Column("api_key", String(255), nullable=True, unique=None, default=None)
    inherit_default_permissions = Column("inherit_default_permissions", Boolean(), nullable=False, unique=None, default=True)

    user_log = relationship('UserLog')
    user_perms = relationship('UserToPerm', primaryjoin="User.user_id==UserToPerm.user_id", cascade='all')

    repositories = relationship('Repository')
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
            q = cls.query().filter(cls.username.ilike(username))
        else:
            q = cls.query().filter(cls.username == username)

        if cache:
            q = q.options(FromCache(
                            "sql_cache_short",
                            "get_user_%s" % _hash_key(username)
                          )
            )
        return q.scalar()

    @classmethod
    def get_by_auth_token(cls, auth_token, cache=False):
        q = cls.query().filter(cls.api_key == auth_token)

        if cache:
            q = q.options(FromCache("sql_cache_short",
                                    "get_auth_token_%s" % auth_token))
        return q.scalar()

    @classmethod
    def get_by_email(cls, email, case_insensitive=False, cache=False):
        if case_insensitive:
            q = cls.query().filter(cls.email.ilike(email))
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
                q = q.filter(UserEmailMap.email.ilike(email))
            else:
                q = q.filter(UserEmailMap.email == email)
            q = q.options(joinedload(UserEmailMap.user))
            if cache:
                q = q.options(FromCache("sql_cache_short",
                                        "get_email_map_key_%s" % email))
            ret = getattr(q.scalar(), 'user', None)

        return ret


class UserEmailMap(Base, BaseModel):
    __tablename__ = 'user_email_map'
    __table_args__ = (
        Index('uem_email_idx', 'email'),
        UniqueConstraint('email'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
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


class UserLog(Base, BaseModel):
    __tablename__ = 'user_logs'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )
    user_log_id = Column("user_log_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=True, unique=None, default=None)
    username = Column("username", String(255), nullable=True, unique=None, default=None)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=True)
    repository_name = Column("repository_name", String(255), nullable=True, unique=None, default=None)
    user_ip = Column("user_ip", String(255), nullable=True, unique=None, default=None)
    action = Column("action", String(1200000), nullable=True, unique=None, default=None)
    action_date = Column("action_date", DateTime(timezone=False), nullable=True, unique=None, default=None)


    user = relationship('User')
    repository = relationship('Repository', cascade='')


class UserGroup(Base, BaseModel):
    __tablename__ = 'users_groups'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )

    users_group_id = Column("users_group_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_name = Column("users_group_name", String(255), nullable=False, unique=True, default=None)
    users_group_active = Column("users_group_active", Boolean(), nullable=True, unique=None, default=None)
    inherit_default_permissions = Column("users_group_inherit_default_permissions", Boolean(), nullable=False, unique=None, default=True)

    members = relationship('UserGroupMember', cascade="all, delete, delete-orphan", lazy="joined")
    users_group_to_perm = relationship('UserGroupToPerm', cascade='all')
    users_group_repo_to_perm = relationship('UserGroupRepoToPerm', cascade='all')

    def __unicode__(self):
        return u'<userGroup(%s)>' % (self.users_group_name)

    @classmethod
    def get_by_group_name(cls, group_name, cache=False,
                          case_insensitive=False):
        if case_insensitive:
            q = cls.query().filter(cls.users_group_name.ilike(group_name))
        else:
            q = cls.query().filter(cls.users_group_name == group_name)
        if cache:
            q = q.options(FromCache(
                            "sql_cache_short",
                            "get_user_%s" % _hash_key(group_name)
                          )
            )
        return q.scalar()

    @classmethod
    def get(cls, users_group_id, cache=False):
        user_group = cls.query()
        if cache:
            user_group = user_group.options(FromCache("sql_cache_short",
                                    "get_users_group_%s" % users_group_id))
        return user_group.get(users_group_id)


class UserGroupMember(Base, BaseModel):
    __tablename__ = 'users_groups_members'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )

    users_group_member_id = Column("users_group_member_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_id = Column("users_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)

    user = relationship('User', lazy='joined')
    users_group = relationship('UserGroup')

    def __init__(self, gr_id='', u_id=''):
        self.users_group_id = gr_id
        self.user_id = u_id


class Repository(Base, BaseModel):
    __tablename__ = 'repositories'
    __table_args__ = (
        UniqueConstraint('repo_name'),
        Index('r_repo_name_idx', 'repo_name'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )

    repo_id = Column("repo_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    repo_name = Column("repo_name", String(255), nullable=False, unique=True, default=None)
    clone_uri = Column("clone_uri", String(255), nullable=True, unique=False, default=None)
    repo_type = Column("repo_type", String(255), nullable=False, unique=False, default=None)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=False, default=None)
    private = Column("private", Boolean(), nullable=True, unique=None, default=None)
    enable_statistics = Column("statistics", Boolean(), nullable=True, unique=None, default=True)
    enable_downloads = Column("downloads", Boolean(), nullable=True, unique=None, default=True)
    description = Column("description", String(10000), nullable=True, unique=None, default=None)
    created_on = Column('created_on', DateTime(timezone=False), nullable=True, unique=None, default=datetime.datetime.now)
    updated_on = Column('updated_on', DateTime(timezone=False), nullable=True, unique=None, default=datetime.datetime.now)
    landing_rev = Column("landing_revision", String(255), nullable=False, unique=False, default=None)
    enable_locking = Column("enable_locking", Boolean(), nullable=False, unique=None, default=False)
    _locked = Column("locked", String(255), nullable=True, unique=False, default=None)

    fork_id = Column("fork_id", Integer(), ForeignKey('repositories.repo_id'), nullable=True, unique=False, default=None)
    group_id = Column("group_id", Integer(), ForeignKey('groups.group_id'), nullable=True, unique=False, default=None)

    user = relationship('User')
    fork = relationship('Repository', remote_side=repo_id)
    group = relationship('RepoGroup')
    repo_to_perm = relationship('UserRepoToPerm', cascade='all', order_by='UserRepoToPerm.repo_to_perm_id')
    users_group_to_perm = relationship('UserGroupRepoToPerm', cascade='all')
    stats = relationship('Statistics', cascade='all', uselist=False)

    followers = relationship('UserFollowing',
                             primaryjoin='UserFollowing.follows_repo_id==Repository.repo_id',
                             cascade='all')

    logs = relationship('UserLog')
    comments = relationship('ChangesetComment', cascade="all, delete, delete-orphan")

    pull_requests_org = relationship('PullRequest',
                    primaryjoin='PullRequest.org_repo_id==Repository.repo_id',
                    cascade="all, delete, delete-orphan")

    pull_requests_other = relationship('PullRequest',
                    primaryjoin='PullRequest.other_repo_id==Repository.repo_id',
                    cascade="all, delete, delete-orphan")

    def __unicode__(self):
        return u"<%s('%s:%s')>" % (self.__class__.__name__, self.repo_id,
                                   self.repo_name)


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
         'mysql_charset': 'utf8'},
    )
    __mapper_args__ = {'order_by': 'group_name'}

    group_id = Column("group_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    group_name = Column("group_name", String(255), nullable=False, unique=True, default=None)
    group_parent_id = Column("group_parent_id", Integer(), ForeignKey('groups.group_id'), nullable=True, unique=None, default=None)
    group_description = Column("group_description", String(10000), nullable=True, unique=None, default=None)
    enable_locking = Column("enable_locking", Boolean(), nullable=False, unique=None, default=False)

    repo_group_to_perm = relationship('UserRepoGroupToPerm', cascade='all', order_by='UserRepoGroupToPerm.group_to_perm_id')
    users_group_to_perm = relationship('UserGroupRepoGroupToPerm', cascade='all')
    parent_group = relationship('RepoGroup', remote_side=group_id)

    def __init__(self, group_name='', parent_group=None):
        self.group_name = group_name
        self.parent_group = parent_group

    def __unicode__(self):
        return u"<%s('%s:%s')>" % (self.__class__.__name__, self.group_id,
                                  self.group_name)

    @classmethod
    def url_sep(cls):
        return URL_SEP

    @classmethod
    def get_by_group_name(cls, group_name, cache=False, case_insensitive=False):
        if case_insensitive:
            gr = cls.query()\
                .filter(cls.group_name.ilike(group_name))
        else:
            gr = cls.query()\
                .filter(cls.group_name == group_name)
        if cache:
            gr = gr.options(FromCache(
                            "sql_cache_short",
                            "get_group_%s" % _hash_key(group_name)
                            )
            )
        return gr.scalar()


class Permission(Base, BaseModel):
    __tablename__ = 'permissions'
    __table_args__ = (
        Index('p_perm_name_idx', 'permission_name'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )
    PERMS = [
        ('repository.none', _('Repository no access')),
        ('repository.read', _('Repository read access')),
        ('repository.write', _('Repository write access')),
        ('repository.admin', _('Repository admin access')),

        ('group.none', _('Repositories Group no access')),
        ('group.read', _('Repositories Group read access')),
        ('group.write', _('Repositories Group write access')),
        ('group.admin', _('Repositories Group admin access')),

        ('hg.admin', _('RhodeCode Administrator')),
        ('hg.create.none', _('Repository creation disabled')),
        ('hg.create.repository', _('Repository creation enabled')),
        ('hg.fork.none', _('Repository forking disabled')),
        ('hg.fork.repository', _('Repository forking enabled')),
        ('hg.register.none', _('Register disabled')),
        ('hg.register.manual_activate', _('Register new user with RhodeCode '
                                          'with manual activation')),

        ('hg.register.auto_activate', _('Register new user with RhodeCode '
                                        'with auto activation')),
    ]

    # defines which permissions are more important higher the more important
    PERM_WEIGHTS = {
        'repository.none': 0,
        'repository.read': 1,
        'repository.write': 3,
        'repository.admin': 4,

        'group.none': 0,
        'group.read': 1,
        'group.write': 3,
        'group.admin': 4,

        'hg.fork.none': 0,
        'hg.fork.repository': 1,
        'hg.create.none': 0,
        'hg.create.repository':1
    }

    DEFAULT_USER_PERMISSIONS = [
        'repository.read',
        'group.read',
        'hg.create.repository',
        'hg.fork.repository',
        'hg.register.manual_activate',
    ]

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
         'mysql_charset': 'utf8'}
    )
    repo_to_perm_id = Column("repo_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=False, unique=None, default=None)

    user = relationship('User')
    repository = relationship('Repository')
    permission = relationship('Permission')

    def __unicode__(self):
        return u'<user:%s => %s >' % (self.user, self.repository)


class UserToPerm(Base, BaseModel):
    __tablename__ = 'user_to_perm'
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
    )
    user_to_perm_id = Column("user_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)

    user = relationship('User')
    permission = relationship('Permission', lazy='joined')


class UserGroupRepoToPerm(Base, BaseModel):
    __tablename__ = 'users_group_repo_to_perm'
    __table_args__ = (
        UniqueConstraint('repository_id', 'users_group_id', 'permission_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
    )
    users_group_to_perm_id = Column("users_group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_id = Column("users_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)
    repository_id = Column("repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=False, unique=None, default=None)

    users_group = relationship('UserGroup')
    permission = relationship('Permission')
    repository = relationship('Repository')

    def __unicode__(self):
        return u'<userGroup:%s => %s >' % (self.users_group, self.repository)


class UserGroupToPerm(Base, BaseModel):
    __tablename__ = 'users_group_to_perm'
    __table_args__ = (
        UniqueConstraint('users_group_id', 'permission_id',),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
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
         'mysql_charset': 'utf8'}
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
         'mysql_charset': 'utf8'}
    )

    users_group_repo_group_to_perm_id = Column("users_group_repo_group_to_perm_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    users_group_id = Column("users_group_id", Integer(), ForeignKey('users_groups.users_group_id'), nullable=False, unique=None, default=None)
    group_id = Column("group_id", Integer(), ForeignKey('groups.group_id'), nullable=False, unique=None, default=None)
    permission_id = Column("permission_id", Integer(), ForeignKey('permissions.permission_id'), nullable=False, unique=None, default=None)

    users_group = relationship('UserGroup')
    permission = relationship('Permission')
    group = relationship('RepoGroup')


class Statistics(Base, BaseModel):
    __tablename__ = 'statistics'
    __table_args__ = (
         UniqueConstraint('repository_id'),
         {'extend_existing': True, 'mysql_engine': 'InnoDB',
          'mysql_charset': 'utf8'}
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
         'mysql_charset': 'utf8'}
    )

    user_following_id = Column("user_following_id", Integer(), nullable=False, unique=True, default=None, primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None, default=None)
    follows_repo_id = Column("follows_repository_id", Integer(), ForeignKey('repositories.repo_id'), nullable=True, unique=None, default=None)
    follows_user_id = Column("follows_user_id", Integer(), ForeignKey('users.user_id'), nullable=True, unique=None, default=None)
    follows_from = Column('follows_from', DateTime(timezone=False), nullable=True, unique=None, default=datetime.datetime.now)

    user = relationship('User', primaryjoin='User.user_id==UserFollowing.user_id')

    follows_user = relationship('User', primaryjoin='User.user_id==UserFollowing.follows_user_id')
    follows_repository = relationship('Repository', order_by='Repository.repo_name')


class CacheInvalidation(Base, BaseModel):
    __tablename__ = 'cache_invalidation'
    __table_args__ = (
        UniqueConstraint('cache_key'),
        Index('key_idx', 'cache_key'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
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
         'mysql_charset': 'utf8'},
    )
    comment_id = Column('comment_id', Integer(), nullable=False, primary_key=True)
    repo_id = Column('repo_id', Integer(), ForeignKey('repositories.repo_id'), nullable=False)
    revision = Column('revision', String(40), nullable=True)
    pull_request_id = Column("pull_request_id", Integer(), ForeignKey('pull_requests.pull_request_id'), nullable=True)
    line_no = Column('line_no', Unicode(10), nullable=True)
    hl_lines = Column('hl_lines', Unicode(512), nullable=True)
    f_path = Column('f_path', Unicode(1000), nullable=True)
    user_id = Column('user_id', Integer(), ForeignKey('users.user_id'), nullable=False)
    text = Column('text', UnicodeText().with_variant(UnicodeText(25000), 'mysql'), nullable=False)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    modified_at = Column('modified_at', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)

    author = relationship('User', lazy='joined')
    repo = relationship('Repository')
    status_change = relationship('ChangesetStatus', cascade="all, delete, delete-orphan")
    pull_request = relationship('PullRequest', lazy='joined')

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


class ChangesetStatus(Base, BaseModel):
    __tablename__ = 'changeset_statuses'
    __table_args__ = (
        Index('cs_revision_idx', 'revision'),
        Index('cs_version_idx', 'version'),
        UniqueConstraint('repo_id', 'revision', 'version'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
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



class PullRequest(Base, BaseModel):
    __tablename__ = 'pull_requests'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )

    STATUS_NEW = u'new'
    STATUS_OPEN = u'open'
    STATUS_CLOSED = u'closed'

    pull_request_id = Column('pull_request_id', Integer(), nullable=False, primary_key=True)
    title = Column('title', Unicode(256), nullable=True)
    description = Column('description', UnicodeText().with_variant(UnicodeText(10240), 'mysql'), nullable=True)
    status = Column('status', Unicode(256), nullable=False, default=STATUS_NEW)
    created_on = Column('created_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    updated_on = Column('updated_on', DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=False, unique=None)
    _revisions = Column('revisions', UnicodeText().with_variant(UnicodeText(20500), 'mysql'))
    org_repo_id = Column('org_repo_id', Integer(), ForeignKey('repositories.repo_id'), nullable=False)
    org_ref = Column('org_ref', Unicode(256), nullable=False)
    other_repo_id = Column('other_repo_id', Integer(), ForeignKey('repositories.repo_id'), nullable=False)
    other_ref = Column('other_ref', Unicode(256), nullable=False)

    author = relationship('User', lazy='joined')
    reviewers = relationship('PullRequestReviewers',
                             cascade="all, delete, delete-orphan")
    org_repo = relationship('Repository', primaryjoin='PullRequest.org_repo_id==Repository.repo_id')
    other_repo = relationship('Repository', primaryjoin='PullRequest.other_repo_id==Repository.repo_id')
    statuses = relationship('ChangesetStatus')
    comments = relationship('ChangesetComment',
                             cascade="all, delete, delete-orphan")


class PullRequestReviewers(Base, BaseModel):
    __tablename__ = 'pull_request_reviewers'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )

    def __init__(self, user=None, pull_request=None):
        self.user = user
        self.pull_request = pull_request

    pull_requests_reviewers_id = Column('pull_requests_reviewers_id', Integer(), nullable=False, primary_key=True)
    pull_request_id = Column("pull_request_id", Integer(), ForeignKey('pull_requests.pull_request_id'), nullable=False)
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'), nullable=True)

    user = relationship('User')
    pull_request = relationship('PullRequest')


class Notification(Base, BaseModel):
    __tablename__ = 'notifications'
    __table_args__ = (
        Index('notification_type_idx', 'type'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
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
    type_ = Column('type', Unicode(256))

    created_by_user = relationship('User')
    notifications_to_users = relationship('UserNotification', lazy='joined',
                                          cascade="all, delete, delete-orphan")


class UserNotification(Base, BaseModel):
    __tablename__ = 'user_to_notification'
    __table_args__ = (
        UniqueConstraint('user_id', 'notification_id'),
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'}
    )
    user_id = Column('user_id', Integer(), ForeignKey('users.user_id'), primary_key=True)
    notification_id = Column("notification_id", Integer(), ForeignKey('notifications.notification_id'), primary_key=True)
    read = Column('read', Boolean, default=False)
    sent_on = Column('sent_on', DateTime(timezone=False), nullable=True, unique=None)

    user = relationship('User', lazy="joined")
    notification = relationship('Notification', lazy="joined",
                                order_by=lambda: Notification.created_on.desc(),)


class DbMigrateVersion(Base, BaseModel):
    __tablename__ = 'db_migrate_version'
    __table_args__ = (
        {'extend_existing': True, 'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8'},
    )
    repository_id = Column('repository_id', String(250), primary_key=True)
    repository_path = Column('repository_path', Text)
    version = Column('version', Integer)
