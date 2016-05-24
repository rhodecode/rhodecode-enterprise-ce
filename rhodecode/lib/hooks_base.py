# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016  RhodeCode GmbH
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
Set of hooks run by RhodeCode Enterprise
"""

import os
import collections

import rhodecode
from rhodecode.lib import helpers as h
from rhodecode.lib.utils import action_logger
from rhodecode.lib.utils2 import safe_str
from rhodecode.lib.exceptions import HTTPLockedRC, UserCreationError
from rhodecode.model.db import Repository, User


HookResponse = collections.namedtuple('HookResponse', ('status', 'output'))


def _get_scm_size(alias, root_path):

    if not alias.startswith('.'):
        alias += '.'

    size_scm, size_root = 0, 0
    for path, unused_dirs, files in os.walk(safe_str(root_path)):
        if path.find(alias) != -1:
            for f in files:
                try:
                    size_scm += os.path.getsize(os.path.join(path, f))
                except OSError:
                    pass
        else:
            for f in files:
                try:
                    size_root += os.path.getsize(os.path.join(path, f))
                except OSError:
                    pass

    size_scm_f = h.format_byte_size_binary(size_scm)
    size_root_f = h.format_byte_size_binary(size_root)
    size_total_f = h.format_byte_size_binary(size_root + size_scm)

    return size_scm_f, size_root_f, size_total_f


# actual hooks called by Mercurial internally, and GIT by our Python Hooks
def repo_size(extras):
    """Present size of repository after push."""
    repo = Repository.get_by_repo_name(extras.repository)
    vcs_part = safe_str(u'.%s' % repo.repo_type)
    size_vcs, size_root, size_total = _get_scm_size(vcs_part,
                                                    repo.repo_full_path)
    msg = ('Repository `%s` size summary %s:%s repo:%s total:%s\n'
           % (repo.repo_name, vcs_part, size_vcs, size_root, size_total))
    return HookResponse(0, msg)


def pre_push(extras):
    """
    Hook executed before pushing code.

    It bans pushing when the repository is locked.
    """
    usr = User.get_by_username(extras.username)


    output = ''
    if extras.locked_by[0] and usr.user_id != int(extras.locked_by[0]):
        locked_by = User.get(extras.locked_by[0]).username
        reason = extras.locked_by[2]
        # this exception is interpreted in git/hg middlewares and based
        # on that proper return code is server to client
        _http_ret = HTTPLockedRC(
            _locked_by_explanation(extras.repository, locked_by, reason))
        if str(_http_ret.code).startswith('2'):
            # 2xx Codes don't raise exceptions
            output = _http_ret.title
        else:
            raise _http_ret

    # Calling hooks after checking the lock, for consistent behavior
    pre_push_extension(repo_store_path=Repository.base_path(), **extras)

    return HookResponse(0, output)


def pre_pull(extras):
    """
    Hook executed before pulling the code.

    It bans pulling when the repository is locked.
    """

    output = ''
    if extras.locked_by[0]:
        locked_by = User.get(extras.locked_by[0]).username
        reason = extras.locked_by[2]
        # this exception is interpreted in git/hg middlewares and based
        # on that proper return code is server to client
        _http_ret = HTTPLockedRC(
            _locked_by_explanation(extras.repository, locked_by, reason))
        if str(_http_ret.code).startswith('2'):
            # 2xx Codes don't raise exceptions
            output = _http_ret.title
        else:
            raise _http_ret

    # Calling hooks after checking the lock, for consistent behavior
    pre_pull_extension(**extras)

    return HookResponse(0, output)


def post_pull(extras):
    """Hook executed after client pulls the code."""
    user = User.get_by_username(extras.username)
    action = 'pull'
    action_logger(user, action, extras.repository, extras.ip, commit=True)

    # extension hook call
    post_pull_extension(**extras)

    output = ''
    # make lock is a tri state False, True, None. We only make lock on True
    if extras.make_lock is True:
        Repository.lock(Repository.get_by_repo_name(extras.repository),
                        user.user_id,
                        lock_reason=Repository.LOCK_PULL)
        msg = 'Made lock on repo `%s`' % (extras.repository,)
        output += msg

    if extras.locked_by[0]:
        locked_by = User.get(extras.locked_by[0]).username
        reason = extras.locked_by[2]
        _http_ret = HTTPLockedRC(
            _locked_by_explanation(extras.repository, locked_by, reason))
        if str(_http_ret.code).startswith('2'):
            # 2xx Codes don't raise exceptions
            output += _http_ret.title

    return HookResponse(0, output)


def post_push(extras):
    """Hook executed after user pushes to the repository."""
    action_tmpl = extras.action + ':%s'
    commit_ids = extras.commit_ids[:29000]

    action = action_tmpl % ','.join(commit_ids)
    action_logger(
        extras.username, action, extras.repository, extras.ip, commit=True)

    # extension hook call
    post_push_extension(
        repo_store_path=Repository.base_path(),
        pushed_revs=commit_ids,
        **extras)

    output = ''
    # make lock is a tri state False, True, None. We only release lock on False
    if extras.make_lock is False:
        Repository.unlock(Repository.get_by_repo_name(extras.repository))
        msg = 'Released lock on repo `%s`\n' % extras.repository
        output += msg

    if extras.locked_by[0]:
        locked_by = User.get(extras.locked_by[0]).username
        reason = extras.locked_by[2]
        _http_ret = HTTPLockedRC(
            _locked_by_explanation(extras.repository, locked_by, reason))
        # TODO: johbo: if not?
        if str(_http_ret.code).startswith('2'):
            # 2xx Codes don't raise exceptions
            output += _http_ret.title

    output += 'RhodeCode: push completed\n'

    return HookResponse(0, output)


def _locked_by_explanation(repo_name, user_name, reason):
    message = (
        'Repository `%s` locked by user `%s`. Reason:`%s`'
        % (repo_name, user_name, reason))
    return message


def check_allowed_create_user(user_dict, created_by, **kwargs):
    # pre create hooks
    if pre_create_user.is_active():
        allowed, reason = pre_create_user(created_by=created_by, **user_dict)
        if not allowed:
            raise UserCreationError(reason)


class ExtensionCallback(object):
    """
    Forwards a given call to rcextensions, sanitizes keyword arguments.

    Does check if there is an extension active for that hook. If it is
    there, it will forward all `kwargs_keys` keyword arguments to the
    extension callback.
    """

    def __init__(self, hook_name, kwargs_keys):
        self._hook_name = hook_name
        self._kwargs_keys = set(kwargs_keys)

    def __call__(self, *args, **kwargs):
        kwargs_to_pass = dict((key, kwargs[key]) for key in self._kwargs_keys)
        callback = self._get_callback()
        if callback:
            return callback(**kwargs_to_pass)

    def is_active(self):
        return hasattr(rhodecode.EXTENSIONS, self._hook_name)

    def _get_callback(self):
        return getattr(rhodecode.EXTENSIONS, self._hook_name, None)


pre_pull_extension = ExtensionCallback(
    hook_name='PRE_PULL_HOOK',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository'))


post_pull_extension = ExtensionCallback(
    hook_name='PULL_HOOK',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository'))


pre_push_extension = ExtensionCallback(
    hook_name='PRE_PUSH_HOOK',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'repo_store_path'))


post_push_extension = ExtensionCallback(
    hook_name='PUSH_HOOK',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'repo_store_path', 'pushed_revs'))


pre_create_user = ExtensionCallback(
    hook_name='PRE_CREATE_USER_HOOK',
    kwargs_keys=(
        'username', 'password', 'email', 'firstname', 'lastname', 'active',
        'admin', 'created_by'))


log_create_pull_request = ExtensionCallback(
    hook_name='CREATE_PULL_REQUEST',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers'))


log_merge_pull_request = ExtensionCallback(
    hook_name='MERGE_PULL_REQUEST',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers'))


log_close_pull_request = ExtensionCallback(
    hook_name='CLOSE_PULL_REQUEST',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers'))


log_review_pull_request = ExtensionCallback(
    hook_name='REVIEW_PULL_REQUEST',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers'))


log_update_pull_request = ExtensionCallback(
    hook_name='UPDATE_PULL_REQUEST',
    kwargs_keys=(
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers'))


log_create_user = ExtensionCallback(
    hook_name='CREATE_USER_HOOK',
    kwargs_keys=(
        'username', 'full_name_or_username', 'full_contact', 'user_id',
        'name', 'firstname', 'short_contact', 'admin', 'lastname',
        'ip_addresses', 'extern_type', 'extern_name',
        'email', 'api_key', 'api_keys', 'last_login',
        'full_name', 'active', 'password', 'emails',
        'inherit_default_permissions', 'created_by', 'created_on'))


log_delete_user = ExtensionCallback(
    hook_name='DELETE_USER_HOOK',
    kwargs_keys=(
        'username', 'full_name_or_username', 'full_contact', 'user_id',
        'name', 'firstname', 'short_contact', 'admin', 'lastname',
        'ip_addresses',
        'email', 'api_key', 'last_login',
        'full_name', 'active', 'password', 'emails',
        'inherit_default_permissions', 'deleted_by'))


log_create_repository = ExtensionCallback(
    hook_name='CREATE_REPO_HOOK',
    kwargs_keys=(
        'repo_name', 'repo_type', 'description', 'private', 'created_on',
        'enable_downloads', 'repo_id', 'user_id', 'enable_statistics',
        'clone_uri', 'fork_id', 'group_id', 'created_by'))


log_delete_repository = ExtensionCallback(
    hook_name='DELETE_REPO_HOOK',
    kwargs_keys=(
        'repo_name', 'repo_type', 'description', 'private', 'created_on',
        'enable_downloads', 'repo_id', 'user_id', 'enable_statistics',
        'clone_uri', 'fork_id', 'group_id', 'deleted_by', 'deleted_on'))


log_create_repository_group = ExtensionCallback(
    hook_name='CREATE_REPO_GROUP_HOOK',
    kwargs_keys=(
        'group_name', 'group_parent_id', 'group_description',
        'group_id', 'user_id', 'created_by', 'created_on',
        'enable_locking'))
