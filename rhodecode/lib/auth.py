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
authentication and permission libraries
"""

import inspect
import collections
import fnmatch
import hashlib
import itertools
import logging
import os
import random
import time
import traceback
from functools import wraps

import ipaddress
from pylons import url, request
from pylons.controllers.util import abort, redirect
from pylons.i18n.translation import _
from sqlalchemy import or_
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm import joinedload
from zope.cachedescriptors.property import Lazy as LazyProperty

import rhodecode
from rhodecode.model import meta
from rhodecode.model.meta import Session
from rhodecode.model.user import UserModel
from rhodecode.model.db import (
    User, Repository, Permission, UserToPerm, UserGroupToPerm, UserGroupMember,
    UserIpMap, UserApiKeys)
from rhodecode.lib import caches
from rhodecode.lib.utils2 import safe_unicode, aslist, safe_str, md5
from rhodecode.lib.utils import (
    get_repo_slug, get_repo_group_slug, get_user_group_slug)
from rhodecode.lib.caching_query import FromCache


if rhodecode.is_unix:
    import bcrypt

log = logging.getLogger(__name__)

csrf_token_key = "csrf_token"


class PasswordGenerator(object):
    """
    This is a simple class for generating password from different sets of
    characters
    usage::

        passwd_gen = PasswordGenerator()
        #print 8-letter password containing only big and small letters
            of alphabet
        passwd_gen.gen_password(8, passwd_gen.ALPHABETS_BIG_SMALL)
    """
    ALPHABETS_NUM = r'''1234567890'''
    ALPHABETS_SMALL = r'''qwertyuiopasdfghjklzxcvbnm'''
    ALPHABETS_BIG = r'''QWERTYUIOPASDFGHJKLZXCVBNM'''
    ALPHABETS_SPECIAL = r'''`-=[]\;',./~!@#$%^&*()_+{}|:"<>?'''
    ALPHABETS_FULL = ALPHABETS_BIG + ALPHABETS_SMALL \
        + ALPHABETS_NUM + ALPHABETS_SPECIAL
    ALPHABETS_ALPHANUM = ALPHABETS_BIG + ALPHABETS_SMALL + ALPHABETS_NUM
    ALPHABETS_BIG_SMALL = ALPHABETS_BIG + ALPHABETS_SMALL
    ALPHABETS_ALPHANUM_BIG = ALPHABETS_BIG + ALPHABETS_NUM
    ALPHABETS_ALPHANUM_SMALL = ALPHABETS_SMALL + ALPHABETS_NUM

    def __init__(self, passwd=''):
        self.passwd = passwd

    def gen_password(self, length, type_=None):
        if type_ is None:
            type_ = self.ALPHABETS_FULL
        self.passwd = ''.join([random.choice(type_) for _ in xrange(length)])
        return self.passwd


class _RhodeCodeCryptoBase(object):

    def hash_create(self, str_):
        """
        hash the string using

        :param str_: password to hash
        """
        raise NotImplementedError

    def hash_check_with_upgrade(self, password, hashed):
        """
        Returns tuple in which first element is boolean that states that
        given password matches it's hashed version, and the second is new hash
        of the password, in case this password should be migrated to new
        cipher.
        """
        checked_hash = self.hash_check(password, hashed)
        return checked_hash, None

    def hash_check(self, password, hashed):
        """
        Checks matching password with it's hashed value.

        :param password: password
        :param hashed: password in hashed form
        """
        raise NotImplementedError

    def _assert_bytes(self, value):
        """
        Passing in an `unicode` object can lead to hard to detect issues
        if passwords contain non-ascii characters.  Doing a type check
        during runtime, so that such mistakes are detected early on.
        """
        if not isinstance(value, str):
            raise TypeError(
                "Bytestring required as input, got %r." % (value, ))


class _RhodeCodeCryptoBCrypt(_RhodeCodeCryptoBase):

    def hash_create(self, str_):
        self._assert_bytes(str_)
        return bcrypt.hashpw(str_, bcrypt.gensalt(10))

    def hash_check_with_upgrade(self, password, hashed):
        """
        Returns tuple in which first element is boolean that states that
        given password matches it's hashed version, and the second is new hash
        of the password, in case this password should be migrated to new
        cipher.

        This implements special upgrade logic which works like that:
         - check if the given password == bcrypted hash, if yes then we
           properly used password and it was already in bcrypt. Proceed
           without any changes
         - if bcrypt hash check is not working try with sha256. If hash compare
           is ok, it means we using correct but old hashed password. indicate
           hash change and proceed
        """

        new_hash = None

        # regular pw check
        password_match_bcrypt = self.hash_check(password, hashed)

        # now we want to know if the password was maybe from sha256
        # basically calling _RhodeCodeCryptoSha256().hash_check()
        if not password_match_bcrypt:
            if _RhodeCodeCryptoSha256().hash_check(password, hashed):
                new_hash = self.hash_create(password)  # make new bcrypt hash
                password_match_bcrypt = True

        return password_match_bcrypt, new_hash

    def hash_check(self, password, hashed):
        """
        Checks matching password with it's hashed value.

        :param password: password
        :param hashed: password in hashed form
        """
        self._assert_bytes(password)
        try:
            return bcrypt.hashpw(password, hashed) == hashed
        except ValueError as e:
            # we're having a invalid salt here probably, we should not crash
            # just return with False as it would be a wrong password.
            log.debug('Failed to check password hash using bcrypt %s',
                      safe_str(e))

        return False


class _RhodeCodeCryptoSha256(_RhodeCodeCryptoBase):

    def hash_create(self, str_):
        self._assert_bytes(str_)
        return hashlib.sha256(str_).hexdigest()

    def hash_check(self, password, hashed):
        """
        Checks matching password with it's hashed value.

        :param password: password
        :param hashed: password in hashed form
        """
        self._assert_bytes(password)
        return hashlib.sha256(password).hexdigest() == hashed


class _RhodeCodeCryptoMd5(_RhodeCodeCryptoBase):

    def hash_create(self, str_):
        self._assert_bytes(str_)
        return hashlib.md5(str_).hexdigest()

    def hash_check(self, password, hashed):
        """
        Checks matching password with it's hashed value.

        :param password: password
        :param hashed: password in hashed form
        """
        self._assert_bytes(password)
        return hashlib.md5(password).hexdigest() == hashed


def crypto_backend():
    """
    Return the matching crypto backend.

    Selection is based on if we run tests or not, we pick md5 backend to run
    tests faster since BCRYPT is expensive to calculate
    """
    if rhodecode.is_test:
        RhodeCodeCrypto = _RhodeCodeCryptoMd5()
    else:
        RhodeCodeCrypto = _RhodeCodeCryptoBCrypt()

    return RhodeCodeCrypto


def get_crypt_password(password):
    """
    Create the hash of `password` with the active crypto backend.

    :param password: The cleartext password.
    :type password: unicode
    """
    password = safe_str(password)
    return crypto_backend().hash_create(password)


def check_password(password, hashed):
    """
    Check if the value in `password` matches the hash in `hashed`.

    :param password: The cleartext password.
    :type password: unicode

    :param hashed: The expected hashed version of the password.
    :type hashed: The hash has to be passed in in text representation.
    """
    password = safe_str(password)
    return crypto_backend().hash_check(password, hashed)


def generate_auth_token(data, salt=None):
    """
    Generates API KEY from given string
    """

    if salt is None:
        salt = os.urandom(16)
    return hashlib.sha1(safe_str(data) + salt).hexdigest()


class CookieStoreWrapper(object):

    def __init__(self, cookie_store):
        self.cookie_store = cookie_store

    def __repr__(self):
        return 'CookieStore<%s>' % (self.cookie_store)

    def get(self, key, other=None):
        if isinstance(self.cookie_store, dict):
            return self.cookie_store.get(key, other)
        elif isinstance(self.cookie_store, AuthUser):
            return self.cookie_store.__dict__.get(key, other)


def _cached_perms_data(user_id, scope, user_is_admin,
                       user_inherit_default_permissions, explicit, algo):

    permissions = PermissionCalculator(
        user_id, scope, user_is_admin, user_inherit_default_permissions,
        explicit, algo)
    return permissions.calculate()


class PermissionCalculator(object):

    def __init__(
            self, user_id, scope, user_is_admin,
            user_inherit_default_permissions, explicit, algo):
        self.user_id = user_id
        self.user_is_admin = user_is_admin
        self.inherit_default_permissions = user_inherit_default_permissions
        self.explicit = explicit
        self.algo = algo

        scope = scope or {}
        self.scope_repo_id = scope.get('repo_id')
        self.scope_repo_group_id = scope.get('repo_group_id')
        self.scope_user_group_id = scope.get('user_group_id')

        self.default_user_id = User.get_default_user(cache=True).user_id

        self.permissions_repositories = {}
        self.permissions_repository_groups = {}
        self.permissions_user_groups = {}
        self.permissions_global = set()

        self.default_repo_perms = Permission.get_default_repo_perms(
            self.default_user_id, self.scope_repo_id)
        self.default_repo_groups_perms = Permission.get_default_group_perms(
            self.default_user_id, self.scope_repo_group_id)
        self.default_user_group_perms = \
            Permission.get_default_user_group_perms(
                self.default_user_id, self.scope_user_group_id)

    def calculate(self):
        if self.user_is_admin:
            return self._admin_permissions()

        self._calculate_global_default_permissions()
        self._calculate_global_permissions()
        self._calculate_default_permissions()
        self._calculate_repository_permissions()
        self._calculate_repository_group_permissions()
        self._calculate_user_group_permissions()
        return self._permission_structure()

    def _admin_permissions(self):
        """
        admin user have all default rights for repositories
        and groups set to admin
        """
        self.permissions_global.add('hg.admin')
        self.permissions_global.add('hg.create.write_on_repogroup.true')

        # repositories
        for perm in self.default_repo_perms:
            r_k = perm.UserRepoToPerm.repository.repo_name
            p = 'repository.admin'
            self.permissions_repositories[r_k] = p

        # repository groups
        for perm in self.default_repo_groups_perms:
            rg_k = perm.UserRepoGroupToPerm.group.group_name
            p = 'group.admin'
            self.permissions_repository_groups[rg_k] = p

        # user groups
        for perm in self.default_user_group_perms:
            u_k = perm.UserUserGroupToPerm.user_group.users_group_name
            p = 'usergroup.admin'
            self.permissions_user_groups[u_k] = p

        return self._permission_structure()

    def _calculate_global_default_permissions(self):
        """
        global permissions taken from the default user
        """
        default_global_perms = UserToPerm.query()\
            .filter(UserToPerm.user_id == self.default_user_id)\
            .options(joinedload(UserToPerm.permission))

        for perm in default_global_perms:
            self.permissions_global.add(perm.permission.permission_name)

    def _calculate_global_permissions(self):
        """
        Set global system permissions with user permissions or permissions
        taken from the user groups of the current user.

        The permissions include repo creating, repo group creating, forking
        etc.
        """

        # now we read the defined permissions and overwrite what we have set
        # before those can be configured from groups or users explicitly.

        # TODO: johbo: This seems to be out of sync, find out the reason
        # for the comment below and update it.

        # In case we want to extend this list we should be always in sync with
        # User.DEFAULT_USER_PERMISSIONS definitions
        _configurable = frozenset([
            'hg.fork.none', 'hg.fork.repository',
            'hg.create.none', 'hg.create.repository',
            'hg.usergroup.create.false', 'hg.usergroup.create.true',
            'hg.repogroup.create.false', 'hg.repogroup.create.true',
            'hg.create.write_on_repogroup.false',
            'hg.create.write_on_repogroup.true',
            'hg.inherit_default_perms.false', 'hg.inherit_default_perms.true'
        ])

        # USER GROUPS comes first user group global permissions
        user_perms_from_users_groups = Session().query(UserGroupToPerm)\
            .options(joinedload(UserGroupToPerm.permission))\
            .join((UserGroupMember, UserGroupToPerm.users_group_id ==
                   UserGroupMember.users_group_id))\
            .filter(UserGroupMember.user_id == self.user_id)\
            .order_by(UserGroupToPerm.users_group_id)\
            .all()

        # need to group here by groups since user can be in more than
        # one group, so we get all groups
        _explicit_grouped_perms = [
            [x, list(y)] for x, y in
            itertools.groupby(user_perms_from_users_groups,
                              lambda _x: _x.users_group)]

        for gr, perms in _explicit_grouped_perms:
            # since user can be in multiple groups iterate over them and
            # select the lowest permissions first (more explicit)
            # TODO: marcink: do this^^

            # group doesn't inherit default permissions so we actually set them
            if not gr.inherit_default_permissions:
                # NEED TO IGNORE all previously set configurable permissions
                # and replace them with explicitly set from this user
                # group permissions
                self.permissions_global = self.permissions_global.difference(
                    _configurable)
                for perm in perms:
                    self.permissions_global.add(
                        perm.permission.permission_name)

        # user explicit global permissions
        user_perms = Session().query(UserToPerm)\
            .options(joinedload(UserToPerm.permission))\
            .filter(UserToPerm.user_id == self.user_id).all()

        if not self.inherit_default_permissions:
            # NEED TO IGNORE all configurable permissions and
            # replace them with explicitly set from this user permissions
            self.permissions_global = self.permissions_global.difference(
                _configurable)
            for perm in user_perms:
                self.permissions_global.add(perm.permission.permission_name)

    def _calculate_default_permissions(self):
        """
        Set default user permissions for repositories, repository groups
        taken from the default user.

        Calculate inheritance of object permissions based on what we have now
        in GLOBAL permissions. We check if .false is in GLOBAL since this is
        explicitly set. Inherit is the opposite of .false being there.

        .. note::

           the syntax is little bit odd but what we need to check here is
           the opposite of .false permission being in the list so even for
           inconsistent state when both .true/.false is there
           .false is more important

        """
        user_inherit_object_permissions = not ('hg.inherit_default_perms.false'
                                               in self.permissions_global)

        # defaults for repositories, taken from `default` user permissions
        # on given repo
        for perm in self.default_repo_perms:
            r_k = perm.UserRepoToPerm.repository.repo_name
            if perm.Repository.private and not (
                    perm.Repository.user_id == self.user_id):
                # disable defaults for private repos,
                p = 'repository.none'
            elif perm.Repository.user_id == self.user_id:
                # set admin if owner
                p = 'repository.admin'
            else:
                p = perm.Permission.permission_name
                # if we decide this user isn't inheriting permissions from
                # default user we set him to .none so only explicit
                # permissions work
                if not user_inherit_object_permissions:
                    p = 'repository.none'
            self.permissions_repositories[r_k] = p

        # defaults for repository groups taken from `default` user permission
        # on given group
        for perm in self.default_repo_groups_perms:
            rg_k = perm.UserRepoGroupToPerm.group.group_name
            if perm.RepoGroup.user_id == self.user_id:
                # set admin if owner
                p = 'group.admin'
            else:
                p = perm.Permission.permission_name

            # if we decide this user isn't inheriting permissions from default
            # user we set him to .none so only explicit permissions work
            if not user_inherit_object_permissions:
                p = 'group.none'
            self.permissions_repository_groups[rg_k] = p

        # defaults for user groups taken from `default` user permission
        # on given user group
        for perm in self.default_user_group_perms:
            u_k = perm.UserUserGroupToPerm.user_group.users_group_name
            p = perm.Permission.permission_name
            # if we decide this user isn't inheriting permissions from default
            # user we set him to .none so only explicit permissions work
            if not user_inherit_object_permissions:
                p = 'usergroup.none'
            self.permissions_user_groups[u_k] = p

    def _calculate_repository_permissions(self):
        """
        Repository permissions for the current user.

        Check if the user is part of user groups for this repository and
        fill in the permission from it. `_choose_permission` decides of which
        permission should be selected based on selected method.
        """

        # user group for repositories permissions
        user_repo_perms_from_user_group = Permission\
            .get_default_repo_perms_from_user_group(
                self.user_id, self.scope_repo_id)

        multiple_counter = collections.defaultdict(int)
        for perm in user_repo_perms_from_user_group:
            r_k = perm.UserGroupRepoToPerm.repository.repo_name
            multiple_counter[r_k] += 1
            p = perm.Permission.permission_name

            if perm.Repository.user_id == self.user_id:
                # set admin if owner
                p = 'repository.admin'
            else:
                if multiple_counter[r_k] > 1:
                    cur_perm = self.permissions_repositories[r_k]
                    p = self._choose_permission(p, cur_perm)
            self.permissions_repositories[r_k] = p

        # user explicit permissions for repositories, overrides any specified
        # by the group permission
        user_repo_perms = Permission.get_default_repo_perms(
            self.user_id, self.scope_repo_id)
        for perm in user_repo_perms:
            r_k = perm.UserRepoToPerm.repository.repo_name
            # set admin if owner
            if perm.Repository.user_id == self.user_id:
                p = 'repository.admin'
            else:
                p = perm.Permission.permission_name
                if not self.explicit:
                    cur_perm = self.permissions_repositories.get(
                        r_k, 'repository.none')
                    p = self._choose_permission(p, cur_perm)
            self.permissions_repositories[r_k] = p

    def _calculate_repository_group_permissions(self):
        """
        Repository group permissions for the current user.

        Check if the user is part of user groups for repository groups and
        fill in the permissions from it. `_choose_permmission` decides of which
        permission should be selected based on selected method.
        """
        # user group for repo groups permissions
        user_repo_group_perms_from_user_group = Permission\
            .get_default_group_perms_from_user_group(
                self.user_id, self.scope_repo_group_id)

        multiple_counter = collections.defaultdict(int)
        for perm in user_repo_group_perms_from_user_group:
            g_k = perm.UserGroupRepoGroupToPerm.group.group_name
            multiple_counter[g_k] += 1
            p = perm.Permission.permission_name
            if perm.RepoGroup.user_id == self.user_id:
                # set admin if owner
                p = 'group.admin'
            else:
                if multiple_counter[g_k] > 1:
                    cur_perm = self.permissions_repository_groups[g_k]
                    p = self._choose_permission(p, cur_perm)
            self.permissions_repository_groups[g_k] = p

        # user explicit permissions for repository groups
        user_repo_groups_perms = Permission.get_default_group_perms(
            self.user_id, self.scope_repo_group_id)
        for perm in user_repo_groups_perms:
            rg_k = perm.UserRepoGroupToPerm.group.group_name
            if perm.RepoGroup.user_id == self.user_id:
                # set admin if owner
                p = 'group.admin'
            else:
                p = perm.Permission.permission_name
                if not self.explicit:
                    cur_perm = self.permissions_repository_groups.get(
                        rg_k, 'group.none')
                    p = self._choose_permission(p, cur_perm)
            self.permissions_repository_groups[rg_k] = p

    def _calculate_user_group_permissions(self):
        """
        User group permissions for the current user.
        """
        # user group for user group permissions
        user_group_from_user_group = Permission\
            .get_default_user_group_perms_from_user_group(
                self.user_id, self.scope_repo_group_id)

        multiple_counter = collections.defaultdict(int)
        for perm in user_group_from_user_group:
            g_k = perm.UserGroupUserGroupToPerm\
                .target_user_group.users_group_name
            multiple_counter[g_k] += 1
            p = perm.Permission.permission_name
            if multiple_counter[g_k] > 1:
                cur_perm = self.permissions_user_groups[g_k]
                p = self._choose_permission(p, cur_perm)
            self.permissions_user_groups[g_k] = p

        # user explicit permission for user groups
        user_user_groups_perms = Permission.get_default_user_group_perms(
            self.user_id, self.scope_user_group_id)
        for perm in user_user_groups_perms:
            u_k = perm.UserUserGroupToPerm.user_group.users_group_name
            p = perm.Permission.permission_name
            if not self.explicit:
                cur_perm = self.permissions_user_groups.get(
                    u_k, 'usergroup.none')
                p = self._choose_permission(p, cur_perm)
            self.permissions_user_groups[u_k] = p

    def _choose_permission(self, new_perm, cur_perm):
        new_perm_val = Permission.PERM_WEIGHTS[new_perm]
        cur_perm_val = Permission.PERM_WEIGHTS[cur_perm]
        if self.algo == 'higherwin':
            if new_perm_val > cur_perm_val:
                return new_perm
            return cur_perm
        elif self.algo == 'lowerwin':
            if new_perm_val < cur_perm_val:
                return new_perm
            return cur_perm

    def _permission_structure(self):
        return {
            'global': self.permissions_global,
            'repositories': self.permissions_repositories,
            'repositories_groups': self.permissions_repository_groups,
            'user_groups': self.permissions_user_groups,
        }


def allowed_auth_token_access(controller_name, whitelist=None, auth_token=None):
    """
    Check if given controller_name is in whitelist of auth token access
    """
    if not whitelist:
        from rhodecode import CONFIG
        whitelist = aslist(
            CONFIG.get('api_access_controllers_whitelist'), sep=',')
        log.debug(
            'Allowed controllers for AUTH TOKEN access: %s' % (whitelist,))

    auth_token_access_valid = False
    for entry in whitelist:
        if fnmatch.fnmatch(controller_name, entry):
            auth_token_access_valid = True
            break

    if auth_token_access_valid:
        log.debug('controller:%s matches entry in whitelist'
                  % (controller_name,))
    else:
        msg = ('controller: %s does *NOT* match any entry in whitelist'
               % (controller_name,))
        if auth_token:
            # if we use auth token key and don't have access it's a warning
            log.warning(msg)
        else:
            log.debug(msg)

    return auth_token_access_valid


class AuthUser(object):
    """
    A simple object that handles all attributes of user in RhodeCode

    It does lookup based on API key,given user, or user present in session
    Then it fills all required information for such user. It also checks if
    anonymous access is enabled and if so, it returns default user as logged in
    """
    GLOBAL_PERMS = [x[0] for x in Permission.PERMS]

    def __init__(self, user_id=None, api_key=None, username=None, ip_addr=None):

        self.user_id = user_id
        self._api_key = api_key

        self.api_key = None
        self.feed_token = ''
        self.username = username
        self.ip_addr = ip_addr
        self.name = ''
        self.lastname = ''
        self.email = ''
        self.is_authenticated = False
        self.admin = False
        self.inherit_default_permissions = False
        self.password = ''

        self.anonymous_user = None  # propagated on propagate_data
        self.propagate_data()
        self._instance = None
        self._permissions_scoped_cache = {}  # used to bind scoped calculation

    @LazyProperty
    def permissions(self):
        return self.get_perms(user=self, cache=False)

    def permissions_with_scope(self, scope):
        """
        Call the get_perms function with scoped data. The scope in that function
        narrows the SQL calls to the given ID of objects resulting in fetching
        Just particular permission we want to obtain. If scope is an empty dict
        then it basically narrows the scope to GLOBAL permissions only.

        :param scope: dict
        """
        if 'repo_name' in scope:
            obj = Repository.get_by_repo_name(scope['repo_name'])
            if obj:
                scope['repo_id'] = obj.repo_id
        _scope = {
            'repo_id': -1,
            'user_group_id': -1,
            'repo_group_id': -1,
        }
        _scope.update(scope)
        cache_key = "_".join(map(safe_str, reduce(lambda a, b: a+b,
                                                  _scope.items())))
        if cache_key not in self._permissions_scoped_cache:
            # store in cache to mimic how the @LazyProperty works,
            # the difference here is that we use the unique key calculated
            # from params and values
            res = self.get_perms(user=self, cache=False, scope=_scope)
            self._permissions_scoped_cache[cache_key] = res
        return self._permissions_scoped_cache[cache_key]

    @property
    def auth_tokens(self):
        return self.get_auth_tokens()

    def get_instance(self):
        return User.get(self.user_id)

    def update_lastactivity(self):
        if self.user_id:
            User.get(self.user_id).update_lastactivity()

    def propagate_data(self):
        """
        Fills in user data and propagates values to this instance. Maps fetched
        user attributes to this class instance attributes
        """

        user_model = UserModel()
        anon_user = self.anonymous_user = User.get_default_user(cache=True)
        is_user_loaded = False

        # lookup by userid
        if self.user_id is not None and self.user_id != anon_user.user_id:
            log.debug('Trying Auth User lookup by USER ID %s' % self.user_id)
            is_user_loaded = user_model.fill_data(self, user_id=self.user_id)

        # try go get user by api key
        elif self._api_key and self._api_key != anon_user.api_key:
            log.debug('Trying Auth User lookup by API KEY %s' % self._api_key)
            is_user_loaded = user_model.fill_data(self, api_key=self._api_key)

        # lookup by username
        elif self.username:
            log.debug('Trying Auth User lookup by USER NAME %s' % self.username)
            is_user_loaded = user_model.fill_data(self, username=self.username)
        else:
            log.debug('No data in %s that could been used to log in' % self)

        if not is_user_loaded:
            log.debug('Failed to load user. Fallback to default user')
            # if we cannot authenticate user try anonymous
            if anon_user.active:
                user_model.fill_data(self, user_id=anon_user.user_id)
                # then we set this user is logged in
                self.is_authenticated = True
            else:
                # in case of disabled anonymous user we reset some of the
                # parameters so such user is "corrupted", skipping the fill_data
                for attr in ['user_id', 'username', 'admin', 'active']:
                    setattr(self, attr, None)
                self.is_authenticated = False

        if not self.username:
            self.username = 'None'

        log.debug('Auth User is now %s' % self)

    def get_perms(self, user, scope=None, explicit=True, algo='higherwin',
                  cache=False):
        """
        Fills user permission attribute with permissions taken from database
        works for permissions given for repositories, and for permissions that
        are granted to groups

        :param user: instance of User object from database
        :param explicit: In case there are permissions both for user and a group
            that user is part of, explicit flag will defiine if user will
            explicitly override permissions from group, if it's False it will
            make decision based on the algo
        :param algo: algorithm to decide what permission should be choose if
            it's multiple defined, eg user in two different groups. It also
            decides if explicit flag is turned off how to specify the permission
            for case when user is in a group + have defined separate permission
        """
        user_id = user.user_id
        user_is_admin = user.is_admin

        # inheritance of global permissions like create repo/fork repo etc
        user_inherit_default_permissions = user.inherit_default_permissions

        log.debug('Computing PERMISSION tree for scope %s' % (scope, ))
        compute = caches.conditional_cache(
            'short_term', 'cache_desc',
            condition=cache, func=_cached_perms_data)
        result = compute(user_id, scope, user_is_admin,
                         user_inherit_default_permissions, explicit, algo)

        result_repr = []
        for k in result:
            result_repr.append((k, len(result[k])))

        log.debug('PERMISSION tree computed %s' % (result_repr,))
        return result

    def get_auth_tokens(self):
        auth_tokens = [self.api_key]
        for api_key in UserApiKeys.query()\
                .filter(UserApiKeys.user_id == self.user_id)\
                .filter(or_(UserApiKeys.expires == -1,
                            UserApiKeys.expires >= time.time())).all():
            auth_tokens.append(api_key.api_key)

        return auth_tokens

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_user_object(self):
        return self.user_id is not None

    @property
    def repositories_admin(self):
        """
        Returns list of repositories you're an admin of
        """
        return [x[0] for x in self.permissions['repositories'].iteritems()
                if x[1] == 'repository.admin']

    @property
    def repository_groups_admin(self):
        """
        Returns list of repository groups you're an admin of
        """
        return [x[0]
                for x in self.permissions['repositories_groups'].iteritems()
                if x[1] == 'group.admin']

    @property
    def user_groups_admin(self):
        """
        Returns list of user groups you're an admin of
        """
        return [x[0] for x in self.permissions['user_groups'].iteritems()
                if x[1] == 'usergroup.admin']

    @property
    def ip_allowed(self):
        """
        Checks if ip_addr used in constructor is allowed from defined list of
        allowed ip_addresses for user

        :returns: boolean, True if ip is in allowed ip range
        """
        # check IP
        inherit = self.inherit_default_permissions
        return AuthUser.check_ip_allowed(self.user_id, self.ip_addr,
                                         inherit_from_default=inherit)

    @classmethod
    def check_ip_allowed(cls, user_id, ip_addr, inherit_from_default):
        allowed_ips = AuthUser.get_allowed_ips(
            user_id, cache=True, inherit_from_default=inherit_from_default)
        if check_ip_access(source_ip=ip_addr, allowed_ips=allowed_ips):
            log.debug('IP:%s is in range of %s' % (ip_addr, allowed_ips))
            return True
        else:
            log.info('Access for IP:%s forbidden, '
                     'not in %s' % (ip_addr, allowed_ips))
            return False

    def __repr__(self):
        return "<AuthUser('id:%s[%s] ip:%s auth:%s')>"\
            % (self.user_id, self.username, self.ip_addr, self.is_authenticated)

    def set_authenticated(self, authenticated=True):
        if self.user_id != self.anonymous_user.user_id:
            self.is_authenticated = authenticated

    def get_cookie_store(self):
        return {
            'username': self.username,
            'password': md5(self.password),
            'user_id': self.user_id,
            'is_authenticated': self.is_authenticated
        }

    @classmethod
    def from_cookie_store(cls, cookie_store):
        """
        Creates AuthUser from a cookie store

        :param cls:
        :param cookie_store:
        """
        user_id = cookie_store.get('user_id')
        username = cookie_store.get('username')
        api_key = cookie_store.get('api_key')
        return AuthUser(user_id, api_key, username)

    @classmethod
    def get_allowed_ips(cls, user_id, cache=False, inherit_from_default=False):
        _set = set()

        if inherit_from_default:
            default_ips = UserIpMap.query().filter(
                UserIpMap.user == User.get_default_user(cache=True))
            if cache:
                default_ips = default_ips.options(FromCache("sql_cache_short",
                                                  "get_user_ips_default"))

            # populate from default user
            for ip in default_ips:
                try:
                    _set.add(ip.ip_addr)
                except ObjectDeletedError:
                    # since we use heavy caching sometimes it happens that
                    # we get deleted objects here, we just skip them
                    pass

        user_ips = UserIpMap.query().filter(UserIpMap.user_id == user_id)
        if cache:
            user_ips = user_ips.options(FromCache("sql_cache_short",
                                                  "get_user_ips_%s" % user_id))

        for ip in user_ips:
            try:
                _set.add(ip.ip_addr)
            except ObjectDeletedError:
                # since we use heavy caching sometimes it happens that we get
                # deleted objects here, we just skip them
                pass
        return _set or set(['0.0.0.0/0', '::/0'])


def set_available_permissions(config):
    """
    This function will propagate pylons globals with all available defined
    permission given in db. We don't want to check each time from db for new
    permissions since adding a new permission also requires application restart
    ie. to decorate new views with the newly created permission

    :param config: current pylons config instance

    """
    log.info('getting information about all available permissions')
    try:
        sa = meta.Session
        all_perms = sa.query(Permission).all()
        config['available_permissions'] = [x.permission_name for x in all_perms]
    except Exception:
        log.error(traceback.format_exc())
    finally:
        meta.Session.remove()


def get_csrf_token(session=None, force_new=False, save_if_missing=True):
    """
    Return the current authentication token, creating one if one doesn't
    already exist and the save_if_missing flag is present.

    :param session: pass in the pylons session, else we use the global ones
    :param force_new: force to re-generate the token and store it in session
    :param save_if_missing: save the newly generated token if it's missing in
        session
    """
    if not session:
        from pylons import session

    if (csrf_token_key not in session and save_if_missing) or force_new:
        token = hashlib.sha1(str(random.getrandbits(128))).hexdigest()
        session[csrf_token_key] = token
        if hasattr(session, 'save'):
            session.save()
    return session.get(csrf_token_key)


# CHECK DECORATORS
class CSRFRequired(object):
    """
    Decorator for authenticating a form

    This decorator uses an authorization token stored in the client's
    session for prevention of certain Cross-site request forgery (CSRF)
    attacks (See
    http://en.wikipedia.org/wiki/Cross-site_request_forgery for more
    information).

    For use with the ``webhelpers.secure_form`` helper functions.

    """
    def __init__(self, token=csrf_token_key, header='X-CSRF-Token'):
        self.token = token
        self.header = header

    def __call__(self, func):
        return get_cython_compat_decorator(self.__wrapper, func)

    def _get_csrf(self, _request):
        return _request.POST.get(self.token, _request.headers.get(self.header))

    def check_csrf(self, _request, cur_token):
        supplied_token = self._get_csrf(_request)
        return supplied_token and supplied_token == cur_token

    def __wrapper(self, func, *fargs, **fkwargs):
        cur_token = get_csrf_token(save_if_missing=False)
        if self.check_csrf(request, cur_token):
            if request.POST.get(self.token):
                del request.POST[self.token]
            return func(*fargs, **fkwargs)
        else:
            reason = 'token-missing'
            supplied_token = self._get_csrf(request)
            if supplied_token and cur_token != supplied_token:
                reason = 'token-mismatch [%s:%s]' % (cur_token or ''[:6],
                                                     supplied_token or ''[:6])

            csrf_message = \
                ("Cross-site request forgery detected, request denied. See "
                 "http://en.wikipedia.org/wiki/Cross-site_request_forgery for "
                 "more information.")
        log.warn('Cross-site request forgery detected, request %r DENIED: %s '
                 'REMOTE_ADDR:%s, HEADERS:%s' % (
                     request, reason, request.remote_addr, request.headers))

        abort(403, detail=csrf_message)


class LoginRequired(object):
    """
    Must be logged in to execute this function else
    redirect to login page

    :param api_access: if enabled this checks only for valid auth token
        and grants access based on valid token
    """
    def __init__(self, auth_token_access=False):
        self.auth_token_access = auth_token_access

    def __call__(self, func):
        return get_cython_compat_decorator(self.__wrapper, func)

    def __wrapper(self, func, *fargs, **fkwargs):
        cls = fargs[0]
        user = cls._rhodecode_user
        loc = "%s:%s" % (cls.__class__.__name__, func.__name__)
        log.debug('Starting login restriction checks for user: %s' % (user,))
        # check if our IP is allowed
        ip_access_valid = True
        if not user.ip_allowed:
            from rhodecode.lib import helpers as h
            h.flash(h.literal(_('IP %s not allowed' % (user.ip_addr,))),
                    category='warning')
            ip_access_valid = False

        # check if we used an APIKEY and it's a valid one
        # defined whitelist of controllers which API access will be enabled
        _auth_token = request.GET.get(
            'auth_token', '') or request.GET.get('api_key', '')
        auth_token_access_valid = allowed_auth_token_access(
            loc, auth_token=_auth_token)

        # explicit controller is enabled or API is in our whitelist
        if self.auth_token_access or auth_token_access_valid:
            log.debug('Checking AUTH TOKEN access for %s' % (cls,))

            if _auth_token and _auth_token in user.auth_tokens:
                auth_token_access_valid = True
                log.debug('AUTH TOKEN ****%s is VALID' % (_auth_token[-4:],))
            else:
                auth_token_access_valid = False
                if not _auth_token:
                    log.debug("AUTH TOKEN *NOT* present in request")
                else:
                    log.warning(
                        "AUTH TOKEN ****%s *NOT* valid" % _auth_token[-4:])

        log.debug('Checking if %s is authenticated @ %s' % (user.username, loc))
        reason = 'RHODECODE_AUTH' if user.is_authenticated \
            else 'AUTH_TOKEN_AUTH'

        if ip_access_valid and (
                user.is_authenticated or auth_token_access_valid):
            log.info(
                'user %s authenticating with:%s IS authenticated on func %s'
                % (user, reason, loc))

            # update user data to check last activity
            user.update_lastactivity()
            Session().commit()
            return func(*fargs, **fkwargs)
        else:
            log.warning(
                'user %s authenticating with:%s NOT authenticated on '
                'func: %s: IP_ACCESS:%s AUTH_TOKEN_ACCESS:%s'
                % (user, reason, loc, ip_access_valid,
                   auth_token_access_valid))
            # we preserve the get PARAM
            came_from = request.path_qs

            log.debug('redirecting to login page with %s' % (came_from,))
            return redirect(
                url('login_home', came_from=came_from))


class NotAnonymous(object):
    """
    Must be logged in to execute this function else
    redirect to login page"""

    def __call__(self, func):
        return get_cython_compat_decorator(self.__wrapper, func)

    def __wrapper(self, func, *fargs, **fkwargs):
        cls = fargs[0]
        self.user = cls._rhodecode_user

        log.debug('Checking if user is not anonymous @%s' % cls)

        anonymous = self.user.username == User.DEFAULT_USER

        if anonymous:
            came_from = request.path_qs

            import rhodecode.lib.helpers as h
            h.flash(_('You need to be a registered user to '
                      'perform this action'),
                    category='warning')
            return redirect(url('login_home', came_from=came_from))
        else:
            return func(*fargs, **fkwargs)


class XHRRequired(object):
    def __call__(self, func):
        return get_cython_compat_decorator(self.__wrapper, func)

    def __wrapper(self, func, *fargs, **fkwargs):
        log.debug('Checking if request is XMLHttpRequest (XHR)')
        xhr_message = 'This is not a valid XMLHttpRequest (XHR) request'
        if not request.is_xhr:
            abort(400, detail=xhr_message)

        return func(*fargs, **fkwargs)


class HasAcceptedRepoType(object):
    """
    Check if requested repo is within given repo type aliases

    TODO: anderson: not sure where to put this decorator
    """

    def __init__(self, *repo_type_list):
        self.repo_type_list = set(repo_type_list)

    def __call__(self, func):
        return get_cython_compat_decorator(self.__wrapper, func)

    def __wrapper(self, func, *fargs, **fkwargs):
        cls = fargs[0]
        rhodecode_repo = cls.rhodecode_repo

        log.debug('%s checking repo type for %s in %s',
                  self.__class__.__name__,
                  rhodecode_repo.alias, self.repo_type_list)

        if rhodecode_repo.alias in self.repo_type_list:
            return func(*fargs, **fkwargs)
        else:
            import rhodecode.lib.helpers as h
            h.flash(h.literal(
                _('Action not supported for %s.' % rhodecode_repo.alias)),
                category='warning')
            return redirect(
                url('summary_home', repo_name=cls.rhodecode_db_repo.repo_name))


class PermsDecorator(object):
    """
    Base class for controller decorators, we extract the current user from
    the class itself, which has it stored in base controllers
    """

    def __init__(self, *required_perms):
        self.required_perms = set(required_perms)

    def __call__(self, func):
        return get_cython_compat_decorator(self.__wrapper, func)

    def __wrapper(self, func, *fargs, **fkwargs):
        cls = fargs[0]
        _user = cls._rhodecode_user

        log.debug('checking %s permissions %s for %s %s',
                  self.__class__.__name__, self.required_perms, cls, _user)

        if self.check_permissions(_user):
            log.debug('Permission granted for %s %s', cls, _user)
            return func(*fargs, **fkwargs)

        else:
            log.debug('Permission denied for %s %s', cls, _user)
            anonymous = _user.username == User.DEFAULT_USER

            if anonymous:
                came_from = request.path_qs

                import rhodecode.lib.helpers as h
                h.flash(_('You need to be signed in to view this page'),
                        category='warning')
                return redirect(url('login_home', came_from=came_from))

            else:
                # redirect with forbidden ret code
                return abort(403)

    def check_permissions(self, user):
        """Dummy function for overriding"""
        raise NotImplementedError(
            'You have to write this function in child class')


class HasPermissionAllDecorator(PermsDecorator):
    """
    Checks for access permission for all given predicates. All of them
    have to be meet in order to fulfill the request
    """

    def check_permissions(self, user):
        perms = user.permissions_with_scope({})
        if self.required_perms.issubset(perms['global']):
            return True
        return False


class HasPermissionAnyDecorator(PermsDecorator):
    """
    Checks for access permission for any of given predicates. In order to
    fulfill the request any of predicates must be meet
    """

    def check_permissions(self, user):
        perms = user.permissions_with_scope({})
        if self.required_perms.intersection(perms['global']):
            return True
        return False


class HasRepoPermissionAllDecorator(PermsDecorator):
    """
    Checks for access permission for all given predicates for specific
    repository. All of them have to be meet in order to fulfill the request
    """

    def check_permissions(self, user):
        perms = user.permissions
        repo_name = get_repo_slug(request)
        try:
            user_perms = set([perms['repositories'][repo_name]])
        except KeyError:
            return False
        if self.required_perms.issubset(user_perms):
            return True
        return False


class HasRepoPermissionAnyDecorator(PermsDecorator):
    """
    Checks for access permission for any of given predicates for specific
    repository. In order to fulfill the request any of predicates must be meet
    """

    def check_permissions(self, user):
        perms = user.permissions
        repo_name = get_repo_slug(request)
        try:
            user_perms = set([perms['repositories'][repo_name]])
        except KeyError:
            return False

        if self.required_perms.intersection(user_perms):
            return True
        return False


class HasRepoGroupPermissionAllDecorator(PermsDecorator):
    """
    Checks for access permission for all given predicates for specific
    repository group. All of them have to be meet in order to
    fulfill the request
    """

    def check_permissions(self, user):
        perms = user.permissions
        group_name = get_repo_group_slug(request)
        try:
            user_perms = set([perms['repositories_groups'][group_name]])
        except KeyError:
            return False

        if self.required_perms.issubset(user_perms):
            return True
        return False


class HasRepoGroupPermissionAnyDecorator(PermsDecorator):
    """
    Checks for access permission for any of given predicates for specific
    repository group. In order to fulfill the request any
    of predicates must be met
    """

    def check_permissions(self, user):
        perms = user.permissions
        group_name = get_repo_group_slug(request)
        try:
            user_perms = set([perms['repositories_groups'][group_name]])
        except KeyError:
            return False

        if self.required_perms.intersection(user_perms):
            return True
        return False


class HasUserGroupPermissionAllDecorator(PermsDecorator):
    """
    Checks for access permission for all given predicates for specific
    user group. All of them have to be meet in order to fulfill the request
    """

    def check_permissions(self, user):
        perms = user.permissions
        group_name = get_user_group_slug(request)
        try:
            user_perms = set([perms['user_groups'][group_name]])
        except KeyError:
            return False

        if self.required_perms.issubset(user_perms):
            return True
        return False


class HasUserGroupPermissionAnyDecorator(PermsDecorator):
    """
    Checks for access permission for any of given predicates for specific
    user group. In order to fulfill the request any of predicates must be meet
    """

    def check_permissions(self, user):
        perms = user.permissions
        group_name = get_user_group_slug(request)
        try:
            user_perms = set([perms['user_groups'][group_name]])
        except KeyError:
            return False

        if self.required_perms.intersection(user_perms):
            return True
        return False


# CHECK FUNCTIONS
class PermsFunction(object):
    """Base function for other check functions"""

    def __init__(self, *perms):
        self.required_perms = set(perms)
        self.repo_name = None
        self.repo_group_name = None
        self.user_group_name = None

    def __bool__(self):
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        log.error('Checking bool value on a class instance of perm '
                  'function is not allowed: %s' % ''.join(stack_trace))
        # rather than throwing errors, here we always return False so if by
        # accident someone checks truth for just an instance it will always end
        # up in returning False
        return False
    __nonzero__ = __bool__

    def __call__(self, check_location='', user=None):
        if not user:
            log.debug('Using user attribute from global request')
            # TODO: remove this someday,put as user as attribute here
            user = request.user

        # init auth user if not already given
        if not isinstance(user, AuthUser):
            log.debug('Wrapping user %s into AuthUser', user)
            user = AuthUser(user.user_id)

        cls_name = self.__class__.__name__
        check_scope = self._get_check_scope(cls_name)
        check_location = check_location or 'unspecified location'

        log.debug('checking cls:%s %s usr:%s %s @ %s', cls_name,
                  self.required_perms, user, check_scope, check_location)
        if not user:
            log.warning('Empty user given for permission check')
            return False

        if self.check_permissions(user):
            log.debug('Permission to repo:`%s` GRANTED for user:`%s` @ %s',
                      check_scope, user, check_location)
            return True

        else:
            log.debug('Permission to repo:`%s` DENIED for user:`%s` @ %s',
                      check_scope, user, check_location)
            return False

    def _get_check_scope(self, cls_name):
        return {
            'HasPermissionAll':          'GLOBAL',
            'HasPermissionAny':          'GLOBAL',
            'HasRepoPermissionAll':      'repo:%s' % self.repo_name,
            'HasRepoPermissionAny':      'repo:%s' % self.repo_name,
            'HasRepoGroupPermissionAll': 'repo_group:%s' % self.repo_group_name,
            'HasRepoGroupPermissionAny': 'repo_group:%s' % self.repo_group_name,
            'HasUserGroupPermissionAll': 'user_group:%s' % self.user_group_name,
            'HasUserGroupPermissionAny': 'user_group:%s' % self.user_group_name,
        }.get(cls_name, '?:%s' % cls_name)

    def check_permissions(self, user):
        """Dummy function for overriding"""
        raise Exception('You have to write this function in child class')


class HasPermissionAll(PermsFunction):
    def check_permissions(self, user):
        perms = user.permissions_with_scope({})
        if self.required_perms.issubset(perms.get('global')):
            return True
        return False


class HasPermissionAny(PermsFunction):
    def check_permissions(self, user):
        perms = user.permissions_with_scope({})
        if self.required_perms.intersection(perms.get('global')):
            return True
        return False


class HasRepoPermissionAll(PermsFunction):
    def __call__(self, repo_name=None, check_location='', user=None):
        self.repo_name = repo_name
        return super(HasRepoPermissionAll, self).__call__(check_location, user)

    def check_permissions(self, user):
        if not self.repo_name:
            self.repo_name = get_repo_slug(request)

        perms = user.permissions
        try:
            user_perms = set([perms['repositories'][self.repo_name]])
        except KeyError:
            return False
        if self.required_perms.issubset(user_perms):
            return True
        return False


class HasRepoPermissionAny(PermsFunction):
    def __call__(self, repo_name=None, check_location='', user=None):
        self.repo_name = repo_name
        return super(HasRepoPermissionAny, self).__call__(check_location, user)

    def check_permissions(self, user):
        if not self.repo_name:
            self.repo_name = get_repo_slug(request)

        perms = user.permissions
        try:
            user_perms = set([perms['repositories'][self.repo_name]])
        except KeyError:
            return False
        if self.required_perms.intersection(user_perms):
            return True
        return False


class HasRepoGroupPermissionAny(PermsFunction):
    def __call__(self, group_name=None, check_location='', user=None):
        self.repo_group_name = group_name
        return super(HasRepoGroupPermissionAny, self).__call__(
            check_location, user)

    def check_permissions(self, user):
        perms = user.permissions
        try:
            user_perms = set(
                [perms['repositories_groups'][self.repo_group_name]])
        except KeyError:
            return False
        if self.required_perms.intersection(user_perms):
            return True
        return False


class HasRepoGroupPermissionAll(PermsFunction):
    def __call__(self, group_name=None, check_location='', user=None):
        self.repo_group_name = group_name
        return super(HasRepoGroupPermissionAll, self).__call__(
            check_location, user)

    def check_permissions(self, user):
        perms = user.permissions
        try:
            user_perms = set(
                [perms['repositories_groups'][self.repo_group_name]])
        except KeyError:
            return False
        if self.required_perms.issubset(user_perms):
            return True
        return False


class HasUserGroupPermissionAny(PermsFunction):
    def __call__(self, user_group_name=None, check_location='', user=None):
        self.user_group_name = user_group_name
        return super(HasUserGroupPermissionAny, self).__call__(
            check_location, user)

    def check_permissions(self, user):
        perms = user.permissions
        try:
            user_perms = set([perms['user_groups'][self.user_group_name]])
        except KeyError:
            return False
        if self.required_perms.intersection(user_perms):
            return True
        return False


class HasUserGroupPermissionAll(PermsFunction):
    def __call__(self, user_group_name=None, check_location='', user=None):
        self.user_group_name = user_group_name
        return super(HasUserGroupPermissionAll, self).__call__(
            check_location, user)

    def check_permissions(self, user):
        perms = user.permissions
        try:
            user_perms = set([perms['user_groups'][self.user_group_name]])
        except KeyError:
            return False
        if self.required_perms.issubset(user_perms):
            return True
        return False


# SPECIAL VERSION TO HANDLE MIDDLEWARE AUTH
class HasPermissionAnyMiddleware(object):
    def __init__(self, *perms):
        self.required_perms = set(perms)

    def __call__(self, user, repo_name):
        # repo_name MUST be unicode, since we handle keys in permission
        # dict by unicode
        repo_name = safe_unicode(repo_name)
        user = AuthUser(user.user_id)
        log.debug(
            'Checking VCS protocol permissions %s for user:%s repo:`%s`',
            self.required_perms, user, repo_name)

        if self.check_permissions(user, repo_name):
            log.debug('Permission to repo:`%s` GRANTED for user:%s @ %s',
                      repo_name, user, 'PermissionMiddleware')
            return True

        else:
            log.debug('Permission to repo:`%s` DENIED for user:%s @ %s',
                      repo_name, user, 'PermissionMiddleware')
            return False

    def check_permissions(self, user, repo_name):
        perms = user.permissions_with_scope({'repo_name': repo_name})

        try:
            user_perms = set([perms['repositories'][repo_name]])
        except Exception:
            log.exception('Error while accessing user permissions')
            return False

        if self.required_perms.intersection(user_perms):
            return True
        return False


# SPECIAL VERSION TO HANDLE API AUTH
class _BaseApiPerm(object):
    def __init__(self, *perms):
        self.required_perms = set(perms)

    def __call__(self, check_location=None, user=None, repo_name=None,
                 group_name=None, user_group_name=None):
        cls_name = self.__class__.__name__
        check_scope = 'global:%s' % (self.required_perms,)
        if repo_name:
            check_scope += ', repo_name:%s' % (repo_name,)

        if group_name:
            check_scope += ', repo_group_name:%s' % (group_name,)

        if user_group_name:
            check_scope += ', user_group_name:%s' % (user_group_name,)

        log.debug(
            'checking cls:%s %s %s @ %s'
            % (cls_name, self.required_perms, check_scope, check_location))
        if not user:
            log.debug('Empty User passed into arguments')
            return False

        # process user
        if not isinstance(user, AuthUser):
            user = AuthUser(user.user_id)
        if not check_location:
            check_location = 'unspecified'
        if self.check_permissions(user.permissions, repo_name, group_name,
                                  user_group_name):
            log.debug('Permission to repo:`%s` GRANTED for user:`%s` @ %s',
                      check_scope, user, check_location)
            return True

        else:
            log.debug('Permission to repo:`%s` DENIED for user:`%s` @ %s',
                      check_scope, user, check_location)
            return False

    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        """
        implement in child class should return True if permissions are ok,
        False otherwise

        :param perm_defs: dict with permission definitions
        :param repo_name: repo name
        """
        raise NotImplementedError()


class HasPermissionAllApi(_BaseApiPerm):
    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        if self.required_perms.issubset(perm_defs.get('global')):
            return True
        return False


class HasPermissionAnyApi(_BaseApiPerm):
    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        if self.required_perms.intersection(perm_defs.get('global')):
            return True
        return False


class HasRepoPermissionAllApi(_BaseApiPerm):
    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        try:
            _user_perms = set([perm_defs['repositories'][repo_name]])
        except KeyError:
            log.warning(traceback.format_exc())
            return False
        if self.required_perms.issubset(_user_perms):
            return True
        return False


class HasRepoPermissionAnyApi(_BaseApiPerm):
    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        try:
            _user_perms = set([perm_defs['repositories'][repo_name]])
        except KeyError:
            log.warning(traceback.format_exc())
            return False
        if self.required_perms.intersection(_user_perms):
            return True
        return False


class HasRepoGroupPermissionAnyApi(_BaseApiPerm):
    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        try:
            _user_perms = set([perm_defs['repositories_groups'][group_name]])
        except KeyError:
            log.warning(traceback.format_exc())
            return False
        if self.required_perms.intersection(_user_perms):
            return True
        return False


class HasRepoGroupPermissionAllApi(_BaseApiPerm):
    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        try:
            _user_perms = set([perm_defs['repositories_groups'][group_name]])
        except KeyError:
            log.warning(traceback.format_exc())
            return False
        if self.required_perms.issubset(_user_perms):
            return True
        return False


class HasUserGroupPermissionAnyApi(_BaseApiPerm):
    def check_permissions(self, perm_defs, repo_name=None, group_name=None,
                          user_group_name=None):
        try:
            _user_perms = set([perm_defs['user_groups'][user_group_name]])
        except KeyError:
            log.warning(traceback.format_exc())
            return False
        if self.required_perms.intersection(_user_perms):
            return True
        return False


def check_ip_access(source_ip, allowed_ips=None):
    """
    Checks if source_ip is a subnet of any of allowed_ips.

    :param source_ip:
    :param allowed_ips: list of allowed ips together with mask
    """
    log.debug('checking if ip:%s is subnet of %s' % (source_ip, allowed_ips))
    source_ip_address = ipaddress.ip_address(source_ip)
    if isinstance(allowed_ips, (tuple, list, set)):
        for ip in allowed_ips:
            try:
                network_address = ipaddress.ip_network(ip, strict=False)
                if source_ip_address in network_address:
                    log.debug('IP %s is network %s' %
                              (source_ip_address, network_address))
                    return True
                # for any case we cannot determine the IP, don't crash just
                # skip it and log as error, we want to say forbidden still when
                # sending bad IP
            except Exception:
                log.error(traceback.format_exc())
                continue
    return False


def get_cython_compat_decorator(wrapper, func):
    """
    Creates a cython compatible decorator. The previously used
    decorator.decorator() function seems to be incompatible with cython.

    :param wrapper: __wrapper method of the decorator class
    :param func: decorated function
    """
    @wraps(func)
    def local_wrapper(*args, **kwds):
        return wrapper(func, *args, **kwds)
    local_wrapper.__wrapped__ = func
    return local_wrapper
