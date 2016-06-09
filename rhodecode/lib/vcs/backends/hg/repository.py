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
HG repository module
"""

import logging
import binascii
import os
import re
import shutil
import urllib

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.datelib import (
    utcdate_fromtimestamp, makedate, date_astimestamp)
from rhodecode.lib.utils import safe_unicode, safe_str
from rhodecode.lib.vcs import connection
from rhodecode.lib.vcs.backends.base import (
    BaseRepository, CollectionGenerator, Config, MergeResponse,
    MergeFailureReason)
from rhodecode.lib.vcs.backends.hg.commit import MercurialCommit
from rhodecode.lib.vcs.backends.hg.diff import MercurialDiff
from rhodecode.lib.vcs.backends.hg.inmemory import MercurialInMemoryCommit
from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import (
    EmptyRepositoryError, RepositoryError, TagAlreadyExistError,
    TagDoesNotExistError, CommitDoesNotExistError)

hexlify = binascii.hexlify
nullid = "\0" * 20

log = logging.getLogger(__name__)


class MercurialRepository(BaseRepository):
    """
    Mercurial repository backend
    """
    DEFAULT_BRANCH_NAME = 'default'

    def __init__(self, repo_path, config=None, create=False, src_url=None,
                 update_after_clone=False, with_wire=None):
        """
        Raises RepositoryError if repository could not be find at the given
        ``repo_path``.

        :param repo_path: local path of the repository
        :param config: config object containing the repo configuration
        :param create=False: if set to True, would try to create repository if
           it does not exist rather than raising exception
        :param src_url=None: would try to clone repository from given location
        :param update_after_clone=False: sets update of working copy after
           making a clone
        """
        self.path = safe_str(os.path.abspath(repo_path))
        self.config = config if config else Config()
        self._remote = connection.Hg(
            self.path, self.config, with_wire=with_wire)

        self._init_repo(create, src_url, update_after_clone)

        # caches
        self._commit_ids = {}

    @LazyProperty
    def commit_ids(self):
        """
        Returns list of commit ids, in ascending order.  Being lazy
        attribute allows external tools to inject shas from cache.
        """
        commit_ids = self._get_all_commit_ids()
        self._rebuild_cache(commit_ids)
        return commit_ids

    def _rebuild_cache(self, commit_ids):
        self._commit_ids = dict((commit_id, index)
                                for index, commit_id in enumerate(commit_ids))

    @LazyProperty
    def branches(self):
        return self._get_branches()

    @LazyProperty
    def branches_closed(self):
        return self._get_branches(active=False, closed=True)

    @LazyProperty
    def branches_all(self):
        all_branches = {}
        all_branches.update(self.branches)
        all_branches.update(self.branches_closed)
        return all_branches

    def _get_branches(self, active=True, closed=False):
        """
        Gets branches for this repository
        Returns only not closed active branches by default

        :param active: return also active branches
        :param closed: return also closed branches

        """
        if self.is_empty():
            return {}

        def get_name(ctx):
            return ctx[0]

        _branches = [(safe_unicode(n), hexlify(h),) for n, h in
                     self._remote.branches(active, closed).items()]

        return OrderedDict(sorted(_branches, key=get_name, reverse=False))

    @LazyProperty
    def tags(self):
        """
        Gets tags for this repository
        """
        return self._get_tags()

    def _get_tags(self):
        if self.is_empty():
            return {}

        def get_name(ctx):
            return ctx[0]

        _tags = [(safe_unicode(n), hexlify(h),) for n, h in
                 self._remote.tags().items()]

        return OrderedDict(sorted(_tags, key=get_name, reverse=True))

    def tag(self, name, user, commit_id=None, message=None, date=None,
            **kwargs):
        """
        Creates and returns a tag for the given ``commit_id``.

        :param name: name for new tag
        :param user: full username, i.e.: "Joe Doe <joe.doe@example.com>"
        :param commit_id: commit id for which new tag would be created
        :param message: message of the tag's commit
        :param date: date of tag's commit

        :raises TagAlreadyExistError: if tag with same name already exists
        """
        if name in self.tags:
            raise TagAlreadyExistError("Tag %s already exists" % name)
        commit = self.get_commit(commit_id=commit_id)
        local = kwargs.setdefault('local', False)

        if message is None:
            message = "Added tag %s for commit %s" % (name, commit.short_id)

        date, tz = date_to_timestamp_plus_offset(date)

        self._remote.tag(
            name, commit.raw_id, message, local, user, date, tz)

        # Reinitialize tags
        self.tags = self._get_tags()
        tag_id = self.tags[name]

        return self.get_commit(commit_id=tag_id)

    def remove_tag(self, name, user, message=None, date=None):
        """
        Removes tag with the given `name`.

        :param name: name of the tag to be removed
        :param user: full username, i.e.: "Joe Doe <joe.doe@example.com>"
        :param message: message of the tag's removal commit
        :param date: date of tag's removal commit

        :raises TagDoesNotExistError: if tag with given name does not exists
        """
        if name not in self.tags:
            raise TagDoesNotExistError("Tag %s does not exist" % name)
        if message is None:
            message = "Removed tag %s" % name
        local = False

        date, tz = date_to_timestamp_plus_offset(date)

        self._remote.tag(name, nullid, message, local, user, date, tz)
        self.tags = self._get_tags()

    @LazyProperty
    def bookmarks(self):
        """
        Gets bookmarks for this repository
        """
        return self._get_bookmarks()

    def _get_bookmarks(self):
        if self.is_empty():
            return {}

        def get_name(ctx):
            return ctx[0]

        _bookmarks = [
            (safe_unicode(n), hexlify(h)) for n, h in
            self._remote.bookmarks().items()]

        return OrderedDict(sorted(_bookmarks, key=get_name))

    def _get_all_commit_ids(self):
        return self._remote.get_all_commit_ids('visible')

    def get_diff(
            self, commit1, commit2, path='', ignore_whitespace=False,
            context=3, path1=None):
        """
        Returns (git like) *diff*, as plain text. Shows changes introduced by
        `commit2` since `commit1`.

        :param commit1: Entry point from which diff is shown. Can be
          ``self.EMPTY_COMMIT`` - in this case, patch showing all
          the changes since empty state of the repository until `commit2`
        :param commit2: Until which commit changes should be shown.
        :param ignore_whitespace: If set to ``True``, would not show whitespace
          changes. Defaults to ``False``.
        :param context: How many lines before/after changed lines should be
          shown. Defaults to ``3``.
        """
        self._validate_diff_commits(commit1, commit2)
        if path1 is not None and path1 != path:
            raise ValueError("Diff of two different paths not supported.")

        if path:
            file_filter = [self.path, path]
        else:
            file_filter = None

        diff = self._remote.diff(
            commit1.raw_id, commit2.raw_id, file_filter=file_filter,
            opt_git=True, opt_ignorews=ignore_whitespace,
            context=context)
        return MercurialDiff(diff)

    def strip(self, commit_id, branch=None):
        self._remote.strip(commit_id, update=False, backup="none")

        self.commit_ids = self._get_all_commit_ids()
        self._rebuild_cache(self.commit_ids)

    def get_common_ancestor(self, commit_id1, commit_id2, repo2):
        if commit_id1 == commit_id2:
            return commit_id1

        ancestors = self._remote.revs_from_revspec(
            "ancestor(id(%s), id(%s))", commit_id1, commit_id2,
            other_path=repo2.path)
        return repo2[ancestors[0]].raw_id if ancestors else None

    def compare(self, commit_id1, commit_id2, repo2, merge, pre_load=None):
        if commit_id1 == commit_id2:
            commits = []
        else:
            if merge:
                indexes = self._remote.revs_from_revspec(
                    "ancestors(id(%s)) - ancestors(id(%s)) - id(%s)",
                    commit_id2, commit_id1, commit_id1, other_path=repo2.path)
            else:
                indexes = self._remote.revs_from_revspec(
                    "id(%s)..id(%s) - id(%s)", commit_id1, commit_id2,
                    commit_id1, other_path=repo2.path)

            commits = [repo2.get_commit(commit_idx=idx, pre_load=pre_load)
                       for idx in indexes]

        return commits

    @staticmethod
    def check_url(url, config):
        """
        Function will check given url and try to verify if it's a valid
        link. Sometimes it may happened that mercurial will issue basic
        auth request that can cause whole API to hang when used from python
        or other external calls.

        On failures it'll raise urllib2.HTTPError, exception is also thrown
        when the return code is non 200
        """
        # check first if it's not an local url
        if os.path.isdir(url) or url.startswith('file:'):
            return True

        # Request the _remote to verify the url
        return connection.Hg.check_url(url, config.serialize())

    @staticmethod
    def is_valid_repository(path):
        return os.path.isdir(os.path.join(path, '.hg'))

    def _init_repo(self, create, src_url=None, update_after_clone=False):
        """
        Function will check for mercurial repository in given path. If there
        is no repository in that path it will raise an exception unless
        `create` parameter is set to True - in that case repository would
        be created.

        If `src_url` is given, would try to clone repository from the
        location at given clone_point. Additionally it'll make update to
        working copy accordingly to `update_after_clone` flag.
        """
        if create and os.path.exists(self.path):
            raise RepositoryError(
                "Cannot create repository at %s, location already exist"
                % self.path)

        if src_url:
            url = str(self._get_url(src_url))
            MercurialRepository.check_url(url, self.config)

            self._remote.clone(url, self.path, update_after_clone)

            # Don't try to create if we've already cloned repo
            create = False

        if create:
            os.makedirs(self.path, mode=0755)

        self._remote.localrepository(create)

    @LazyProperty
    def in_memory_commit(self):
        return MercurialInMemoryCommit(self)

    @LazyProperty
    def description(self):
        description = self._remote.get_config_value(
            'web', 'description', untrusted=True)
        return safe_unicode(description or self.DEFAULT_DESCRIPTION)

    @LazyProperty
    def contact(self):
        contact = (
            self._remote.get_config_value("web", "contact") or
            self._remote.get_config_value("ui", "username"))
        return safe_unicode(contact or self.DEFAULT_CONTACT)

    @LazyProperty
    def last_change(self):
        """
        Returns last change made on this repository as
        `datetime.datetime` object
        """
        return utcdate_fromtimestamp(self._get_mtime(), makedate()[1])

    def _get_mtime(self):
        try:
            return date_astimestamp(self.get_commit().date)
        except RepositoryError:
            # fallback to filesystem
            cl_path = os.path.join(self.path, '.hg', "00changelog.i")
            st_path = os.path.join(self.path, '.hg', "store")
            if os.path.exists(cl_path):
                return os.stat(cl_path).st_mtime
            else:
                return os.stat(st_path).st_mtime

    def _sanitize_commit_idx(self, idx):
        # Note: Mercurial has ``int(-1)`` reserved as not existing id_or_idx
        # number. A `long` is treated in the correct way though. So we convert
        # `int` to `long` here to make sure it is handled correctly.
        if isinstance(idx, int):
            return long(idx)
        return idx

    def _get_url(self, url):
        """
        Returns normalized url. If schema is not given, would fall
        to filesystem
        (``file:///``) schema.
        """
        url = url.encode('utf8')
        if url != 'default' and '://' not in url:
            url = "file:" + urllib.pathname2url(url)
        return url

    def get_hook_location(self):
        """
        returns absolute path to location where hooks are stored
        """
        return os.path.join(self.path, '.hg', '.hgrc')

    def get_commit(self, commit_id=None, commit_idx=None, pre_load=None):
        """
        Returns ``MercurialCommit`` object representing repository's
        commit at the given `commit_id` or `commit_idx`.
        """
        if self.is_empty():
            raise EmptyRepositoryError("There are no commits yet")

        if commit_id is not None:
            self._validate_commit_id(commit_id)
            try:
                idx = self._commit_ids[commit_id]
                return MercurialCommit(self, commit_id, idx, pre_load=pre_load)
            except KeyError:
                pass
        elif commit_idx is not None:
            self._validate_commit_idx(commit_idx)
            commit_idx = self._sanitize_commit_idx(commit_idx)
            try:
                id_ = self.commit_ids[commit_idx]
                if commit_idx < 0:
                    commit_idx += len(self.commit_ids)
                return MercurialCommit(
                    self, id_, commit_idx, pre_load=pre_load)
            except IndexError:
                commit_id = commit_idx
        else:
            commit_id = "tip"

        # TODO Paris: Ugly hack to "serialize" long for msgpack
        if isinstance(commit_id, long):
            commit_id = float(commit_id)

        if isinstance(commit_id, unicode):
            commit_id = safe_str(commit_id)

        raw_id, idx = self._remote.lookup(commit_id, both=True)

        return MercurialCommit(self, raw_id, idx, pre_load=pre_load)

    def get_commits(
            self, start_id=None, end_id=None, start_date=None, end_date=None,
            branch_name=None, pre_load=None):
        """
        Returns generator of ``MercurialCommit`` objects from start to end
        (both are inclusive)

        :param start_id: None, str(commit_id)
        :param end_id: None, str(commit_id)
        :param start_date: if specified, commits with commit date less than
          ``start_date`` would be filtered out from returned set
        :param end_date: if specified, commits with commit date greater than
          ``end_date`` would be filtered out from returned set
        :param branch_name: if specified, commits not reachable from given
          branch would be filtered out from returned set

        :raise BranchDoesNotExistError: If given ``branch_name`` does not
            exist.
        :raise CommitDoesNotExistError: If commit for given ``start`` or
          ``end`` could not be found.
        """
        # actually we should check now if it's not an empty repo
        branch_ancestors = False
        if self.is_empty():
            raise EmptyRepositoryError("There are no commits yet")
        self._validate_branch_name(branch_name)

        if start_id is not None:
            self._validate_commit_id(start_id)
            c_start = self.get_commit(commit_id=start_id)
            start_pos = self._commit_ids[c_start.raw_id]
        else:
            start_pos = None

        if end_id is not None:
            self._validate_commit_id(end_id)
            c_end = self.get_commit(commit_id=end_id)
            end_pos = max(0, self._commit_ids[c_end.raw_id])
        else:
            end_pos = None

        if None not in [start_id, end_id] and start_pos > end_pos:
            raise RepositoryError(
                "Start commit '%s' cannot be after end commit '%s'" %
                (start_id, end_id))

        if end_pos is not None:
            end_pos += 1

        commit_filter = []
        if branch_name and not branch_ancestors:
            commit_filter.append('branch("%s")' % branch_name)
        elif branch_name and branch_ancestors:
            commit_filter.append('ancestors(branch("%s"))' % branch_name)
        if start_date and not end_date:
            commit_filter.append('date(">%s")' % start_date)
        if end_date and not start_date:
            commit_filter.append('date("<%s")' % end_date)
        if start_date and end_date:
            commit_filter.append(
                'date(">%s") and date("<%s")' % (start_date, end_date))

        # TODO: johbo: Figure out a simpler way for this solution
        collection_generator = CollectionGenerator
        if commit_filter:
            commit_filter = map(safe_str, commit_filter)
            revisions = self._remote.rev_range(commit_filter)
            collection_generator = MercurialIndexBasedCollectionGenerator
        else:
            revisions = self.commit_ids

        if start_pos or end_pos:
            revisions = revisions[start_pos:end_pos]

        return collection_generator(self, revisions, pre_load=pre_load)

    def pull(self, url, commit_ids=None):
        """
        Tries to pull changes from external location.

        :param commit_ids: Optional. Can be set to a list of commit ids
           which shall be pulled from the other repository.
        """
        url = self._get_url(url)
        self._remote.pull(url, commit_ids=commit_ids)

    def _local_clone(self, clone_path):
        """
        Create a local clone of the current repo.
        """
        self._remote.clone(self.path, clone_path, update_after_clone=True,
                           hooks=False)

    def _update(self, revision, clean=False):
        """
        Update the working copty to the specified revision.
        """
        self._remote.update(revision, clean=clean)

    def _identify(self):
        """
        Return the current state of the working directory.
        """
        return self._remote.identify().strip().rstrip('+')

    def _heads(self, branch=None):
        """
        Return the commit ids of the repository heads.
        """
        return self._remote.heads(branch=branch).strip().split(' ')

    def _ancestor(self, revision1, revision2):
        """
        Return the common ancestor of the two revisions.
        """
        return self._remote.ancestor(
            revision1, revision2).strip().split(':')[-1]

    def _local_push(
            self, revision, repository_path, push_branches=False,
            enable_hooks=False):
        """
        Push the given revision to the specified repository.

        :param push_branches: allow to create branches in the target repo.
        """
        self._remote.push(
            [revision], repository_path, hooks=enable_hooks,
            push_branches=push_branches)

    def _local_merge(self, target_ref, merge_message, user_name, user_email,
                     source_ref):
        """
        Merge the given source_revision into the checked out revision.

        Returns the commit id of the merge and a boolean indicating if the
        commit needs to be pushed.
        """
        self._update(target_ref.commit_id)

        ancestor = self._ancestor(target_ref.commit_id, source_ref.commit_id)
        is_the_same_branch = self._is_the_same_branch(target_ref, source_ref)

        if ancestor == source_ref.commit_id:
            # Nothing to do, the changes were already integrated
            return target_ref.commit_id, False

        elif ancestor == target_ref.commit_id and is_the_same_branch:
            # In this case we should force a commit message
            return source_ref.commit_id, True

        if settings.HG_USE_REBASE_FOR_MERGING:
            try:
                bookmark_name = 'rcbook%s%s' % (source_ref.commit_id,
                                                target_ref.commit_id)
                self.bookmark(bookmark_name, revision=source_ref.commit_id)
                self._remote.rebase(
                    source=source_ref.commit_id, dest=target_ref.commit_id)
                self._update(bookmark_name)
                return self._identify(), True
            except RepositoryError:
                # Cleanup any rebase leftovers
                self._remote.rebase(abort=True)
                self._remote.update(clean=True)
                raise
        else:
            try:
                self._remote.merge(source_ref.commit_id)
                self._remote.commit(
                    message=safe_str(merge_message),
                    username=safe_str('%s <%s>' % (user_name, user_email)))
                return self._identify(), True
            except RepositoryError:
                # Cleanup any merge leftovers
                self._remote.update(clean=True)
                raise

    def _is_the_same_branch(self, target_ref, source_ref):
        return (
            self._get_branch_name(target_ref) ==
            self._get_branch_name(source_ref))

    def _get_branch_name(self, ref):
        if ref.type == 'branch':
            return ref.name
        return self._remote.ctx_branch(ref.commit_id)

    def _get_shadow_repository_path(self, workspace_id):
        # The name of the shadow repository must start with '.', so it is
        # skipped by 'rhodecode.lib.utils.get_filesystem_repos'.
        return os.path.join(
            os.path.dirname(self.path),
            '.__shadow_%s_%s' % (os.path.basename(self.path), workspace_id))

    def _maybe_prepare_merge_workspace(self, workspace_id, unused_target_ref):
        shadow_repository_path = self._get_shadow_repository_path(workspace_id)
        if not os.path.exists(shadow_repository_path):
            self._local_clone(shadow_repository_path)
            log.debug(
                'Prepared shadow repository in %s', shadow_repository_path)

        return shadow_repository_path

    def cleanup_merge_workspace(self, workspace_id):
        shadow_repository_path = self._get_shadow_repository_path(workspace_id)
        shutil.rmtree(shadow_repository_path, ignore_errors=True)

    def _merge_repo(self, shadow_repository_path, target_ref,
                    source_repo, source_ref, merge_message,
                    merger_name, merger_email, dry_run=False):
        if target_ref.commit_id not in self._heads():
            return MergeResponse(
                False, False, None, MergeFailureReason.TARGET_IS_NOT_HEAD)

        if (target_ref.type == 'branch' and
                len(self._heads(target_ref.name)) != 1):
            return MergeResponse(
                False, False, None,
                MergeFailureReason.HG_TARGET_HAS_MULTIPLE_HEADS)

        shadow_repo = self._get_shadow_instance(shadow_repository_path)

        log.debug('Pulling in target reference %s', target_ref)
        self._validate_pull_reference(target_ref)
        shadow_repo._local_pull(self.path, target_ref)
        try:
            log.debug('Pulling in source reference %s', source_ref)
            source_repo._validate_pull_reference(source_ref)
            shadow_repo._local_pull(source_repo.path, source_ref)
        except CommitDoesNotExistError as e:
            log.exception('Failure when doing local pull on hg shadow repo')
            return MergeResponse(
                False, False, None, MergeFailureReason.MISSING_COMMIT)

        merge_commit_id = None
        merge_failure_reason = MergeFailureReason.NONE

        try:
            merge_commit_id, needs_push = shadow_repo._local_merge(
                target_ref, merge_message, merger_name, merger_email,
                source_ref)
            merge_possible = True
        except RepositoryError as e:
            log.exception('Failure when doing local merge on hg shadow repo')
            merge_possible = False
            merge_failure_reason = MergeFailureReason.MERGE_FAILED

        if merge_possible and not dry_run:
            if needs_push:
                # In case the target is a bookmark, update it, so after pushing
                # the bookmarks is also updated in the target.
                if target_ref.type == 'book':
                    shadow_repo.bookmark(
                        target_ref.name, revision=merge_commit_id)

                try:
                    shadow_repo_with_hooks = self._get_shadow_instance(
                        shadow_repository_path,
                        enable_hooks=True)
                    # Note: the push_branches option will push any new branch
                    # defined in the source repository to the target. This may
                    # be dangerous as branches are permanent in Mercurial.
                    # This feature was requested in issue #441.
                    shadow_repo_with_hooks._local_push(
                        merge_commit_id, self.path, push_branches=True,
                        enable_hooks=True)
                    merge_succeeded = True
                except RepositoryError:
                    log.exception(
                        'Failure when doing local from the shadow repository '
                        'to the target repository.')
                    merge_succeeded = False
                    merge_failure_reason = MergeFailureReason.PUSH_FAILED
            else:
                merge_succeeded = True
        else:
            merge_succeeded = False

        if dry_run:
            merge_commit_id = None

        return MergeResponse(
            merge_possible, merge_succeeded, merge_commit_id,
            merge_failure_reason)

    def _get_shadow_instance(
            self, shadow_repository_path, enable_hooks=False):
        config = self.config.copy()
        if not enable_hooks:
            config.clear_section('hooks')
        return MercurialRepository(shadow_repository_path, config)

    def _validate_pull_reference(self, reference):
        if not (reference.name in self.bookmarks or
                reference.name in self.branches or
                self.get_commit(reference.commit_id)):
            raise CommitDoesNotExistError(
                'Unknown branch, bookmark or commit id')

    def _local_pull(self, repository_path, reference):
        """
        Fetch a branch, bookmark or commit from a local repository.
        """
        repository_path = os.path.abspath(repository_path)
        if repository_path == self.path:
            raise ValueError('Cannot pull from the same repository')

        reference_type_to_option_name = {
            'book': 'bookmark',
            'branch': 'branch',
        }
        option_name = reference_type_to_option_name.get(
            reference.type, 'revision')

        if option_name == 'revision':
            ref = reference.commit_id
        else:
            ref = reference.name

        options = {option_name: [ref]}
        self._remote.pull_cmd(repository_path, hooks=False, **options)

    def bookmark(self, bookmark, revision=None):
        if isinstance(bookmark, unicode):
            bookmark = safe_str(bookmark)
        self._remote.bookmark(bookmark, revision=revision)


class MercurialIndexBasedCollectionGenerator(CollectionGenerator):

    def _commit_factory(self, commit_id):
        return self.repo.get_commit(
            commit_idx=commit_id, pre_load=self.pre_load)
