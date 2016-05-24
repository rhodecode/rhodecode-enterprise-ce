# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016  RhodeCode GmbH
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
JSON RPC utils
"""

import collections
import logging

from rhodecode.api.exc import JSONRPCError
from rhodecode.lib.auth import HasPermissionAnyApi, HasRepoPermissionAnyApi
from rhodecode.lib.utils import safe_unicode
from rhodecode.controllers.utils import get_commit_from_ref_name
from rhodecode.lib.vcs.exceptions import RepositoryError

log = logging.getLogger(__name__)




class OAttr(object):
    """
    Special Option that defines other attribute, and can default to them

    Example::

        def test(apiuser, userid=Optional(OAttr('apiuser')):
            user = Optional.extract(userid, evaluate_locals=local())
            #if we pass in userid, we get it, else it will default to apiuser
            #attribute
    """

    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __repr__(self):
        return '<OptionalAttr:%s>' % self.attr_name

    def __call__(self):
        return self


class Optional(object):
    """
    Defines an optional parameter::

        param = param.getval() if isinstance(param, Optional) else param
        param = param() if isinstance(param, Optional) else param

    is equivalent of::

        param = Optional.extract(param)

    """

    def __init__(self, type_):
        self.type_ = type_

    def __repr__(self):
        return '<Optional:%s>' % self.type_.__repr__()

    def __call__(self):
        return self.getval()

    def getval(self, evaluate_locals=None):
        """
        returns value from this Optional instance
        """
        if isinstance(self.type_, OAttr):
            param_name = self.type_.attr_name
            if evaluate_locals:
                return evaluate_locals[param_name]
            # use params name
            return param_name
        return self.type_

    @classmethod
    def extract(cls, val, evaluate_locals=None):
        """
        Extracts value from Optional() instance

        :param val:
        :return: original value if it's not Optional instance else
            value of instance
        """
        if isinstance(val, cls):
            return val.getval(evaluate_locals)
        return val


def parse_args(cli_args, key_prefix=''):
    from rhodecode.lib.utils2 import (escape_split)
    kwargs = collections.defaultdict(dict)
    for el in escape_split(cli_args, ','):
        kv = escape_split(el, '=', 1)
        if len(kv) == 2:
            k, v = kv
            kwargs[key_prefix + k] = v
    return kwargs


def get_origin(obj):
    """
    Get origin of permission from object.

    :param obj:
    """
    origin = 'permission'

    if getattr(obj, 'owner_row', '') and getattr(obj, 'admin_row', ''):
        # admin and owner case, maybe we should use dual string ?
        origin = 'owner'
    elif getattr(obj, 'owner_row', ''):
        origin = 'owner'
    elif getattr(obj, 'admin_row', ''):
        origin = 'super-admin'
    return origin


def store_update(updates, attr, name):
    """
    Stores param in updates dict if it's not instance of Optional
    allows easy updates of passed in params
    """
    if not isinstance(attr, Optional):
        updates[name] = attr


def has_superadmin_permission(apiuser):
    """
    Return True if apiuser is admin or return False

    :param apiuser:
    """
    if HasPermissionAnyApi('hg.admin')(user=apiuser):
        return True
    return False


def has_repo_permissions(apiuser, repoid, repo, perms):
    """
    Raise JsonRPCError if apiuser is not authorized or return True

    :param apiuser:
    :param repoid:
    :param repo:
    :param perms:
    """
    if not HasRepoPermissionAnyApi(*perms)(
            user=apiuser, repo_name=repo.repo_name):
        raise JSONRPCError(
            'repository `%s` does not exist' % repoid)

    return True


def get_user_or_error(userid):
    """
    Get user by id or name or return JsonRPCError if not found

    :param userid:
    """
    from rhodecode.model.user import UserModel

    user_model = UserModel()
    try:
        user = user_model.get_user(int(userid))
    except ValueError:
        user = user_model.get_by_username(userid)

    if user is None:
        raise JSONRPCError("user `%s` does not exist" % (userid,))
    return user


def get_repo_or_error(repoid):
    """
    Get repo by id or name or return JsonRPCError if not found

    :param repoid:
    """
    from rhodecode.model.repo import RepoModel

    repo = RepoModel().get_repo(repoid)
    if repo is None:
        raise JSONRPCError('repository `%s` does not exist' % (repoid,))
    return repo


def get_repo_group_or_error(repogroupid):
    """
    Get repo group by id or name or return JsonRPCError if not found

    :param repogroupid:
    """
    from rhodecode.model.repo_group import RepoGroupModel

    repo_group = RepoGroupModel()._get_repo_group(repogroupid)
    if repo_group is None:
        raise JSONRPCError(
            'repository group `%s` does not exist' % (repogroupid,))
    return repo_group


def get_user_group_or_error(usergroupid):
    """
    Get user group by id or name or return JsonRPCError if not found

    :param usergroupid:
    """
    from rhodecode.model.user_group import UserGroupModel

    user_group = UserGroupModel().get_group(usergroupid)
    if user_group is None:
        raise JSONRPCError('user group `%s` does not exist' % (usergroupid,))
    return user_group


def get_perm_or_error(permid, prefix=None):
    """
    Get permission by id or name or return JsonRPCError if not found

    :param permid:
    """
    from rhodecode.model.permission import PermissionModel

    perm = PermissionModel.cls.get_by_key(permid)
    if perm is None:
        raise JSONRPCError('permission `%s` does not exist' % (permid,))
    if prefix:
        if not perm.permission_name.startswith(prefix):
            raise JSONRPCError('permission `%s` is invalid, '
                               'should start with %s' % (permid, prefix))
    return perm


def get_gist_or_error(gistid):
    """
    Get gist by id or gist_access_id or return JsonRPCError if not found

    :param gistid:
    """
    from rhodecode.model.gist import GistModel

    gist = GistModel.cls.get_by_access_id(gistid)
    if gist is None:
        raise JSONRPCError('gist `%s` does not exist' % (gistid,))
    return gist


def get_pull_request_or_error(pullrequestid):
    """
    Get pull request by id or return JsonRPCError if not found

    :param pullrequestid:
    """
    from rhodecode.model.pull_request import PullRequestModel

    try:
        pull_request = PullRequestModel().get(int(pullrequestid))
    except ValueError:
        raise JSONRPCError('pullrequestid must be an integer')
    if not pull_request:
        raise JSONRPCError('pull request `%s` does not exist' % (
            pullrequestid,))
    return pull_request


def build_commit_data(commit, detail_level):
    parsed_diff = []
    if detail_level == 'extended':
        for f in commit.added:
            parsed_diff.append(_get_commit_dict(filename=f.path, op='A'))
        for f in commit.changed:
            parsed_diff.append(_get_commit_dict(filename=f.path, op='M'))
        for f in commit.removed:
            parsed_diff.append(_get_commit_dict(filename=f.path, op='D'))

    elif detail_level == 'full':
        from rhodecode.lib.diffs import DiffProcessor
        diff_processor = DiffProcessor(commit.diff())
        for dp in diff_processor.prepare():
            del dp['stats']['ops']
            _stats = dp['stats']
            parsed_diff.append(_get_commit_dict(
                filename=dp['filename'], op=dp['operation'],
                new_revision=dp['new_revision'],
                old_revision=dp['old_revision'],
                raw_diff=dp['raw_diff'], stats=_stats))

    return parsed_diff


def get_commit_or_error(ref, repo):
    try:
        ref_type, _, ref_hash = ref.split(':')
    except ValueError:
        raise JSONRPCError(
            'Ref `{ref}` given in a wrong format. Please check the API'
            ' documentation for more details'.format(ref=ref))
    try:
        # TODO: dan: refactor this to use repo.scm_instance().get_commit()
        # once get_commit supports ref_types
        return get_commit_from_ref_name(repo, ref_hash)
    except RepositoryError:
        raise JSONRPCError('Ref `{ref}` does not exist'.format(ref=ref))


def resolve_ref_or_error(ref, repo):
    def _parse_ref(type_, name, hash_=None):
        return type_, name, hash_

    try:
        ref_type, ref_name, ref_hash = _parse_ref(*ref.split(':'))
    except TypeError:
        raise JSONRPCError(
            'Ref `{ref}` given in a wrong format. Please check the API'
            ' documentation for more details'.format(ref=ref))

    try:
        ref_hash = ref_hash or _get_ref_hash(repo, ref_type, ref_name)
    except (KeyError, ValueError):
        raise JSONRPCError(
            'The specified {type} `{name}` does not exist'.format(
                type=ref_type, name=ref_name))

    return ':'.join([ref_type, ref_name, ref_hash])


def _get_commit_dict(
        filename, op, new_revision=None, old_revision=None,
        raw_diff=None, stats=None):
    if stats is None:
        stats = {
            "added": None,
            "binary": None,
            "deleted": None
        }
    return {
        "filename": safe_unicode(filename),
        "op": op,

        # extra details
        "new_revision": new_revision,
        "old_revision": old_revision,

        "raw_diff": raw_diff,
        "stats": stats
    }


# TODO: mikhail: Think about moving this function to some library
def _get_ref_hash(repo, type_, name):
    vcs_repo = repo.scm_instance()
    if type_ == 'branch' and vcs_repo.alias in ('hg', 'git'):
        return vcs_repo.branches[name]
    elif type_ == 'bookmark' and vcs_repo.alias == 'hg':
        return vcs_repo.bookmarks[name]
    else:
        raise ValueError()
