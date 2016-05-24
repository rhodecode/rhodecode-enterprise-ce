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
Reference example of the rcextensions module.

This module is also used during integration tests to verify that all showed
examples are valid.
"""

import collections
import os
import imp

here = os.path.dirname(os.path.abspath(__file__))


def load_extension(filename, async=False):
    """
    use to load extensions inside rcextension folder.
    for example::

        callback = load_extension('email.py', async=False)
        if callback:
            callback('foobar')

    put file named email.py inside rcextensions folder to load it. Changing
    async=True will make the call of the plugin async, it's useful for
    blocking calls like sending an email or notification with APIs.
    """
    mod = ''.join(filename.split('.')[:-1])
    loaded = imp.load_source(mod, os.path.join(here, filename))

    callback = getattr(loaded, 'run', None)
    if not callback:
        raise Exception('Plugin missing `run` method')
    if async:
        # modify callback so it's actually an async call
        def _async_callback(*args, **kwargs):
            import threading
            thr = threading.Thread(target=callback, args=args, kwargs=kwargs)
            thr.start()
            if kwargs.get('_async_block'):
                del kwargs['_async_block']
                thr.join()

        return _async_callback
    return callback


# Additional mappings that are not present in the pygments lexers
# used for building stats
# format is {'ext':['Names']} eg. {'py':['Python']} note: there can be
# more than one name for extension
# NOTE: that this will overide any mappings in LANGUAGES_EXTENSIONS_MAP
# build by pygments
EXTRA_MAPPINGS = {}

# additional lexer definitions for custom files it's overrides pygments lexers,
# and uses defined name of lexer to colorize the files. Format is {'ext':
# 'lexer_name'} List of lexers can be printed running:
#   >> python -c "import pprint;from pygments import lexers;
#           pprint.pprint([(x[0], x[1]) for x in lexers.get_all_lexers()]);"

EXTRA_LEXERS = {}


calls = collections.defaultdict(list)


def log_call(name):
    def wrap(f):
        def wrapper(*args, **kwargs):
            calls[name].append((args, kwargs))
            return f(*args, **kwargs)
        return wrapper
    return wrap


# =============================================================================
#  POST CREATE REPOSITORY HOOK
# =============================================================================
# this function will be executed after each repository is created


def _crrepohook(*args, **kwargs):
    """
    Post create repository HOOK
    kwargs available:
     :param repo_name:
     :param repo_type:
     :param description:
     :param private:
     :param created_on:
     :param enable_downloads:
     :param repo_id:
     :param user_id:
     :param enable_statistics:
     :param clone_uri:
     :param fork_id:
     :param group_id:
     :param created_by:
    """

    expected_parameters = (
        'repo_name', 'repo_type', 'description', 'private', 'created_on',
        'enable_downloads', 'repo_id', 'user_id', 'enable_statistics',
        'clone_uri', 'fork_id', 'group_id', 'created_by')
    _verify_kwargs(expected_parameters, kwargs)

    return 0

CREATE_REPO_HOOK = _crrepohook


# =============================================================================
#  POST CREATE REPOSITORY GROUP HOOK
# =============================================================================
# this function will be executed after each repository group is created


def _crrepogrouphook(*args, **kwargs):
    """
    Post create repository group HOOK
    kwargs available:

     :param group_name:
     :param group_parent_id:
     :param group_description:
     :param group_id:
     :param user_id:
     :param created_by:
     :param created_on:
     :param enable_locking:
    """

    expected_parameters = (
        'group_name', 'group_parent_id', 'group_description',
        'group_id', 'user_id', 'created_by', 'created_on',
        'enable_locking')
    _verify_kwargs(expected_parameters, kwargs)

    return 0

CREATE_REPO_GROUP_HOOK = _crrepogrouphook

# =============================================================================
#  PRE CREATE USER HOOK
# =============================================================================
# this function will be executed before each user is created


def _pre_cruserhook(*args, **kwargs):
    """
    Pre create user HOOK, it returns a tuple of bool, reason.
    If bool is False the user creation will be stopped and reason
    will be displayed to the user.
    kwargs available:
    :param username:
    :param password:
    :param email:
    :param firstname:
    :param lastname:
    :param active:
    :param admin:
    :param created_by:
    """

    expected_parameters = (
        'username', 'password', 'email', 'firstname', 'lastname', 'active',
        'admin', 'created_by')
    _verify_kwargs(expected_parameters, kwargs)

    reason = 'allowed'
    return True, reason
PRE_CREATE_USER_HOOK = _pre_cruserhook

# =============================================================================
#  POST CREATE USER HOOK
# =============================================================================
# this function will be executed after each user is created


def _cruserhook(*args, **kwargs):
    """
    Post create user HOOK
    kwargs available:
      :param username:
      :param full_name_or_username:
      :param full_contact:
      :param user_id:
      :param name:
      :param firstname:
      :param short_contact:
      :param admin:
      :param lastname:
      :param ip_addresses:
      :param extern_type:
      :param extern_name:
      :param email:
      :param api_key:
      :parma api_keys:
      :param last_login:
      :param full_name:
      :param active:
      :param password:
      :param emails:
      :param inherit_default_permissions:
      :param created_by:
      :param created_on:
    """

    expected_parameters = (
        'username', 'full_name_or_username', 'full_contact', 'user_id',
        'name', 'firstname', 'short_contact', 'admin', 'lastname',
        'ip_addresses', 'extern_type', 'extern_name',
        'email', 'api_key', 'api_keys', 'last_login',
        'full_name', 'active', 'password', 'emails',
        'inherit_default_permissions', 'created_by', 'created_on')
    _verify_kwargs(expected_parameters, kwargs)

    return 0
CREATE_USER_HOOK = _cruserhook


# =============================================================================
#  POST DELETE REPOSITORY HOOK
# =============================================================================
# this function will be executed after each repository deletion


def _dlrepohook(*args, **kwargs):
    """
    Post delete repository HOOK
    kwargs available:
     :param repo_name:
     :param repo_type:
     :param description:
     :param private:
     :param created_on:
     :param enable_downloads:
     :param repo_id:
     :param user_id:
     :param enable_statistics:
     :param clone_uri:
     :param fork_id:
     :param group_id:
     :param deleted_by:
     :param deleted_on:
    """

    expected_parameters = (
        'repo_name', 'repo_type', 'description', 'private', 'created_on',
        'enable_downloads', 'repo_id', 'user_id', 'enable_statistics',
        'clone_uri', 'fork_id', 'group_id', 'deleted_by', 'deleted_on')
    _verify_kwargs(expected_parameters, kwargs)

    return 0
DELETE_REPO_HOOK = _dlrepohook


# =============================================================================
#  POST DELETE USER HOOK
# =============================================================================
# this function will be executed after each user is deleted


def _dluserhook(*args, **kwargs):
    """
    Post delete user HOOK
    kwargs available:
      :param username:
      :param full_name_or_username:
      :param full_contact:
      :param user_id:
      :param name:
      :param firstname:
      :param short_contact:
      :param admin:
      :param lastname:
      :param ip_addresses:
      :param ldap_dn:
      :param email:
      :param api_key:
      :param last_login:
      :param full_name:
      :param active:
      :param password:
      :param emails:
      :param inherit_default_permissions:
      :param deleted_by:
    """

    expected_parameters = (
        'username', 'full_name_or_username', 'full_contact', 'user_id',
        'name', 'firstname', 'short_contact', 'admin', 'lastname',
        'ip_addresses',
        # TODO: johbo: Check what's the status with the ldap_dn parameter
        # 'ldap_dn',
        'email', 'api_key', 'last_login',
        'full_name', 'active', 'password', 'emails',
        'inherit_default_permissions', 'deleted_by')
    _verify_kwargs(expected_parameters, kwargs)

    return 0
DELETE_USER_HOOK = _dluserhook


# =============================================================================
#  PRE PUSH HOOK
# =============================================================================


# this function will be executed after each push it's executed after the
# build-in hook that RhodeCode uses for logging pushes
@log_call('pre_push')
def _prepushhook(*args, **kwargs):
    """
    Pre push hook
    kwargs available:

      :param server_url: url of instance that triggered this hook
      :param config: path to .ini config used
      :param scm: type of VS 'git' or 'hg'
      :param username: name of user who pushed
      :param ip: ip of who pushed
      :param action: push
      :param repository: repository name
      :param repo_store_path: full path to where repositories are stored
    """

    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'repo_store_path')
    _verify_kwargs(expected_parameters, kwargs)

    return 0
PRE_PUSH_HOOK = _prepushhook


# =============================================================================
#  POST PUSH HOOK
# =============================================================================


# this function will be executed after each push it's executed after the
# build-in hook that RhodeCode uses for logging pushes
@log_call('post_push')
def _pushhook(*args, **kwargs):
    """
    Post push hook
    kwargs available:

      :param server_url: url of instance that triggered this hook
      :param config: path to .ini config used
      :param scm: type of VS 'git' or 'hg'
      :param username: name of user who pushed
      :param ip: ip of who pushed
      :param action: push
      :param repository: repository name
      :param repo_store_path: full path to where repositories are stored
      :param pushed_revs: list of pushed revisions
    """

    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'repo_store_path', 'pushed_revs')
    _verify_kwargs(expected_parameters, kwargs)

    return 0
PUSH_HOOK = _pushhook


# =============================================================================
#  PRE PULL HOOK
# =============================================================================

# this function will be executed after each push it's executed after the
# build-in hook that RhodeCode uses for logging pulls
def _prepullhook(*args, **kwargs):
    """
    Post pull hook
    kwargs available::

      :param server_url: url of instance that triggered this hook
      :param config: path to .ini config used
      :param scm: type of VS 'git' or 'hg'
      :param username: name of user who pulled
      :param ip: ip of who pulled
      :param action: pull
      :param repository: repository name
    """

    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository')
    _verify_kwargs(expected_parameters, kwargs)

    return 0
PRE_PULL_HOOK = _prepullhook



# =============================================================================
#  POST PULL HOOK
# =============================================================================

# this function will be executed after each push it's executed after the
# build-in hook that RhodeCode uses for logging pulls
def _pullhook(*args, **kwargs):
    """
    Post pull hook
    kwargs available::

      :param server_url: url of instance that triggered this hook
      :param config: path to .ini config used
      :param scm: type of VS 'git' or 'hg'
      :param username: name of user who pulled
      :param ip: ip of who pulled
      :param action: pull
      :param repository: repository name
    """

    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository')
    _verify_kwargs(expected_parameters, kwargs)

    return 0
PULL_HOOK = _pullhook


# =============================================================================
#  PULL REQUEST RELATED HOOKS
# =============================================================================

def _create_pull_request_hook(*args, **kwargs):
    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers')
    _verify_kwargs(expected_parameters, kwargs)
    return 0
CREATE_PULL_REQUEST = _create_pull_request_hook


def _merge_pull_request_hook(*args, **kwargs):
    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers')
    _verify_kwargs(expected_parameters, kwargs)
    return 0
MERGE_PULL_REQUEST = _merge_pull_request_hook


def _close_pull_request_hook(*args, **kwargs):
    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers')
    _verify_kwargs(expected_parameters, kwargs)
    return 0
CLOSE_PULL_REQUEST = _close_pull_request_hook


def _review_pull_request_hook(*args, **kwargs):
    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers')
    _verify_kwargs(expected_parameters, kwargs)
    return 0
REVIEW_PULL_REQUEST = _review_pull_request_hook


def _update_pull_request_hook(*args, **kwargs):
    expected_parameters = (
        'server_url', 'config', 'scm', 'username', 'ip', 'action',
        'repository', 'pull_request_id', 'url', 'title', 'description',
        'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
        'mergeable', 'source', 'target', 'author', 'reviewers')
    _verify_kwargs(expected_parameters, kwargs)
    return 0
UPDATE_PULL_REQUEST = _update_pull_request_hook


def _verify_kwargs(expected_parameters, kwargs):
    """
    Verify that exactly `expected_parameters` are passed in as `kwargs`.
    """
    expected_parameters = set(expected_parameters)
    kwargs_keys = set(kwargs.keys())
    if kwargs_keys != expected_parameters:
        missing_kwargs = expected_parameters - kwargs_keys
        unexpected_kwargs = kwargs_keys - expected_parameters
        raise AssertionError(
            "Missing parameters: %r, unexpected parameters: %s" %
            (missing_kwargs, unexpected_kwargs))
