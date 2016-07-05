# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016  RhodeCode GmbH
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

import logging
import time

import colander

from rhodecode import BACKENDS
from rhodecode.api import jsonrpc_method, JSONRPCError, JSONRPCForbidden, json
from rhodecode.api.utils import (
    has_superadmin_permission, Optional, OAttr, get_repo_or_error,
    get_user_group_or_error, get_user_or_error, has_repo_permissions,
    get_perm_or_error, store_update, get_repo_group_or_error, parse_args,
    get_origin, build_commit_data)
from rhodecode.lib.auth import (
    HasPermissionAnyApi, HasRepoGroupPermissionAnyApi,
    HasUserGroupPermissionAnyApi)
from rhodecode.lib.exceptions import StatusChangeOnClosedPullRequestError
from rhodecode.lib.utils import map_groups
from rhodecode.lib.utils2 import str2bool, time_to_datetime
from rhodecode.model.changeset_status import ChangesetStatusModel
from rhodecode.model.comment import ChangesetCommentsModel
from rhodecode.model.db import (
    Session, ChangesetStatus, RepositoryField, Repository)
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.scm import ScmModel, RepoList
from rhodecode.model.settings import SettingsModel
from rhodecode.model.validation_schema import RepoSchema

log = logging.getLogger(__name__)


@jsonrpc_method()
def get_repo(request, apiuser, repoid, cache=Optional(True)):
    """
    Gets an existing repository by its name or repository_id.

    The members section so the output returns users groups or users
    associated with that repository.

    This command can only be run using an |authtoken| with admin rights,
    or users with at least read rights to the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: The repository name or repository id.
    :type repoid: str or int
    :param cache: use the cached value for last changeset
    :type: cache: Optional(bool)

    Example output:

    .. code-block:: bash

        {
          "error": null,
          "id": <repo_id>,
          "result": {
            "clone_uri": null,
            "created_on": "timestamp",
            "description": "repo description",
            "enable_downloads": false,
            "enable_locking": false,
            "enable_statistics": false,
            "followers": [
              {
                "active": true,
                "admin": false,
                "api_key": "****************************************",
                "api_keys": [
                  "****************************************"
                ],
                "email": "user@example.com",
                "emails": [
                  "user@example.com"
                ],
                "extern_name": "rhodecode",
                "extern_type": "rhodecode",
                "firstname": "username",
                "ip_addresses": [],
                "language": null,
                "last_login": "2015-09-16T17:16:35.854",
                "lastname": "surname",
                "user_id": <user_id>,
                "username": "name"
              }
            ],
            "fork_of": "parent-repo",
            "landing_rev": [
              "rev",
              "tip"
            ],
            "last_changeset": {
              "author": "User <user@example.com>",
              "branch": "default",
              "date": "timestamp",
              "message": "last commit message",
              "parents": [
                {
                  "raw_id": "commit-id"
                }
              ],
              "raw_id": "commit-id",
              "revision": <revision number>,
              "short_id": "short id"
            },
            "lock_reason": null,
            "locked_by": null,
            "locked_date": null,
            "members": [
              {
                "name": "super-admin-name",
                "origin": "super-admin",
                "permission": "repository.admin",
                "type": "user"
              },
              {
                "name": "owner-name",
                "origin": "owner",
                "permission": "repository.admin",
                "type": "user"
              },
              {
                "name": "user-group-name",
                "origin": "permission",
                "permission": "repository.write",
                "type": "user_group"
              }
            ],
            "owner": "owner-name",
            "permissions": [
              {
                "name": "super-admin-name",
                "origin": "super-admin",
                "permission": "repository.admin",
                "type": "user"
              },
              {
                "name": "owner-name",
                "origin": "owner",
                "permission": "repository.admin",
                "type": "user"
              },
              {
                "name": "user-group-name",
                "origin": "permission",
                "permission": "repository.write",
                "type": "user_group"
              }
            ],
            "private": true,
            "repo_id": 676,
            "repo_name": "user-group/repo-name",
            "repo_type": "hg"
          }
        }
    """

    repo = get_repo_or_error(repoid)
    cache = Optional.extract(cache)
    include_secrets = False
    if has_superadmin_permission(apiuser):
        include_secrets = True
    else:
        # check if we have at least read permission for this repo !
        _perms = (
            'repository.admin', 'repository.write', 'repository.read',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    permissions = []
    for _user in repo.permissions():
        user_data = {
            'name': _user.username,
            'permission': _user.permission,
            'origin': get_origin(_user),
            'type': "user",
        }
        permissions.append(user_data)

    for _user_group in repo.permission_user_groups():
        user_group_data = {
            'name': _user_group.users_group_name,
            'permission': _user_group.permission,
            'origin': get_origin(_user_group),
            'type': "user_group",
        }
        permissions.append(user_group_data)

    following_users = [
        user.user.get_api_data(include_secrets=include_secrets)
        for user in repo.followers]

    if not cache:
        repo.update_commit_cache()
    data = repo.get_api_data(include_secrets=include_secrets)
    data['members'] = permissions  # TODO: this should be deprecated soon
    data['permissions'] = permissions
    data['followers'] = following_users
    return data


@jsonrpc_method()
def get_repos(request, apiuser):
    """
    Lists all existing repositories.

    This command can only be run using an |authtoken| with admin rights,
    or users with at least read rights to |repos|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: [
                  {
                    "repo_id" :          "<repo_id>",
                    "repo_name" :        "<reponame>"
                    "repo_type" :        "<repo_type>",
                    "clone_uri" :        "<clone_uri>",
                    "private": :         "<bool>",
                    "created_on" :       "<datetimecreated>",
                    "description" :      "<description>",
                    "landing_rev":       "<landing_rev>",
                    "owner":             "<repo_owner>",
                    "fork_of":           "<name_of_fork_parent>",
                    "enable_downloads":  "<bool>",
                    "enable_locking":    "<bool>",
                    "enable_statistics": "<bool>",
                  },
                  ...
                ]
        error:  null
    """

    include_secrets = has_superadmin_permission(apiuser)
    _perms = ('repository.read', 'repository.write', 'repository.admin',)
    extras = {'user': apiuser}

    repo_list = RepoList(
        RepoModel().get_all(), perm_set=_perms, extra_kwargs=extras)
    return [repo.get_api_data(include_secrets=include_secrets)
            for repo in repo_list]


@jsonrpc_method()
def get_repo_changeset(request, apiuser, repoid, revision,
                       details=Optional('basic')):
    """
    Returns information about a changeset.

    Additionally parameters define the amount of details returned by
    this function.

    This command can only be run using an |authtoken| with admin rights,
    or users with at least read rights to the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: The repository name or repository id
    :type repoid: str or int
    :param revision: revision for which listing should be done
    :type revision: str
    :param details: details can be 'basic|extended|full' full gives diff
        info details like the diff itself, and number of changed files etc.
    :type details: Optional(str)

    """
    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = (
            'repository.admin', 'repository.write', 'repository.read',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    changes_details = Optional.extract(details)
    _changes_details_types = ['basic', 'extended', 'full']
    if changes_details not in _changes_details_types:
        raise JSONRPCError(
            'ret_type must be one of %s' % (
                ','.join(_changes_details_types)))

    pre_load = ['author', 'branch', 'date', 'message', 'parents',
                'status', '_commit', '_file_paths']

    try:
        cs = repo.get_commit(commit_id=revision, pre_load=pre_load)
    except TypeError as e:
        raise JSONRPCError(e.message)
    _cs_json = cs.__json__()
    _cs_json['diff'] = build_commit_data(cs, changes_details)
    if changes_details == 'full':
        _cs_json['refs'] = {
            'branches': [cs.branch],
            'bookmarks': getattr(cs, 'bookmarks', []),
            'tags': cs.tags
        }
    return _cs_json


@jsonrpc_method()
def get_repo_changesets(request, apiuser, repoid, start_rev, limit,
                        details=Optional('basic')):
    """
    Returns a set of commits limited by the number starting
    from the `start_rev` option.

    Additional parameters define the amount of details returned by this
    function.

    This command can only be run using an |authtoken| with admin rights,
    or users with at least read rights to |repos|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: The repository name or repository ID.
    :type repoid: str or int
    :param start_rev: The starting revision from where to get changesets.
    :type start_rev: str
    :param limit: Limit the number of commits to this amount
    :type limit: str or int
    :param details: Set the level of detail returned. Valid option are:
        ``basic``, ``extended`` and ``full``.
    :type details: Optional(str)

    .. note::

       Setting the parameter `details` to the value ``full`` is extensive
       and returns details like the diff itself, and the number
       of changed files.

    """
    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = (
            'repository.admin', 'repository.write', 'repository.read',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    changes_details = Optional.extract(details)
    _changes_details_types = ['basic', 'extended', 'full']
    if changes_details not in _changes_details_types:
        raise JSONRPCError(
            'ret_type must be one of %s' % (
                ','.join(_changes_details_types)))

    limit = int(limit)
    pre_load = ['author', 'branch', 'date', 'message', 'parents',
                'status', '_commit', '_file_paths']

    vcs_repo = repo.scm_instance()
    # SVN needs a special case to distinguish its index and commit id
    if vcs_repo and vcs_repo.alias == 'svn' and (start_rev == '0'):
        start_rev = vcs_repo.commit_ids[0]

    try:
        commits = vcs_repo.get_commits(
            start_id=start_rev, pre_load=pre_load)
    except TypeError as e:
        raise JSONRPCError(e.message)
    except Exception:
        log.exception('Fetching of commits failed')
        raise JSONRPCError('Error occurred during commit fetching')

    ret = []
    for cnt, commit in enumerate(commits):
        if cnt >= limit != -1:
            break
        _cs_json = commit.__json__()
        _cs_json['diff'] = build_commit_data(commit, changes_details)
        if changes_details == 'full':
            _cs_json['refs'] = {
                'branches': [commit.branch],
                'bookmarks': getattr(commit, 'bookmarks', []),
                'tags': commit.tags
            }
        ret.append(_cs_json)
    return ret


@jsonrpc_method()
def get_repo_nodes(request, apiuser, repoid, revision, root_path,
                   ret_type=Optional('all'), details=Optional('basic')):
    """
    Returns a list of nodes and children in a flat list for a given
    path at given revision.

    It's possible to specify ret_type to show only `files` or `dirs`.

    This command can only be run using an |authtoken| with admin rights,
    or users with at least read rights to |repos|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: The repository name or repository ID.
    :type repoid: str or int
    :param revision: The revision for which listing should be done.
    :type revision: str
    :param root_path: The path from which to start displaying.
    :type root_path: str
    :param ret_type: Set the return type. Valid options are
        ``all`` (default), ``files`` and ``dirs``.
    :type ret_type: Optional(str)
    :param details: Returns extended information about nodes, such as
        md5, binary, and or content.  The valid options are ``basic`` and
        ``full``.
    :type details: Optional(str)

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: [
                  {
                    "name" : "<name>"
                    "type" : "<type>",
                    "binary": "<true|false>" (only in extended mode)
                    "md5"  : "<md5 of file content>" (only in extended mode)
                  },
                  ...
                ]
        error:  null
    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = (
            'repository.admin', 'repository.write', 'repository.read',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    ret_type = Optional.extract(ret_type)
    details = Optional.extract(details)
    _extended_types = ['basic', 'full']
    if details not in _extended_types:
        raise JSONRPCError(
            'ret_type must be one of %s' % (','.join(_extended_types)))
    extended_info = False
    content = False
    if details == 'basic':
        extended_info = True

    if details == 'full':
        extended_info = content = True

    _map = {}
    try:
        # check if repo is not empty by any chance, skip quicker if it is.
        _scm = repo.scm_instance()
        if _scm.is_empty():
            return []

        _d, _f = ScmModel().get_nodes(
            repo, revision, root_path, flat=False,
            extended_info=extended_info, content=content)
        _map = {
            'all': _d + _f,
            'files': _f,
            'dirs': _d,
        }
        return _map[ret_type]
    except KeyError:
        raise JSONRPCError(
            'ret_type must be one of %s' % (','.join(sorted(_map.keys()))))
    except Exception:
        log.exception("Exception occurred while trying to get repo nodes")
        raise JSONRPCError(
            'failed to get repo: `%s` nodes' % repo.repo_name
        )


@jsonrpc_method()
def get_repo_refs(request, apiuser, repoid):
    """
    Returns a dictionary of current references. It returns
    bookmarks, branches, closed_branches, and tags for given repository

    It's possible to specify ret_type to show only `files` or `dirs`.

    This command can only be run using an |authtoken| with admin rights,
    or users with at least read rights to |repos|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: The repository name or repository ID.
    :type repoid: str or int

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: [
                  TODO...
                ]
        error:  null
    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin', 'repository.write', 'repository.read',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    try:
        # check if repo is not empty by any chance, skip quicker if it is.
        vcs_instance = repo.scm_instance()
        refs = vcs_instance.refs()
        return refs
    except Exception:
        log.exception("Exception occurred while trying to get repo refs")
        raise JSONRPCError(
            'failed to get repo: `%s` references' % repo.repo_name
        )


@jsonrpc_method()
def create_repo(request, apiuser, repo_name, repo_type,
                owner=Optional(OAttr('apiuser')), description=Optional(''),
                private=Optional(False), clone_uri=Optional(None),
                landing_rev=Optional('rev:tip'),
                enable_statistics=Optional(False),
                enable_locking=Optional(False),
                enable_downloads=Optional(False),
                copy_permissions=Optional(False)):
    """
    Creates a repository.

    * If the repository name contains "/", all the required repository
      groups will be created.

      For example "foo/bar/baz" will create |repo| groups "foo" and "bar"
      (with "foo" as parent). It will also create the "baz" repository
      with "bar" as |repo| group.

    This command can only be run using an |authtoken| with at least
    write permissions to the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repo_name: Set the repository name.
    :type repo_name: str
    :param repo_type: Set the repository type; 'hg','git', or 'svn'.
    :type repo_type: str
    :param owner: user_id or username
    :type owner: Optional(str)
    :param description: Set the repository description.
    :type description: Optional(str)
    :param private:
    :type private: bool
    :param clone_uri:
    :type clone_uri: str
    :param landing_rev: <rev_type>:<rev>
    :type landing_rev: str
    :param enable_locking:
    :type enable_locking: bool
    :param enable_downloads:
    :type enable_downloads: bool
    :param enable_statistics:
    :type enable_statistics: bool
    :param copy_permissions: Copy permission from group in which the
        repository is being created.
    :type copy_permissions: bool


    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg": "Created new repository `<reponame>`",
                  "success": true,
                  "task": "<celery task id or None if done sync>"
                }
        error:  null


    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
         'failed to create repository `<repo_name>`
      }

    """
    schema = RepoSchema()
    try:
        data = schema.deserialize({
            'repo_name': repo_name
        })
    except colander.Invalid as e:
        raise JSONRPCError("Validation failed: %s" % (e.asdict(),))
    repo_name = data['repo_name']

    (repo_name_cleaned,
     parent_group_name) = RepoGroupModel()._get_group_name_and_parent(
        repo_name)

    if not HasPermissionAnyApi(
            'hg.admin', 'hg.create.repository')(user=apiuser):
        # check if we have admin permission for this repo group if given !

        if parent_group_name:
            repogroupid = parent_group_name
            repo_group = get_repo_group_or_error(parent_group_name)

            _perms = ('group.admin',)
            if not HasRepoGroupPermissionAnyApi(*_perms)(
                    user=apiuser, group_name=repo_group.group_name):
                raise JSONRPCError(
                    'repository group `%s` does not exist' % (
                        repogroupid,))
        else:
            raise JSONRPCForbidden()

    if not has_superadmin_permission(apiuser):
        if not isinstance(owner, Optional):
            # forbid setting owner for non-admins
            raise JSONRPCError(
                'Only RhodeCode admin can specify `owner` param')

    if isinstance(owner, Optional):
        owner = apiuser.user_id

    owner = get_user_or_error(owner)

    if RepoModel().get_by_repo_name(repo_name):
        raise JSONRPCError("repo `%s` already exist" % repo_name)

    defs = SettingsModel().get_default_repo_settings(strip_prefix=True)
    if isinstance(private, Optional):
        private = defs.get('repo_private') or Optional.extract(private)
    if isinstance(repo_type, Optional):
        repo_type = defs.get('repo_type')
    if isinstance(enable_statistics, Optional):
        enable_statistics = defs.get('repo_enable_statistics')
    if isinstance(enable_locking, Optional):
        enable_locking = defs.get('repo_enable_locking')
    if isinstance(enable_downloads, Optional):
        enable_downloads = defs.get('repo_enable_downloads')

    clone_uri = Optional.extract(clone_uri)
    description = Optional.extract(description)
    landing_rev = Optional.extract(landing_rev)
    copy_permissions = Optional.extract(copy_permissions)

    try:
        # create structure of groups and return the last group
        repo_group = map_groups(repo_name)
        data = {
            'repo_name': repo_name_cleaned,
            'repo_name_full': repo_name,
            'repo_type': repo_type,
            'repo_description': description,
            'owner': owner,
            'repo_private': private,
            'clone_uri': clone_uri,
            'repo_group': repo_group.group_id if repo_group else None,
            'repo_landing_rev': landing_rev,
            'enable_statistics': enable_statistics,
            'enable_locking': enable_locking,
            'enable_downloads': enable_downloads,
            'repo_copy_permissions': copy_permissions,
        }

        if repo_type not in BACKENDS.keys():
            raise Exception("Invalid backend type %s" % repo_type)
        task = RepoModel().create(form_data=data, cur_user=owner)
        from celery.result import BaseAsyncResult
        task_id = None
        if isinstance(task, BaseAsyncResult):
            task_id = task.task_id
        # no commit, it's done in RepoModel, or async via celery
        return {
            'msg': "Created new repository `%s`" % (repo_name,),
            'success': True,  # cannot return the repo data here since fork
            # cann be done async
            'task': task_id
        }
    except Exception:
        log.exception(
            u"Exception while trying to create the repository %s",
            repo_name)
        raise JSONRPCError(
            'failed to create repository `%s`' % (repo_name,))


@jsonrpc_method()
def add_field_to_repo(request, apiuser, repoid, key, label=Optional(''),
                      description=Optional('')):
    """
    Adds an extra field to a repository.

    This command can only be run using an |authtoken| with at least
    write permissions to the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository id.
    :type repoid: str or int
    :param key: Create a unique field key for this repository.
    :type key: str
    :param label:
    :type label: Optional(str)
    :param description:
    :type description: Optional(str)
    """
    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    label = Optional.extract(label) or key
    description = Optional.extract(description)

    field = RepositoryField.get_by_key_name(key, repo)
    if field:
        raise JSONRPCError('Field with key '
                           '`%s` exists for repo `%s`' % (key, repoid))

    try:
        RepoModel().add_repo_field(repo, key, field_label=label,
                                   field_desc=description)
        Session().commit()
        return {
            'msg': "Added new repository field `%s`" % (key,),
            'success': True,
        }
    except Exception:
        log.exception("Exception occurred while trying to add field to repo")
        raise JSONRPCError(
            'failed to create new field for repository `%s`' % (repoid,))


@jsonrpc_method()
def remove_field_from_repo(request, apiuser, repoid, key):
    """
    Removes an extra field from a repository.

    This command can only be run using an |authtoken| with at least
    write permissions to the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param key: Set the unique field key for this repository.
    :type key: str
    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    field = RepositoryField.get_by_key_name(key, repo)
    if not field:
        raise JSONRPCError('Field with key `%s` does not '
                           'exists for repo `%s`' % (key, repoid))

    try:
        RepoModel().delete_repo_field(repo, field_key=key)
        Session().commit()
        return {
            'msg': "Deleted repository field `%s`" % (key,),
            'success': True,
        }
    except Exception:
        log.exception(
            "Exception occurred while trying to delete field from repo")
        raise JSONRPCError(
            'failed to delete field for repository `%s`' % (repoid,))


@jsonrpc_method()
def update_repo(request, apiuser, repoid, name=Optional(None),
                owner=Optional(OAttr('apiuser')),
                group=Optional(None),
                fork_of=Optional(None),
                description=Optional(''), private=Optional(False),
                clone_uri=Optional(None), landing_rev=Optional('rev:tip'),
                enable_statistics=Optional(False),
                enable_locking=Optional(False),
                enable_downloads=Optional(False),
                fields=Optional('')):
    """
    Updates a repository with the given information.

    This command can only be run using an |authtoken| with at least
    write permissions to the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: repository name or repository ID.
    :type repoid: str or int
    :param name: Update the |repo| name.
    :type name: str
    :param owner: Set the |repo| owner.
    :type owner: str
    :param group: Set the |repo| group the |repo| belongs to.
    :type group: str
    :param fork_of: Set the master |repo| name.
    :type fork_of: str
    :param description: Update the |repo| description.
    :type description: str
    :param private: Set the |repo| as private. (True | False)
    :type private: bool
    :param clone_uri: Update the |repo| clone URI.
    :type clone_uri: str
    :param landing_rev: Set the |repo| landing revision. Default is
        ``tip``.
    :type landing_rev: str
    :param enable_statistics: Enable statistics on the |repo|,
        (True | False).
    :type enable_statistics: bool
    :param enable_locking: Enable |repo| locking.
    :type enable_locking: bool
    :param enable_downloads: Enable downloads from the |repo|,
        (True | False).
    :type enable_downloads: bool
    :param fields: Add extra fields to the |repo|. Use the following
        example format: ``field_key=field_val,field_key2=fieldval2``.
        Escape ', ' with \,
    :type fields: str
    """
    repo = get_repo_or_error(repoid)
    include_secrets = False
    if has_superadmin_permission(apiuser):
        include_secrets = True
    else:
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    updates = {
        # update function requires this.
        'repo_name': repo.just_name
    }
    repo_group = group
    if not isinstance(repo_group, Optional):
        repo_group = get_repo_group_or_error(repo_group)
        repo_group = repo_group.group_id

    repo_fork_of = fork_of
    if not isinstance(repo_fork_of, Optional):
        repo_fork_of = get_repo_or_error(repo_fork_of)
        repo_fork_of = repo_fork_of.repo_id

    try:
        store_update(updates, name, 'repo_name')
        store_update(updates, repo_group, 'repo_group')
        store_update(updates, repo_fork_of, 'fork_id')
        store_update(updates, owner, 'user')
        store_update(updates, description, 'repo_description')
        store_update(updates, private, 'repo_private')
        store_update(updates, clone_uri, 'clone_uri')
        store_update(updates, landing_rev, 'repo_landing_rev')
        store_update(updates, enable_statistics, 'repo_enable_statistics')
        store_update(updates, enable_locking, 'repo_enable_locking')
        store_update(updates, enable_downloads, 'repo_enable_downloads')

        # extra fields
        fields = parse_args(Optional.extract(fields), key_prefix='ex_')
        if fields:
            updates.update(fields)

        RepoModel().update(repo, **updates)
        Session().commit()
        return {
            'msg': 'updated repo ID:%s %s' % (
                repo.repo_id, repo.repo_name),
            'repository': repo.get_api_data(
                include_secrets=include_secrets)
        }
    except Exception:
        log.exception(
            u"Exception while trying to update the repository %s",
            repoid)
        raise JSONRPCError('failed to update repo `%s`' % repoid)


@jsonrpc_method()
def fork_repo(request, apiuser, repoid, fork_name,
              owner=Optional(OAttr('apiuser')),
              description=Optional(''), copy_permissions=Optional(False),
              private=Optional(False), landing_rev=Optional('rev:tip')):
    """
    Creates a fork of the specified |repo|.

    * If using |RCE| with Celery this will immediately return a success
      message, even though the fork will be created asynchronously.

    This command can only be run using an |authtoken| with fork
    permissions on the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set repository name or repository ID.
    :type repoid: str or int
    :param fork_name: Set the fork name.
    :type fork_name: str
    :param owner: Set the fork owner.
    :type owner: str
    :param description: Set the fork descripton.
    :type description: str
    :param copy_permissions: Copy permissions from parent |repo|. The
        default is False.
    :type copy_permissions: bool
    :param private: Make the fork private. The default is False.
    :type private: bool
    :param landing_rev: Set the landing revision. The default is tip.

    Example output:

    .. code-block:: bash

        id : <id_for_response>
        api_key : "<api_key>"
        args:     {
                    "repoid" :          "<reponame or repo_id>",
                    "fork_name":        "<forkname>",
                    "owner":            "<username or user_id = Optional(=apiuser)>",
                    "description":      "<description>",
                    "copy_permissions": "<bool>",
                    "private":          "<bool>",
                    "landing_rev":      "<landing_rev>"
                  }

    Example error output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg": "Created fork of `<reponame>` as `<forkname>`",
                  "success": true,
                  "task": "<celery task id or None if done sync>"
                }
        error:  null

    """
    if not has_superadmin_permission(apiuser):
        if not HasPermissionAnyApi('hg.fork.repository')(user=apiuser):
            raise JSONRPCForbidden()

    repo = get_repo_or_error(repoid)
    repo_name = repo.repo_name

    (fork_name_cleaned,
     parent_group_name) = RepoGroupModel()._get_group_name_and_parent(
        fork_name)

    if not has_superadmin_permission(apiuser):
        # check if we have at least read permission for
        # this repo that we fork !
        _perms = (
            'repository.admin', 'repository.write', 'repository.read')
        has_repo_permissions(apiuser, repoid, repo, _perms)

        if not isinstance(owner, Optional):
            # forbid setting owner for non super admins
            raise JSONRPCError(
                'Only RhodeCode admin can specify `owner` param'
            )
        # check if we have a create.repo permission if not maybe the parent
        # group permission
        if not HasPermissionAnyApi('hg.create.repository')(user=apiuser):
            if parent_group_name:
                repogroupid = parent_group_name
                repo_group = get_repo_group_or_error(parent_group_name)

                _perms = ('group.admin',)
                if not HasRepoGroupPermissionAnyApi(*_perms)(
                        user=apiuser, group_name=repo_group.group_name):
                    raise JSONRPCError(
                        'repository group `%s` does not exist' % (
                            repogroupid,))
            else:
                raise JSONRPCForbidden()

    _repo = RepoModel().get_by_repo_name(fork_name)
    if _repo:
        type_ = 'fork' if _repo.fork else 'repo'
        raise JSONRPCError("%s `%s` already exist" % (type_, fork_name))

    if isinstance(owner, Optional):
        owner = apiuser.user_id

    owner = get_user_or_error(owner)

    try:
        # create structure of groups and return the last group
        repo_group = map_groups(fork_name)
        form_data = {
            'repo_name': fork_name_cleaned,
            'repo_name_full': fork_name,
            'repo_group': repo_group.group_id if repo_group else None,
            'repo_type': repo.repo_type,
            'description': Optional.extract(description),
            'private': Optional.extract(private),
            'copy_permissions': Optional.extract(copy_permissions),
            'landing_rev': Optional.extract(landing_rev),
            'fork_parent_id': repo.repo_id,
        }

        task = RepoModel().create_fork(form_data, cur_user=owner)
        # no commit, it's done in RepoModel, or async via celery
        from celery.result import BaseAsyncResult
        task_id = None
        if isinstance(task, BaseAsyncResult):
            task_id = task.task_id
        return {
            'msg': 'Created fork of `%s` as `%s`' % (
                repo.repo_name, fork_name),
            'success': True,  # cannot return the repo data here since fork
            # can be done async
            'task': task_id
        }
    except Exception:
        log.exception("Exception occurred while trying to fork a repo")
        raise JSONRPCError(
            'failed to fork repository `%s` as `%s`' % (
                repo_name, fork_name))


@jsonrpc_method()
def delete_repo(request, apiuser, repoid, forks=Optional('')):
    """
    Deletes a repository.

    * When the `forks` parameter is set it's possible to detach or delete
      forks of deleted repository.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param forks: Set to `detach` or `delete` forks from the |repo|.
    :type forks: Optional(str)

    Example error output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg": "Deleted repository `<reponame>`",
                  "success": true
                }
        error:  null
    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    try:
        handle_forks = Optional.extract(forks)
        _forks_msg = ''
        _forks = [f for f in repo.forks]
        if handle_forks == 'detach':
            _forks_msg = ' ' + 'Detached %s forks' % len(_forks)
        elif handle_forks == 'delete':
            _forks_msg = ' ' + 'Deleted %s forks' % len(_forks)
        elif _forks:
            raise JSONRPCError(
                'Cannot delete `%s` it still contains attached forks' %
                (repo.repo_name,)
            )

        RepoModel().delete(repo, forks=forks)
        Session().commit()
        return {
            'msg': 'Deleted repository `%s`%s' % (
                repo.repo_name, _forks_msg),
            'success': True
        }
    except Exception:
        log.exception("Exception occurred while trying to delete repo")
        raise JSONRPCError(
            'failed to delete repository `%s`' % (repo.repo_name,)
        )


#TODO: marcink, change name ?
@jsonrpc_method()
def invalidate_cache(request, apiuser, repoid, delete_keys=Optional(False)):
    """
    Invalidates the cache for the specified repository.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Sets the repository name or repository ID.
    :type repoid: str or int
    :param delete_keys: This deletes the invalidated keys instead of
        just flagging them.
    :type delete_keys: Optional(``True`` | ``False``)

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        'msg': Cache for repository `<repository name>` was invalidated,
        'repository': <repository name>
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error : {
         'Error occurred during cache invalidation action'
      }

    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin', 'repository.write',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    delete = Optional.extract(delete_keys)
    try:
        ScmModel().mark_for_invalidation(repo.repo_name, delete=delete)
        return {
            'msg': 'Cache for repository `%s` was invalidated' % (repoid,),
            'repository': repo.repo_name
        }
    except Exception:
        log.exception(
            "Exception occurred while trying to invalidate repo cache")
        raise JSONRPCError(
            'Error occurred during cache invalidation action'
        )


#TODO: marcink, change name ?
@jsonrpc_method()
def lock(request, apiuser, repoid, locked=Optional(None),
         userid=Optional(OAttr('apiuser'))):
    """
    Sets the lock state of the specified |repo| by the given user.
    From more information, see :ref:`repo-locking`.

    * If the ``userid`` option is not set, the repository is locked to the
      user who called the method.
    * If the ``locked`` parameter is not set, the current lock state of the
      repository is displayed.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Sets the repository name or repository ID.
    :type repoid: str or int
    :param locked: Sets the lock state.
    :type locked: Optional(``True`` | ``False``)
    :param userid: Set the repository lock to this user.
    :type userid: Optional(str or int)

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        'repo': '<reponame>',
        'locked': <bool: lock state>,
        'locked_since': <int: lock timestamp>,
        'locked_by': <username of person who made the lock>,
        'lock_reason': <str: reason for locking>,
        'lock_state_changed': <bool: True if lock state has been changed in this request>,
        'msg': 'Repo `<reponame>` locked by `<username>` on <timestamp>.'
        or
        'msg': 'Repo `<repository name>` not locked.'
        or
        'msg': 'User `<user name>` set lock state for repo `<repository name>` to `<new lock state>`'
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        'Error occurred locking repository `<reponame>`
      }
    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        # check if we have at least write permission for this repo !
        _perms = ('repository.admin', 'repository.write',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

        # make sure normal user does not pass someone else userid,
        # he is not allowed to do that
        if not isinstance(userid, Optional) and userid != apiuser.user_id:
            raise JSONRPCError('userid is not the same as your user')

    if isinstance(userid, Optional):
        userid = apiuser.user_id

    user = get_user_or_error(userid)

    if isinstance(locked, Optional):
        lockobj = repo.locked

        if lockobj[0] is None:
            _d = {
                'repo': repo.repo_name,
                'locked': False,
                'locked_since': None,
                'locked_by': None,
                'lock_reason': None,
                'lock_state_changed': False,
                'msg': 'Repo `%s` not locked.' % repo.repo_name
            }
            return _d
        else:
            _user_id, _time, _reason = lockobj
            lock_user = get_user_or_error(userid)
            _d = {
                'repo': repo.repo_name,
                'locked': True,
                'locked_since': _time,
                'locked_by': lock_user.username,
                'lock_reason': _reason,
                'lock_state_changed': False,
                'msg': ('Repo `%s` locked by `%s` on `%s`.'
                        % (repo.repo_name, lock_user.username,
                           json.dumps(time_to_datetime(_time))))
            }
            return _d

    # force locked state through a flag
    else:
        locked = str2bool(locked)
        lock_reason = Repository.LOCK_API
        try:
            if locked:
                lock_time = time.time()
                Repository.lock(repo, user.user_id, lock_time, lock_reason)
            else:
                lock_time = None
                Repository.unlock(repo)
            _d = {
                'repo': repo.repo_name,
                'locked': locked,
                'locked_since': lock_time,
                'locked_by': user.username,
                'lock_reason': lock_reason,
                'lock_state_changed': True,
                'msg': ('User `%s` set lock state for repo `%s` to `%s`'
                        % (user.username, repo.repo_name, locked))
            }
            return _d
        except Exception:
            log.exception(
                "Exception occurred while trying to lock repository")
            raise JSONRPCError(
                'Error occurred locking repository `%s`' % repo.repo_name
            )


@jsonrpc_method()
def comment_commit(
        request, apiuser, repoid, commit_id, message,
        userid=Optional(OAttr('apiuser')), status=Optional(None)):
    """
    Set a commit comment, and optionally change the status of the commit.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param commit_id: Specify the commit_id for which to set a comment.
    :type commit_id: str
    :param message: The comment text.
    :type message: str
    :param userid: Set the user name of the comment creator.
    :type userid: Optional(str or int)
    :param status: status, one of 'not_reviewed', 'approved', 'rejected',
       'under_review'
    :type status: str

    Example error output:

    .. code-block:: json

        {
            "id" : <id_given_in_input>,
            "result" : {
                "msg": "Commented on commit `<commit_id>` for repository `<repoid>`",
                "status_change": null or <status>,
                "success": true
            },
            "error" :  null
        }

    """
    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.read', 'repository.write', 'repository.admin')
        has_repo_permissions(apiuser, repoid, repo, _perms)

    if isinstance(userid, Optional):
        userid = apiuser.user_id

    user = get_user_or_error(userid)
    status = Optional.extract(status)

    allowed_statuses = [x[0] for x in ChangesetStatus.STATUSES]
    if status and status not in allowed_statuses:
        raise JSONRPCError('Bad status, must be on '
                           'of %s got %s' % (allowed_statuses, status,))

    try:
        rc_config = SettingsModel().get_all_settings()
        renderer = rc_config.get('rhodecode_markup_renderer', 'rst')

        comm = ChangesetCommentsModel().create(
            message, repo, user, revision=commit_id, status_change=status,
            renderer=renderer)
        if status:
            # also do a status change
            try:
                ChangesetStatusModel().set_status(
                    repo, status, user, comm, revision=commit_id,
                    dont_allow_on_closed_pull_request=True
                )
            except StatusChangeOnClosedPullRequestError:
                log.exception(
                    "Exception occurred while trying to change repo commit status")
                msg = ('Changing status on a changeset associated with '
                       'a closed pull request is not allowed')
                raise JSONRPCError(msg)

        Session().commit()
        return {
            'msg': (
                'Commented on commit `%s` for repository `%s`' % (
                    comm.revision, repo.repo_name)),
            'status_change': status,
            'success': True,
        }
    except JSONRPCError:
        # catch any inside errors, and re-raise them to prevent from
        # below global catch to silence them
        raise
    except Exception:
        log.exception("Exception occurred while trying to comment on commit")
        raise JSONRPCError(
            'failed to set comment on repository `%s`' % (repo.repo_name,)
        )


@jsonrpc_method()
def grant_user_permission(request, apiuser, repoid, userid, perm):
    """
    Grant permissions for the specified user on the given repository,
    or update existing permissions if found.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param userid: Set the user name.
    :type userid: str
    :param perm: Set the user permissions, using the following format
        ``(repository.(none|read|write|admin))``
    :type perm: str

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "Granted perm: `<perm>` for user: `<username>` in repo: `<reponame>`",
                  "success": true
                }
        error:  null
    """

    repo = get_repo_or_error(repoid)
    user = get_user_or_error(userid)
    perm = get_perm_or_error(perm)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    try:

        RepoModel().grant_user_permission(repo=repo, user=user, perm=perm)

        Session().commit()
        return {
            'msg': 'Granted perm: `%s` for user: `%s` in repo: `%s`' % (
                perm.permission_name, user.username, repo.repo_name
            ),
            'success': True
        }
    except Exception:
        log.exception(
            "Exception occurred while trying edit permissions for repo")
        raise JSONRPCError(
            'failed to edit permission for user: `%s` in repo: `%s`' % (
                userid, repoid
            )
        )


@jsonrpc_method()
def revoke_user_permission(request, apiuser, repoid, userid):
    """
    Revoke permission for a user on the specified repository.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param userid: Set the user name of revoked user.
    :type userid: str or int

    Example error output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "Revoked perm for user: `<username>` in repo: `<reponame>`",
                  "success": true
                }
        error:  null
    """

    repo = get_repo_or_error(repoid)
    user = get_user_or_error(userid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    try:
        RepoModel().revoke_user_permission(repo=repo, user=user)
        Session().commit()
        return {
            'msg': 'Revoked perm for user: `%s` in repo: `%s`' % (
                user.username, repo.repo_name
            ),
            'success': True
        }
    except Exception:
        log.exception(
            "Exception occurred while trying revoke permissions to repo")
        raise JSONRPCError(
            'failed to edit permission for user: `%s` in repo: `%s`' % (
                userid, repoid
            )
        )


@jsonrpc_method()
def grant_user_group_permission(request, apiuser, repoid, usergroupid, perm):
    """
    Grant permission for a user group on the specified repository,
    or update existing permissions.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param usergroupid: Specify the ID of the user group.
    :type usergroupid: str or int
    :param perm: Set the user group permissions using the following
        format: (repository.(none|read|write|admin))
    :type perm: str

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg" : "Granted perm: `<perm>` for group: `<usersgroupname>` in repo: `<reponame>`",
        "success": true

      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to edit permission for user group: `<usergroup>` in repo `<repo>`'
      }

    """

    repo = get_repo_or_error(repoid)
    perm = get_perm_or_error(perm)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have at least read permission for this user group !
        _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    try:
        RepoModel().grant_user_group_permission(
            repo=repo, group_name=user_group, perm=perm)

        Session().commit()
        return {
            'msg': 'Granted perm: `%s` for user group: `%s` in '
                   'repo: `%s`' % (
                       perm.permission_name, user_group.users_group_name,
                       repo.repo_name
                   ),
            'success': True
        }
    except Exception:
        log.exception(
            "Exception occurred while trying change permission on repo")
        raise JSONRPCError(
            'failed to edit permission for user group: `%s` in '
            'repo: `%s`' % (
                usergroupid, repo.repo_name
            )
        )


@jsonrpc_method()
def revoke_user_group_permission(request, apiuser, repoid, usergroupid):
    """
    Revoke the permissions of a user group on a given repository.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param usergroupid: Specify the user group ID.
    :type usergroupid: str or int

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "Revoked perm for group: `<usersgroupname>` in repo: `<reponame>`",
                  "success": true
                }
        error:  null
    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have at least read permission for this user group !
        _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    try:
        RepoModel().revoke_user_group_permission(
            repo=repo, group_name=user_group)

        Session().commit()
        return {
            'msg': 'Revoked perm for user group: `%s` in repo: `%s`' % (
                user_group.users_group_name, repo.repo_name
            ),
            'success': True
        }
    except Exception:
        log.exception("Exception occurred while trying revoke "
                      "user group permission on repo")
        raise JSONRPCError(
            'failed to edit permission for user group: `%s` in '
            'repo: `%s`' % (
                user_group.users_group_name, repo.repo_name
            )
        )


@jsonrpc_method()
def pull(request, apiuser, repoid):
    """
    Triggers a pull on the given repository from a remote location. You
    can use this to keep remote repositories up-to-date.

    This command can only be run using an |authtoken| with admin
    rights to the specified repository. For more information,
    see :ref:`config-token-ref`.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: The repository name or repository ID.
    :type repoid: str or int

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "Pulled from `<repository name>`"
        "repository": "<repository name>"
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "Unable to pull changes from `<reponame>`"
      }

    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    try:
        ScmModel().pull_changes(repo.repo_name, apiuser.username)
        return {
            'msg': 'Pulled from `%s`' % repo.repo_name,
            'repository': repo.repo_name
        }
    except Exception:
        log.exception("Exception occurred while trying to "
                      "pull changes from remote location")
        raise JSONRPCError(
            'Unable to pull changes from `%s`' % repo.repo_name
        )


@jsonrpc_method()
def strip(request, apiuser, repoid, revision, branch):
    """
    Strips the given revision from the specified repository.

    * This will remove the revision and all of its decendants.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: The repository name or repository ID.
    :type repoid: str or int
    :param revision: The revision you wish to strip.
    :type revision: str
    :param branch: The branch from which to strip the revision.
    :type branch: str

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "'Stripped commit <commit_hash> from repo `<repository name>`'"
        "repository": "<repository name>"
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "Unable to strip commit <commit_hash> from repo `<repository name>`"
      }

    """

    repo = get_repo_or_error(repoid)
    if not has_superadmin_permission(apiuser):
        _perms = ('repository.admin',)
        has_repo_permissions(apiuser, repoid, repo, _perms)

    try:
        ScmModel().strip(repo, revision, branch)
        return {
            'msg': 'Stripped commit %s from repo `%s`' % (
                revision, repo.repo_name),
            'repository': repo.repo_name
        }
    except Exception:
        log.exception("Exception while trying to strip")
        raise JSONRPCError(
            'Unable to strip commit %s from repo `%s`' % (
                revision, repo.repo_name)
        )
