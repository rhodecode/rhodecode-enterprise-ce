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
Base module for all VCS systems
"""

import collections
import datetime
import itertools
import logging
import os
import time
import warnings

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.utils2 import safe_str, safe_unicode
from rhodecode.lib.vcs import connection
from rhodecode.lib.vcs.utils import author_name, author_email
from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import (
    CommitError, EmptyRepositoryError, NodeAlreadyAddedError,
    NodeAlreadyChangedError, NodeAlreadyExistsError, NodeAlreadyRemovedError,
    NodeDoesNotExistError, NodeNotChangedError, VCSError,
    ImproperArchiveTypeError, BranchDoesNotExistError, CommitDoesNotExistError,
    RepositoryError)


log = logging.getLogger(__name__)


FILEMODE_DEFAULT = 0100644
FILEMODE_EXECUTABLE = 0100755

Reference = collections.namedtuple('Reference', ('type', 'name', 'commit_id'))
MergeResponse = collections.namedtuple(
    'MergeResponse',
    ('possible', 'executed', 'merge_commit_id', 'failure_reason'))


class MergeFailureReason(object):
    """
    Enumeration with all the reasons why the server side merge could fail.

    DO NOT change the number of the reasons, as they may be stored in the
    database.

    Changing the name of a reason is acceptable and encouraged to deprecate old
    reasons.
    """

    # Everything went well.
    NONE = 0

    # An unexpected exception was raised. Check the logs for more details.
    UNKNOWN = 1

    # The merge was not successful, there are conflicts.
    MERGE_FAILED = 2

    # The merge succeeded but we could not push it to the target repository.
    PUSH_FAILED = 3

    # The specified target is not a head in the target repository.
    TARGET_IS_NOT_HEAD = 4

    # The source repository contains more branches than the target. Pushing
    # the merge will create additional branches in the target.
    HG_SOURCE_HAS_MORE_BRANCHES = 5

    # The target reference has multiple heads. That does not allow to correctly
    # identify the target location. This could only happen for mercurial
    # branches.
    HG_TARGET_HAS_MULTIPLE_HEADS = 6

    # The target repository is locked
    TARGET_IS_LOCKED = 7

    # A involved commit could not be found.
    MISSING_COMMIT = 8


class BaseRepository(object):
    """
    Base Repository for final backends

    .. attribute:: DEFAULT_BRANCH_NAME

       name of default branch (i.e. "trunk" for svn, "master" for git etc.

    .. attribute:: commit_ids

       list of all available commit ids, in ascending order

    .. attribute:: path

       absolute path to the repository

    .. attribute:: bookmarks

       Mapping from name to :term:`Commit ID` of the bookmark. Empty in case
       there are no bookmarks or the backend implementation does not support
       bookmarks.

    .. attribute:: tags

       Mapping from name to :term:`Commit ID` of the tag.

    """

    DEFAULT_BRANCH_NAME = None
    DEFAULT_CONTACT = u"Unknown"
    DEFAULT_DESCRIPTION = u"unknown"
    EMPTY_COMMIT_ID = '0' * 40

    path = None

    def __init__(self, repo_path, config=None, create=False, **kwargs):
        """
        Initializes repository. Raises RepositoryError if repository could
        not be find at the given ``repo_path`` or directory at ``repo_path``
        exists and ``create`` is set to True.

        :param repo_path: local path of the repository
        :param config: repository configuration
        :param create=False: if set to True, would try to create repository.
        :param src_url=None: if set, should be proper url from which repository
          would be cloned; requires ``create`` parameter to be set to True -
          raises RepositoryError if src_url is set and create evaluates to
          False
        """
        raise NotImplementedError

    def __repr__(self):
        return '<%s at %s>' % (self.__class__.__name__, self.path)

    def __len__(self):
        return self.count()

    def __eq__(self, other):
        same_instance = isinstance(other, self.__class__)
        return same_instance and other.path == self.path

    def __ne__(self, other):
        return not self.__eq__(other)

    @LazyProperty
    def EMPTY_COMMIT(self):
        return EmptyCommit(self.EMPTY_COMMIT_ID)

    @LazyProperty
    def alias(self):
        for k, v in settings.BACKENDS.items():
            if v.split('.')[-1] == str(self.__class__.__name__):
                return k

    @LazyProperty
    def name(self):
        return safe_unicode(os.path.basename(self.path))

    @LazyProperty
    def description(self):
        raise NotImplementedError

    def refs(self):
        """
        returns a `dict` with branches, bookmarks, tags, and closed_branches
        for this repository
        """
        raise NotImplementedError

    @LazyProperty
    def branches(self):
        """
        A `dict` which maps branch names to commit ids.
        """
        raise NotImplementedError

    @LazyProperty
    def size(self):
        """
        Returns combined size in bytes for all repository files
        """
        tip = self.get_commit()
        return tip.size

    def size_at_commit(self, commit_id):
        commit = self.get_commit(commit_id)
        return commit.size

    def is_empty(self):
        return not bool(self.commit_ids)

    @staticmethod
    def check_url(url, config):
        """
        Function will check given url and try to verify if it's a valid
        link.
        """
        raise NotImplementedError

    @staticmethod
    def is_valid_repository(path):
        """
        Check if given `path` contains a valid repository of this backend
        """
        raise NotImplementedError

    # ==========================================================================
    # COMMITS
    # ==========================================================================

    def get_commit(self, commit_id=None, commit_idx=None, pre_load=None):
        """
        Returns instance of `BaseCommit` class. If `commit_id` and `commit_idx`
        are both None, most recent commit is returned.

        :param pre_load: Optional. List of commit attributes to load.

        :raises ``EmptyRepositoryError``: if there are no commits
        """
        raise NotImplementedError

    def __iter__(self):
        for commit_id in self.commit_ids:
            yield self.get_commit(commit_id=commit_id)

    def get_commits(
            self, start_id=None, end_id=None, start_date=None, end_date=None,
            branch_name=None, pre_load=None):
        """
        Returns iterator of `BaseCommit` objects from start to end
        not inclusive. This should behave just like a list, ie. end is not
        inclusive.

        :param start_id: None or str, must be a valid commit id
        :param end_id: None or str, must be a valid commit id
        :param start_date:
        :param end_date:
        :param branch_name:
        :param pre_load:
        """
        raise NotImplementedError

    def __getitem__(self, key):
        """
        Allows index based access to the commit objects of this repository.
        """
        pre_load = ["author", "branch", "date", "message", "parents"]
        if isinstance(key, slice):
            return self._get_range(key, pre_load)
        return self.get_commit(commit_idx=key, pre_load=pre_load)

    def _get_range(self, slice_obj, pre_load):
        for commit_id in self.commit_ids.__getitem__(slice_obj):
            yield self.get_commit(commit_id=commit_id, pre_load=pre_load)

    def count(self):
        return len(self.commit_ids)

    def tag(self, name, user, commit_id=None, message=None, date=None, **opts):
        """
        Creates and returns a tag for the given ``commit_id``.

        :param name: name for new tag
        :param user: full username, i.e.: "Joe Doe <joe.doe@example.com>"
        :param commit_id: commit id for which new tag would be created
        :param message: message of the tag's commit
        :param date: date of tag's commit

        :raises TagAlreadyExistError: if tag with same name already exists
        """
        raise NotImplementedError

    def remove_tag(self, name, user, message=None, date=None):
        """
        Removes tag with the given ``name``.

        :param name: name of the tag to be removed
        :param user: full username, i.e.: "Joe Doe <joe.doe@example.com>"
        :param message: message of the tag's removal commit
        :param date: date of tag's removal commit

        :raises TagDoesNotExistError: if tag with given name does not exists
        """
        raise NotImplementedError

    def get_diff(
            self, commit1, commit2, path=None, ignore_whitespace=False,
            context=3, path1=None):
        """
        Returns (git like) *diff*, as plain text. Shows changes introduced by
        `commit2` since `commit1`.

        :param commit1: Entry point from which diff is shown. Can be
          ``self.EMPTY_COMMIT`` - in this case, patch showing all
          the changes since empty state of the repository until `commit2`
        :param commit2: Until which commit changes should be shown.
        :param path: Can be set to a path of a file to create a diff of that
          file. If `path1` is also set, this value is only associated to
          `commit2`.
        :param ignore_whitespace: If set to ``True``, would not show whitespace
          changes. Defaults to ``False``.
        :param context: How many lines before/after changed lines should be
          shown. Defaults to ``3``.
        :param path1: Can be set to a path to associate with `commit1`. This
          parameter works only for backends which support diff generation for
          different paths. Other backends will raise a `ValueError` if `path1`
          is set and has a different value than `path`.
        """
        raise NotImplementedError

    def strip(self, commit_id, branch=None):
        """
        Strip given commit_id from the repository
        """
        raise NotImplementedError

    def get_common_ancestor(self, commit_id1, commit_id2, repo2):
        """
        Return a latest common ancestor commit if one exists for this repo
        `commit_id1` vs `commit_id2` from `repo2`.

        :param commit_id1: Commit it from this repository to use as a
           target for the comparison.
        :param commit_id2: Source commit id to use for comparison.
        :param repo2: Source repository to use for comparison.
        """
        raise NotImplementedError

    def compare(self, commit_id1, commit_id2, repo2, merge, pre_load=None):
        """
        Compare this repository's revision `commit_id1` with `commit_id2`.

        Returns a tuple(commits, ancestor) that would be merged from
        `commit_id2`. Doing a normal compare (``merge=False``), ``None``
        will be returned as ancestor.

        :param commit_id1: Commit it from this repository to use as a
           target for the comparison.
        :param commit_id2: Source commit id to use for comparison.
        :param repo2: Source repository to use for comparison.
        :param merge: If set to ``True`` will do a merge compare which also
           returns the common ancestor.
        :param pre_load: Optional. List of commit attributes to load.
        """
        raise NotImplementedError

    def merge(self, target_ref, source_repo, source_ref, workspace_id,
              user_name='', user_email='', message='', dry_run=False,
              use_rebase=False):
        """
        Merge the revisions specified in `source_ref` from `source_repo`
        onto the `target_ref` of this repository.

        `source_ref` and `target_ref` are named tupls with the following
        fields `type`, `name` and `commit_id`.

        Returns a MergeResponse named tuple with the following fields
        'possible', 'executed', 'source_commit', 'target_commit',
        'merge_commit'.

        :param target_ref: `target_ref` points to the commit on top of which
            the `source_ref` should be merged.
        :param source_repo: The repository that contains the commits to be
            merged.
        :param source_ref: `source_ref` points to the topmost commit from
            the `source_repo` which should be merged.
        :param workspace_id: `workspace_id` unique identifier.
        :param user_name: Merge commit `user_name`.
        :param user_email: Merge commit `user_email`.
        :param message: Merge commit `message`.
        :param dry_run: If `True` the merge will not take place.
        :param use_rebase: If `True` commits from the source will be rebased
            on top of the target instead of being merged.
        """
        if dry_run:
            message = message or 'sample_message'
            user_email = user_email or 'user@email.com'
            user_name = user_name or 'user name'
        else:
            if not user_name:
                raise ValueError('user_name cannot be empty')
            if not user_email:
                raise ValueError('user_email cannot be empty')
            if not message:
                raise ValueError('message cannot be empty')

        shadow_repository_path = self._maybe_prepare_merge_workspace(
            workspace_id, target_ref)

        try:
            return self._merge_repo(
                shadow_repository_path, target_ref, source_repo,
                source_ref, message, user_name, user_email, dry_run=dry_run,
                use_rebase=use_rebase)
        except RepositoryError:
            log.exception(
                'Unexpected failure when running merge, dry-run=%s',
                dry_run)
            return MergeResponse(
                False, False, None, MergeFailureReason.UNKNOWN)

    def _merge_repo(self, shadow_repository_path, target_ref,
                    source_repo, source_ref, merge_message,
                    merger_name, merger_email, dry_run=False):
        """Internal implementation of merge."""
        raise NotImplementedError

    def _maybe_prepare_merge_workspace(self, workspace_id, target_ref):
        """
        Create the merge workspace.

        :param workspace_id: `workspace_id` unique identifier.
        """
        raise NotImplementedError

    def cleanup_merge_workspace(self, workspace_id):
        """
        Remove merge workspace.

        This function MUST not fail in case there is no workspace associated to
        the given `workspace_id`.

        :param workspace_id: `workspace_id` unique identifier.
        """
        raise NotImplementedError

    # ========== #
    # COMMIT API #
    # ========== #

    @LazyProperty
    def in_memory_commit(self):
        """
        Returns :class:`InMemoryCommit` object for this repository.
        """
        raise NotImplementedError

    # ======================== #
    # UTILITIES FOR SUBCLASSES #
    # ======================== #

    def _validate_diff_commits(self, commit1, commit2):
        """
        Validates that the given commits are related to this repository.

        Intended as a utility for sub classes to have a consistent validation
        of input parameters in methods like :meth:`get_diff`.
        """
        self._validate_commit(commit1)
        self._validate_commit(commit2)
        if (isinstance(commit1, EmptyCommit) and
                isinstance(commit2, EmptyCommit)):
            raise ValueError("Cannot compare two empty commits")

    def _validate_commit(self, commit):
        if not isinstance(commit, BaseCommit):
            raise TypeError(
                "%s is not of type BaseCommit" % repr(commit))
        if commit.repository != self and not isinstance(commit, EmptyCommit):
            raise ValueError(
                "Commit %s must be a valid commit from this repository %s, "
                "related to this repository instead %s." %
                (commit, self, commit.repository))

    def _validate_commit_id(self, commit_id):
        if not isinstance(commit_id, basestring):
            raise TypeError("commit_id must be a string value")

    def _validate_commit_idx(self, commit_idx):
        if not isinstance(commit_idx, (int, long)):
            raise TypeError("commit_idx must be a numeric value")

    def _validate_branch_name(self, branch_name):
        if branch_name and branch_name not in self.branches_all:
            msg = ("Branch %s not found in %s" % (branch_name, self))
            raise BranchDoesNotExistError(msg)

    #
    # Supporting deprecated API parts
    # TODO: johbo: consider to move this into a mixin
    #

    @property
    def EMPTY_CHANGESET(self):
        warnings.warn(
            "Use EMPTY_COMMIT or EMPTY_COMMIT_ID instead", DeprecationWarning)
        return self.EMPTY_COMMIT_ID

    @property
    def revisions(self):
        warnings.warn("Use commits attribute instead", DeprecationWarning)
        return self.commit_ids

    @revisions.setter
    def revisions(self, value):
        warnings.warn("Use commits attribute instead", DeprecationWarning)
        self.commit_ids = value

    def get_changeset(self, revision=None, pre_load=None):
        warnings.warn("Use get_commit instead", DeprecationWarning)
        commit_id = None
        commit_idx = None
        if isinstance(revision, basestring):
            commit_id = revision
        else:
            commit_idx = revision
        return self.get_commit(
            commit_id=commit_id, commit_idx=commit_idx, pre_load=pre_load)

    def get_changesets(
            self, start=None, end=None, start_date=None, end_date=None,
            branch_name=None, pre_load=None):
        warnings.warn("Use get_commits instead", DeprecationWarning)
        start_id = self._revision_to_commit(start)
        end_id = self._revision_to_commit(end)
        return self.get_commits(
            start_id=start_id, end_id=end_id, start_date=start_date,
            end_date=end_date, branch_name=branch_name, pre_load=pre_load)

    def _revision_to_commit(self, revision):
        """
        Translates a revision to a commit_id

        Helps to support the old changeset based API which allows to use
        commit ids and commit indices interchangeable.
        """
        if revision is None:
            return revision

        if isinstance(revision, basestring):
            commit_id = revision
        else:
            commit_id = self.commit_ids[revision]
        return commit_id

    @property
    def in_memory_changeset(self):
        warnings.warn("Use in_memory_commit instead", DeprecationWarning)
        return self.in_memory_commit


class BaseCommit(object):
    """
    Each backend should implement it's commit representation.

    **Attributes**

        ``repository``
            repository object within which commit exists

        ``id``
            The commit id, may be ``raw_id`` or i.e. for mercurial's tip
            just ``tip``.

        ``raw_id``
            raw commit representation (i.e. full 40 length sha for git
            backend)

        ``short_id``
            shortened (if apply) version of ``raw_id``; it would be simple
            shortcut for ``raw_id[:12]`` for git/mercurial backends or same
            as ``raw_id`` for subversion

        ``idx``
            commit index

        ``files``
            list of ``FileNode`` (``Node`` with NodeKind.FILE) objects

        ``dirs``
            list of ``DirNode`` (``Node`` with NodeKind.DIR) objects

        ``nodes``
            combined list of ``Node`` objects

        ``author``
            author of the commit, as unicode

        ``message``
            message of the commit, as unicode

        ``parents``
            list of parent commits

    """

    branch = None
    """
    Depending on the backend this should be set to the branch name of the
    commit. Backends not supporting branches on commits should leave this
    value as ``None``.
    """

    _ARCHIVE_PREFIX_TEMPLATE = b'{repo_name}-{short_id}'
    """
    This template is used to generate a default prefix for repository archives
    if no prefix has been specified.
    """

    def __str__(self):
        return '<%s at %s:%s>' % (
            self.__class__.__name__, self.idx, self.short_id)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return u'%s:%s' % (self.idx, self.short_id)

    def __eq__(self, other):
        return self.raw_id == other.raw_id

    def __json__(self):
        parents = []
        try:
            for parent in self.parents:
                parents.append({'raw_id': parent.raw_id})
        except NotImplementedError:
            # empty commit doesn't have parents implemented
            pass

        return {
            'short_id': self.short_id,
            'raw_id': self.raw_id,
            'revision': self.idx,
            'message': self.message,
            'date': self.date,
            'author': self.author,
            'parents': parents,
            'branch': self.branch
        }

    @LazyProperty
    def last(self):
        """
        ``True`` if this is last commit in repository, ``False``
        otherwise; trying to access this attribute while there is no
        commits would raise `EmptyRepositoryError`
        """
        if self.repository is None:
            raise CommitError("Cannot check if it's most recent commit")
        return self.raw_id == self.repository.commit_ids[-1]

    @LazyProperty
    def parents(self):
        """
        Returns list of parent commits.
        """
        raise NotImplementedError

    @property
    def merge(self):
        """
        Returns boolean if commit is a merge.
        """
        return len(self.parents) > 1

    @LazyProperty
    def children(self):
        """
        Returns list of child commits.
        """
        raise NotImplementedError

    @LazyProperty
    def id(self):
        """
        Returns string identifying this commit.
        """
        raise NotImplementedError

    @LazyProperty
    def raw_id(self):
        """
        Returns raw string identifying this commit.
        """
        raise NotImplementedError

    @LazyProperty
    def short_id(self):
        """
        Returns shortened version of ``raw_id`` attribute, as string,
        identifying this commit, useful for presentation to users.
        """
        raise NotImplementedError

    @LazyProperty
    def idx(self):
        """
        Returns integer identifying this commit.
        """
        raise NotImplementedError

    @LazyProperty
    def committer(self):
        """
        Returns committer for this commit
        """
        raise NotImplementedError

    @LazyProperty
    def committer_name(self):
        """
        Returns committer name for this commit
        """

        return author_name(self.committer)

    @LazyProperty
    def committer_email(self):
        """
        Returns committer email address for this commit
        """

        return author_email(self.committer)

    @LazyProperty
    def author(self):
        """
        Returns author for this commit
        """

        raise NotImplementedError

    @LazyProperty
    def author_name(self):
        """
        Returns author name for this commit
        """

        return author_name(self.author)

    @LazyProperty
    def author_email(self):
        """
        Returns author email address for this commit
        """

        return author_email(self.author)

    def get_file_mode(self, path):
        """
        Returns stat mode of the file at `path`.
        """
        raise NotImplementedError

    def is_link(self, path):
        """
        Returns ``True`` if given `path` is a symlink
        """
        raise NotImplementedError

    def get_file_content(self, path):
        """
        Returns content of the file at the given `path`.
        """
        raise NotImplementedError

    def get_file_size(self, path):
        """
        Returns size of the file at the given `path`.
        """
        raise NotImplementedError

    def get_file_commit(self, path, pre_load=None):
        """
        Returns last commit of the file at the given `path`.

        :param pre_load: Optional. List of commit attributes to load.
        """
        return self.get_file_history(path, limit=1, pre_load=pre_load)[0]

    def get_file_history(self, path, limit=None, pre_load=None):
        """
        Returns history of file as reversed list of :class:`BaseCommit`
        objects for which file at given `path` has been modified.

        :param limit: Optional. Allows to limit the size of the returned
           history. This is intended as a hint to the underlying backend, so
           that it can apply optimizations depending on the limit.
        :param pre_load: Optional. List of commit attributes to load.
        """
        raise NotImplementedError

    def get_file_annotate(self, path, pre_load=None):
        """
        Returns a generator of four element tuples with
        lineno, sha, commit lazy loader and line

        :param pre_load: Optional. List of commit attributes to load.
        """
        raise NotImplementedError

    def get_nodes(self, path):
        """
        Returns combined ``DirNode`` and ``FileNode`` objects list representing
        state of commit at the given ``path``.

        :raises ``CommitError``: if node at the given ``path`` is not
          instance of ``DirNode``
        """
        raise NotImplementedError

    def get_node(self, path):
        """
        Returns ``Node`` object from the given ``path``.

        :raises ``NodeDoesNotExistError``: if there is no node at the given
          ``path``
        """
        raise NotImplementedError

    def get_largefile_node(self, path):
        """
        Returns the path to largefile from Mercurial storage.
        """
        raise NotImplementedError

    def archive_repo(self, file_path, kind='tgz', subrepos=None,
                     prefix=None, write_metadata=False, mtime=None):
        """
        Creates an archive containing the contents of the repository.

        :param file_path: path to the file which to create the archive.
        :param kind: one of following: ``"tbz2"``, ``"tgz"``, ``"zip"``.
        :param prefix: name of root directory in archive.
            Default is repository name and commit's short_id joined with dash:
            ``"{repo_name}-{short_id}"``.
        :param write_metadata: write a metadata file into archive.
        :param mtime: custom modification time for archive creation, defaults
            to time.time() if not given.

        :raise VCSError: If prefix has a problem.
        """
        allowed_kinds = settings.ARCHIVE_SPECS.keys()
        if kind not in allowed_kinds:
            raise ImproperArchiveTypeError(
                'Archive kind (%s) not supported use one of %s' %
                (kind, allowed_kinds))

        prefix = self._validate_archive_prefix(prefix)

        mtime = mtime or time.time()

        file_info = []
        cur_rev = self.repository.get_commit(commit_id=self.raw_id)
        for _r, _d, files in cur_rev.walk('/'):
            for f in files:
                f_path = os.path.join(prefix, f.path)
                file_info.append(
                    (f_path, f.mode, f.is_link(), f.raw_bytes))

        if write_metadata:
            metadata = [
                ('repo_name', self.repository.name),
                ('rev', self.raw_id),
                ('create_time', mtime),
                ('branch', self.branch),
                ('tags', ','.join(self.tags)),
            ]
            meta = ["%s:%s" % (f_name, value) for f_name, value in metadata]
            file_info.append(('.archival.txt', 0644, False, '\n'.join(meta)))

        connection.Hg.archive_repo(file_path, mtime, file_info, kind)

    def _validate_archive_prefix(self, prefix):
        if prefix is None:
            prefix = self._ARCHIVE_PREFIX_TEMPLATE.format(
                repo_name=safe_str(self.repository.name),
                short_id=self.short_id)
        elif not isinstance(prefix, str):
            raise ValueError("prefix not a bytes object: %s" % repr(prefix))
        elif prefix.startswith('/'):
            raise VCSError("Prefix cannot start with leading slash")
        elif prefix.strip() == '':
            raise VCSError("Prefix cannot be empty")
        return prefix

    @LazyProperty
    def root(self):
        """
        Returns ``RootNode`` object for this commit.
        """
        return self.get_node('')

    def next(self, branch=None):
        """
        Returns next commit from current, if branch is gives it will return
        next commit belonging to this branch

        :param branch: show commits within the given named branch
        """
        indexes = xrange(self.idx + 1, self.repository.count())
        return self._find_next(indexes, branch)

    def prev(self, branch=None):
        """
        Returns previous commit from current, if branch is gives it will
        return previous commit belonging to this branch

        :param branch: show commit within the given named branch
        """
        indexes = xrange(self.idx - 1, -1, -1)
        return self._find_next(indexes, branch)

    def _find_next(self, indexes, branch=None):
        if branch and self.branch != branch:
            raise VCSError('Branch option used on commit not belonging '
                           'to that branch')

        for next_idx in indexes:
            commit = self.repository.get_commit(commit_idx=next_idx)
            if branch and branch != commit.branch:
                continue
            return commit
        raise CommitDoesNotExistError

    def diff(self, ignore_whitespace=True, context=3):
        """
        Returns a `Diff` object representing the change made by this commit.
        """
        parent = (
            self.parents[0] if self.parents else self.repository.EMPTY_COMMIT)
        diff = self.repository.get_diff(
            parent, self,
            ignore_whitespace=ignore_whitespace,
            context=context)
        return diff

    @LazyProperty
    def added(self):
        """
        Returns list of added ``FileNode`` objects.
        """
        raise NotImplementedError

    @LazyProperty
    def changed(self):
        """
        Returns list of modified ``FileNode`` objects.
        """
        raise NotImplementedError

    @LazyProperty
    def removed(self):
        """
        Returns list of removed ``FileNode`` objects.
        """
        raise NotImplementedError

    @LazyProperty
    def size(self):
        """
        Returns total number of bytes from contents of all filenodes.
        """
        return sum((node.size for node in self.get_filenodes_generator()))

    def walk(self, topurl=''):
        """
        Similar to os.walk method. Insted of filesystem it walks through
        commit starting at given ``topurl``.  Returns generator of tuples
        (topnode, dirnodes, filenodes).
        """
        topnode = self.get_node(topurl)
        if not topnode.is_dir():
            return
        yield (topnode, topnode.dirs, topnode.files)
        for dirnode in topnode.dirs:
            for tup in self.walk(dirnode.path):
                yield tup

    def get_filenodes_generator(self):
        """
        Returns generator that yields *all* file nodes.
        """
        for topnode, dirs, files in self.walk():
            for node in files:
                yield node

    #
    # Utilities for sub classes to support consistent behavior
    #

    def no_node_at_path(self, path):
        return NodeDoesNotExistError(
            "There is no file nor directory at the given path: "
            "'%s' at commit %s" % (path, self.short_id))

    def _fix_path(self, path):
        """
        Paths are stored without trailing slash so we need to get rid off it if
        needed.
        """
        return path.rstrip('/')

    #
    # Deprecated API based on changesets
    #

    @property
    def revision(self):
        warnings.warn("Use idx instead", DeprecationWarning)
        return self.idx

    @revision.setter
    def revision(self, value):
        warnings.warn("Use idx instead", DeprecationWarning)
        self.idx = value

    def get_file_changeset(self, path):
        warnings.warn("Use get_file_commit instead", DeprecationWarning)
        return self.get_file_commit(path)


class BaseChangesetClass(type):

    def __instancecheck__(self, instance):
        return isinstance(instance, BaseCommit)


class BaseChangeset(BaseCommit):

    __metaclass__ = BaseChangesetClass

    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "Use BaseCommit instead of BaseChangeset", DeprecationWarning)
        return super(BaseChangeset, cls).__new__(cls, *args, **kwargs)


class BaseInMemoryCommit(object):
    """
    Represents differences between repository's state (most recent head) and
    changes made *in place*.

    **Attributes**

        ``repository``
            repository object for this in-memory-commit

        ``added``
            list of ``FileNode`` objects marked as *added*

        ``changed``
            list of ``FileNode`` objects marked as *changed*

        ``removed``
            list of ``FileNode`` or ``RemovedFileNode`` objects marked to be
            *removed*

        ``parents``
            list of :class:`BaseCommit` instances representing parents of
            in-memory commit. Should always be 2-element sequence.

    """

    def __init__(self, repository):
        self.repository = repository
        self.added = []
        self.changed = []
        self.removed = []
        self.parents = []

    def add(self, *filenodes):
        """
        Marks given ``FileNode`` objects as *to be committed*.

        :raises ``NodeAlreadyExistsError``: if node with same path exists at
           latest commit
        :raises ``NodeAlreadyAddedError``: if node with same path is already
           marked as *added*
        """
        # Check if not already marked as *added* first
        for node in filenodes:
            if node.path in (n.path for n in self.added):
                raise NodeAlreadyAddedError(
                    "Such FileNode %s is already marked for addition"
                    % node.path)
        for node in filenodes:
            self.added.append(node)

    def change(self, *filenodes):
        """
        Marks given ``FileNode`` objects to be *changed* in next commit.

        :raises ``EmptyRepositoryError``: if there are no commits yet
        :raises ``NodeAlreadyExistsError``: if node with same path is already
           marked to be *changed*
        :raises ``NodeAlreadyRemovedError``: if node with same path is already
           marked to be *removed*
        :raises ``NodeDoesNotExistError``: if node doesn't exist in latest
           commit
        :raises ``NodeNotChangedError``: if node hasn't really be changed
        """
        for node in filenodes:
            if node.path in (n.path for n in self.removed):
                raise NodeAlreadyRemovedError(
                    "Node at %s is already marked as removed" % node.path)
        try:
            self.repository.get_commit()
        except EmptyRepositoryError:
            raise EmptyRepositoryError(
                "Nothing to change - try to *add* new nodes rather than "
                "changing them")
        for node in filenodes:
            if node.path in (n.path for n in self.changed):
                raise NodeAlreadyChangedError(
                    "Node at '%s' is already marked as changed" % node.path)
            self.changed.append(node)

    def remove(self, *filenodes):
        """
        Marks given ``FileNode`` (or ``RemovedFileNode``) objects to be
        *removed* in next commit.

        :raises ``NodeAlreadyRemovedError``: if node has been already marked to
           be *removed*
        :raises ``NodeAlreadyChangedError``: if node has been already marked to
           be *changed*
        """
        for node in filenodes:
            if node.path in (n.path for n in self.removed):
                raise NodeAlreadyRemovedError(
                    "Node is already marked to for removal at %s" % node.path)
            if node.path in (n.path for n in self.changed):
                raise NodeAlreadyChangedError(
                    "Node is already marked to be changed at %s" % node.path)
            # We only mark node as *removed* - real removal is done by
            # commit method
            self.removed.append(node)

    def reset(self):
        """
        Resets this instance to initial state (cleans ``added``, ``changed``
        and ``removed`` lists).
        """
        self.added = []
        self.changed = []
        self.removed = []
        self.parents = []

    def get_ipaths(self):
        """
        Returns generator of paths from nodes marked as added, changed or
        removed.
        """
        for node in itertools.chain(self.added, self.changed, self.removed):
            yield node.path

    def get_paths(self):
        """
        Returns list of paths from nodes marked as added, changed or removed.
        """
        return list(self.get_ipaths())

    def check_integrity(self, parents=None):
        """
        Checks in-memory commit's integrity. Also, sets parents if not
        already set.

        :raises CommitError: if any error occurs (i.e.
          ``NodeDoesNotExistError``).
        """
        if not self.parents:
            parents = parents or []
            if len(parents) == 0:
                try:
                    parents = [self.repository.get_commit(), None]
                except EmptyRepositoryError:
                    parents = [None, None]
            elif len(parents) == 1:
                parents += [None]
            self.parents = parents

        # Local parents, only if not None
        parents = [p for p in self.parents if p]

        # Check nodes marked as added
        for p in parents:
            for node in self.added:
                try:
                    p.get_node(node.path)
                except NodeDoesNotExistError:
                    pass
                else:
                    raise NodeAlreadyExistsError(
                        "Node `%s` already exists at %s" % (node.path, p))

        # Check nodes marked as changed
        missing = set(self.changed)
        not_changed = set(self.changed)
        if self.changed and not parents:
            raise NodeDoesNotExistError(str(self.changed[0].path))
        for p in parents:
            for node in self.changed:
                try:
                    old = p.get_node(node.path)
                    missing.remove(node)
                    # if content actually changed, remove node from not_changed
                    if old.content != node.content:
                        not_changed.remove(node)
                except NodeDoesNotExistError:
                    pass
        if self.changed and missing:
            raise NodeDoesNotExistError(
                "Node `%s` marked as modified but missing in parents: %s"
                % (node.path, parents))

        if self.changed and not_changed:
            raise NodeNotChangedError(
                "Node `%s` wasn't actually changed (parents: %s)"
                % (not_changed.pop().path, parents))

        # Check nodes marked as removed
        if self.removed and not parents:
            raise NodeDoesNotExistError(
                "Cannot remove node at %s as there "
                "were no parents specified" % self.removed[0].path)
        really_removed = set()
        for p in parents:
            for node in self.removed:
                try:
                    p.get_node(node.path)
                    really_removed.add(node)
                except CommitError:
                    pass
        not_removed = set(self.removed) - really_removed
        if not_removed:
            # TODO: johbo: This code branch does not seem to be covered
            raise NodeDoesNotExistError(
                "Cannot remove node at %s from "
                "following parents: %s" % (not_removed, parents))

    def commit(
            self, message, author, parents=None, branch=None, date=None,
            **kwargs):
        """
        Performs in-memory commit (doesn't check workdir in any way) and
        returns newly created :class:`BaseCommit`. Updates repository's
        attribute `commits`.

        .. note::

           While overriding this method each backend's should call
           ``self.check_integrity(parents)`` in the first place.

        :param message: message of the commit
        :param author: full username, i.e. "Joe Doe <joe.doe@example.com>"
        :param parents: single parent or sequence of parents from which commit
           would be derived
        :param date: ``datetime.datetime`` instance. Defaults to
           ``datetime.datetime.now()``.
        :param branch: branch name, as string. If none given, default backend's
           branch would be used.

        :raises ``CommitError``: if any error occurs while committing
        """
        raise NotImplementedError


class BaseInMemoryChangesetClass(type):

    def __instancecheck__(self, instance):
        return isinstance(instance, BaseInMemoryCommit)


class BaseInMemoryChangeset(BaseInMemoryCommit):

    __metaclass__ = BaseInMemoryChangesetClass

    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "Use BaseCommit instead of BaseInMemoryCommit", DeprecationWarning)
        return super(BaseInMemoryChangeset, cls).__new__(cls, *args, **kwargs)


class EmptyCommit(BaseCommit):
    """
    An dummy empty commit. It's possible to pass hash when creating
    an EmptyCommit
    """

    def __init__(
            self, commit_id='0' * 40, repo=None, alias=None, idx=-1,
            message='', author='', date=None):
        self._empty_commit_id = commit_id
        # TODO: johbo: Solve idx parameter, default value does not make
        # too much sense
        self.idx = idx
        self.message = message
        self.author = author
        self.date = date or datetime.datetime.fromtimestamp(0)
        self.repository = repo
        self.alias = alias

    @LazyProperty
    def raw_id(self):
        """
        Returns raw string identifying this commit, useful for web
        representation.
        """

        return self._empty_commit_id

    @LazyProperty
    def branch(self):
        if self.alias:
            from rhodecode.lib.vcs.backends import get_backend
            return get_backend(self.alias).DEFAULT_BRANCH_NAME

    @LazyProperty
    def short_id(self):
        return self.raw_id[:12]

    def get_file_commit(self, path):
        return self

    def get_file_content(self, path):
        return u''

    def get_file_size(self, path):
        return 0


class EmptyChangesetClass(type):

    def __instancecheck__(self, instance):
        return isinstance(instance, EmptyCommit)


class EmptyChangeset(EmptyCommit):

    __metaclass__ = EmptyChangesetClass

    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "Use EmptyCommit instead of EmptyChangeset", DeprecationWarning)
        return super(EmptyCommit, cls).__new__(cls, *args, **kwargs)

    def __init__(self, cs='0' * 40, repo=None, requested_revision=None,
                 alias=None, revision=-1, message='', author='', date=None):
        if requested_revision is not None:
            warnings.warn(
                "Parameter requested_revision not supported anymore",
                DeprecationWarning)
        super(EmptyChangeset, self).__init__(
            commit_id=cs, repo=repo, alias=alias, idx=revision,
            message=message, author=author, date=date)

        @property
        def revision(self):
            warnings.warn("Use idx instead", DeprecationWarning)
            return self.idx

        @revision.setter
        def revision(self, value):
            warnings.warn("Use idx instead", DeprecationWarning)
            self.idx = value


class CollectionGenerator(object):

    def __init__(self, repo, commit_ids, collection_size=None, pre_load=None):
        self.repo = repo
        self.commit_ids = commit_ids
        # TODO: (oliver) this isn't currently hooked up
        self.collection_size = None
        self.pre_load = pre_load

    def __len__(self):
        if self.collection_size is not None:
            return self.collection_size
        return self.commit_ids.__len__()

    def __iter__(self):
        for commit_id in self.commit_ids:
            # TODO: johbo: Mercurial passes in commit indices or commit ids
            yield self._commit_factory(commit_id)

    def _commit_factory(self, commit_id):
        """
        Allows backends to override the way commits are generated.
        """
        return self.repo.get_commit(commit_id=commit_id,
                                    pre_load=self.pre_load)

    def __getslice__(self, i, j):
        """
        Returns an iterator of sliced repository
        """
        commit_ids = self.commit_ids[i:j]
        return self.__class__(
            self.repo, commit_ids, pre_load=self.pre_load)

    def __repr__(self):
        return '<CollectionGenerator[len:%s]>' % (self.__len__())


class Config(object):
    """
    Represents the configuration for a repository.

    The API is inspired by :class:`ConfigParser.ConfigParser` from the
    standard library. It implements only the needed subset.
    """

    def __init__(self):
        self._values = {}

    def copy(self):
        clone = Config()
        for section, values in self._values.items():
            clone._values[section] = values.copy()
        return clone

    def __repr__(self):
        return '<Config(%s values) at %s>' % (len(self._values), hex(id(self)))

    def items(self, section):
        return self._values.get(section, {}).iteritems()

    def get(self, section, option):
        return self._values.get(section, {}).get(option)

    def set(self, section, option, value):
        section_values = self._values.setdefault(section, {})
        section_values[option] = value

    def clear_section(self, section):
        self._values[section] = {}

    def serialize(self):
        """
        Creates a list of three tuples (section, key, value) representing
        this config object.
        """
        items = []
        for section in self._values:
            for option, value in self._values[section].items():
                items.append(
                    (safe_str(section), safe_str(option), safe_str(value)))
        return items


class Diff(object):
    """
    Represents a diff result from a repository backend.

    Subclasses have to provide a backend specific value for :attr:`_header_re`.
    """

    _header_re = None

    def __init__(self, raw_diff):
        self.raw = raw_diff

    def chunks(self):
        """
        split the diff in chunks of separate --git a/file b/file chunks
        to make diffs consistent we must prepend with \n, and make sure
        we can detect last chunk as this was also has special rule
        """
        chunks = ('\n' + self.raw).split('\ndiff --git')[1:]
        total_chunks = len(chunks)
        return (DiffChunk(chunk, self, cur_chunk == total_chunks)
                for cur_chunk, chunk in enumerate(chunks, start=1))


class DiffChunk(object):

    def __init__(self, chunk, diff, last_chunk):
        self._diff = diff

        # since we split by \ndiff --git that part is lost from original diff
        # we need to re-apply it at the end, EXCEPT ! if it's last chunk
        if not last_chunk:
            chunk += '\n'

        match = self._diff._header_re.match(chunk)
        self.header = match.groupdict()
        self.diff = chunk[match.end():]
        self.raw = chunk
