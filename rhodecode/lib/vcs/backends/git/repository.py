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
GIT repository module
"""

import logging
import os
import re
import shutil
import time

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.datelib import makedate, date_fromtimestamp
from rhodecode.lib.utils import safe_unicode, safe_str
from rhodecode.lib.vcs import connection, path as vcspath
from rhodecode.lib.vcs.backends.base import (
    BaseRepository, CollectionGenerator, Config, MergeResponse,
    MergeFailureReason)
from rhodecode.lib.vcs.backends.git.commit import GitCommit
from rhodecode.lib.vcs.backends.git.diff import GitDiff
from rhodecode.lib.vcs.backends.git.inmemory import GitInMemoryCommit
from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import (
    CommitDoesNotExistError, EmptyRepositoryError,
    RepositoryError, TagAlreadyExistError, TagDoesNotExistError, VCSError)


SHA_PATTERN = re.compile(r'^[[0-9a-fA-F]{12}|[0-9a-fA-F]{40}]$')

log = logging.getLogger(__name__)


class GitRepository(BaseRepository):
    """
    Git repository backend.
    """
    DEFAULT_BRANCH_NAME = 'master'

    contact = BaseRepository.DEFAULT_CONTACT

    def __init__(self, repo_path, config=None, create=False, src_url=None,
                 update_after_clone=False, with_wire=None, bare=False):

        self.path = safe_str(os.path.abspath(repo_path))
        self.config = config if config else Config()
        self._remote = connection.Git(
            self.path, self.config, with_wire=with_wire)

        self._init_repo(create, src_url, update_after_clone, bare)

        # caches
        self._commit_ids = {}

        self.bookmarks = {}

    @LazyProperty
    def bare(self):
        return self._remote.bare()

    @LazyProperty
    def head(self):
        return self._remote.head()

    @LazyProperty
    def commit_ids(self):
        """
        Returns list of commit ids, in ascending order.  Being lazy
        attribute allows external tools to inject commit ids from cache.
        """
        commit_ids = self._get_all_commit_ids()
        self._rebuild_cache(commit_ids)
        return commit_ids

    def _rebuild_cache(self, commit_ids):
        self._commit_ids = dict((commit_id, index)
                                for index, commit_id in enumerate(commit_ids))

    def run_git_command(self, cmd, **opts):
        """
        Runs given ``cmd`` as git command and returns tuple
        (stdout, stderr).

        :param cmd: git command to be executed
        :param opts: env options to pass into Subprocess command
        """
        if not isinstance(cmd, list):
            raise ValueError('cmd must be a list, got %s instead' % type(cmd))

        out, err = self._remote.run_git_command(cmd, **opts)
        log.debug('Stderr output of git command "%s":\n%s', cmd, err)
        return out, err

    @staticmethod
    def check_url(url, config):
        """
        Function will check given url and try to verify if it's a valid
        link. Sometimes it may happened that git will issue basic
        auth request that can cause whole API to hang when used from python
        or other external calls.

        On failures it'll raise urllib2.HTTPError, exception is also thrown
        when the return code is non 200
        """
        # check first if it's not an url
        if os.path.isdir(url) or url.startswith('file:'):
            return True

        if '+' in url.split('://', 1)[0]:
            url = url.split('+', 1)[1]

        # Request the _remote to verify the url
        return connection.Git.check_url(url, config.serialize())

    @staticmethod
    def is_valid_repository(path):
        if os.path.isdir(os.path.join(path, '.git')):
            return True
        # check case of bare repository
        try:
            GitRepository(path)
            return True
        except VCSError:
            pass
        return False

    def _init_repo(self, create, src_url=None, update_after_clone=False,
                   bare=False):
        if create and os.path.exists(self.path):
            raise RepositoryError(
                "Cannot create repository at %s, location already exist"
                % self.path)

        try:
            if create and src_url:
                GitRepository.check_url(src_url, self.config)
                self.clone(src_url, update_after_clone, bare)
            elif create:
                os.makedirs(self.path, mode=0755)

                if bare:
                    self._remote.init_bare()
                else:
                    self._remote.init()
            else:
                self._remote.assert_correct_path()
        # TODO: johbo: check if we have to translate the OSError here
        except OSError as err:
            raise RepositoryError(err)

    def _get_all_commit_ids(self, filters=None):
        # we must check if this repo is not empty, since later command
        # fails if it is. And it's cheaper to ask than throw the subprocess
        # errors
        try:
            self._remote.head()
        except KeyError:
            return []

        rev_filter = ['--branches', '--tags']
        extra_filter = []

        if filters:
            if filters.get('since'):
                extra_filter.append('--since=%s' % (filters['since']))
            if filters.get('until'):
                extra_filter.append('--until=%s' % (filters['until']))
            if filters.get('branch_name'):
                rev_filter = ['--tags']
                extra_filter.append(filters['branch_name'])
        rev_filter.extend(extra_filter)

            # if filters.get('start') or filters.get('end'):
            #     # skip is offset, max-count is limit
            #     if filters.get('start'):
            #         extra_filter += ' --skip=%s' % filters['start']
            #     if filters.get('end'):
            #         extra_filter += ' --max-count=%s' % (filters['end'] - (filters['start'] or 0))

        cmd = ['rev-list', '--reverse', '--date-order'] + rev_filter
        try:
            output, __ = self.run_git_command(cmd)
        except RepositoryError:
            # Can be raised for empty repositories
            return []
        return output.splitlines()

    def _get_all_commit_ids2(self):
        # alternate implementation
        includes = [x[1][0] for x in self._parsed_refs.iteritems()
                    if x[1][1] != 'T']
        return [c.commit.id for c in self._remote.get_walker(include=includes)]

    def _get_commit_id(self, commit_id_or_idx):
        def is_null(value):
            return len(value) == commit_id_or_idx.count('0')

        if self.is_empty():
            raise EmptyRepositoryError("There are no commits yet")

        if commit_id_or_idx in (None, '', 'tip', 'HEAD', 'head', -1):
            return self.commit_ids[-1]

        is_bstr = isinstance(commit_id_or_idx, (str, unicode))
        if ((is_bstr and commit_id_or_idx.isdigit() and len(commit_id_or_idx) < 12)
            or isinstance(commit_id_or_idx, int) or is_null(commit_id_or_idx)):
            try:
                commit_id_or_idx = self.commit_ids[int(commit_id_or_idx)]
            except Exception:
                msg = "Commit %s does not exist for %s" % (
                    commit_id_or_idx, self)
                raise CommitDoesNotExistError(msg)

        elif is_bstr:
            # get by branch/tag name
            ref_id = self._parsed_refs.get(commit_id_or_idx)
            if ref_id:  # and ref_id[1] in ['H', 'RH', 'T']:
                return ref_id[0]

            tag_ids = self.tags.values()
            # maybe it's a tag ? we don't have them in self.commit_ids
            if commit_id_or_idx in tag_ids:
                return commit_id_or_idx

            elif (not SHA_PATTERN.match(commit_id_or_idx) or
                    commit_id_or_idx not in self.commit_ids):
                msg = "Commit %s does not exist for %s" % (
                    commit_id_or_idx, self)
                raise CommitDoesNotExistError(msg)

        # Ensure we return full id
        if not SHA_PATTERN.match(str(commit_id_or_idx)):
            raise CommitDoesNotExistError(
                "Given commit id %s not recognized" % commit_id_or_idx)
        return commit_id_or_idx

    def get_hook_location(self):
        """
        returns absolute path to location where hooks are stored
        """
        loc = os.path.join(self.path, 'hooks')
        if not self.bare:
            loc = os.path.join(self.path, '.git', 'hooks')
        return loc

    @LazyProperty
    def last_change(self):
        """
        Returns last change made on this repository as
        `datetime.datetime` object.
        """
        return date_fromtimestamp(self._get_mtime(), makedate()[1])

    def _get_mtime(self):
        try:
            return time.mktime(self.get_commit().date.timetuple())
        except RepositoryError:
            idx_loc = '' if self.bare else '.git'
            # fallback to filesystem
            in_path = os.path.join(self.path, idx_loc, "index")
            he_path = os.path.join(self.path, idx_loc, "HEAD")
            if os.path.exists(in_path):
                return os.stat(in_path).st_mtime
            else:
                return os.stat(he_path).st_mtime

    @LazyProperty
    def description(self):
        description = self._remote.get_description()
        return safe_unicode(description or self.DEFAULT_DESCRIPTION)

    def _get_refs_entry(self, value, reverse):
        if self.is_empty():
            return {}

        def get_name(ctx):
            return ctx[0]

        _branches = [
            (safe_unicode(x[0]), x[1][0])
            for x in self._parsed_refs.iteritems() if x[1][1] == value]
        return OrderedDict(sorted(_branches, key=get_name, reverse=reverse))

    def _get_branches(self):
        return self._get_refs_entry('H', False)

    @LazyProperty
    def branches(self):
        return self._get_branches()

    @LazyProperty
    def branches_closed(self):
        return {}

    @LazyProperty
    def branches_all(self):
        all_branches = {}
        all_branches.update(self.branches)
        all_branches.update(self.branches_closed)
        return all_branches

    @LazyProperty
    def tags(self):
        return self._get_tags()

    def _get_tags(self):
        return self._get_refs_entry('T', True)

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
        message = message or "Added tag %s for commit %s" % (
            name, commit.raw_id)
        self._remote.set_refs('refs/tags/%s' % name, commit._commit['id'])

        self._parsed_refs = self._get_parsed_refs()
        self.tags = self._get_tags()
        return commit

    def remove_tag(self, name, user, message=None, date=None):
        """
        Removes tag with the given ``name``.

        :param name: name of the tag to be removed
        :param user: full username, i.e.: "Joe Doe <joe.doe@example.com>"
        :param message: message of the tag's removal commit
        :param date: date of tag's removal commit

        :raises TagDoesNotExistError: if tag with given name does not exists
        """
        if name not in self.tags:
            raise TagDoesNotExistError("Tag %s does not exist" % name)
        tagpath = vcspath.join(
            self._remote.get_refs_path(), 'refs', 'tags', name)
        try:
            os.remove(tagpath)
            self._parsed_refs = self._get_parsed_refs()
            self.tags = self._get_tags()
        except OSError as e:
            raise RepositoryError(e.strerror)

    @LazyProperty
    def _parsed_refs(self):
        return self._get_parsed_refs()

    def _get_parsed_refs(self):
        # TODO: (oliver) who needs RH; branches?
        # Remote Heads were commented out, as they may overwrite local branches
        # See the TODO note in rhodecode.lib.vcs.remote.git:get_refs for more
        # details.
        keys = [('refs/heads/', 'H'),
                #('refs/remotes/origin/', 'RH'),
                ('refs/tags/', 'T')]
        return self._remote.get_refs(keys=keys)

    def get_commit(self, commit_id=None, commit_idx=None, pre_load=None):
        """
        Returns `GitCommit` object representing commit from git repository
        at the given `commit_id` or head (most recent commit) if None given.
        """
        if commit_id is not None:
            self._validate_commit_id(commit_id)
        elif commit_idx is not None:
            self._validate_commit_idx(commit_idx)
            commit_id = commit_idx
        commit_id = self._get_commit_id(commit_id)
        try:
            # Need to call remote to translate id for tagging scenario
            commit_id = self._remote.get_object(commit_id)["commit_id"]
            idx = self._commit_ids[commit_id]
        except KeyError:
            raise RepositoryError("Cannot get object with id %s" % commit_id)

        return GitCommit(self, commit_id, idx, pre_load=pre_load)

    def get_commits(
            self, start_id=None, end_id=None, start_date=None, end_date=None,
            branch_name=None, pre_load=None):
        """
        Returns generator of `GitCommit` objects from start to end (both
        are inclusive), in ascending date order.

        :param start_id: None, str(commit_id)
        :param end_id: None, str(commit_id)
        :param start_date: if specified, commits with commit date less than
          ``start_date`` would be filtered out from returned set
        :param end_date: if specified, commits with commit date greater than
          ``end_date`` would be filtered out from returned set
        :param branch_name: if specified, commits not reachable from given
          branch would be filtered out from returned set

        :raise BranchDoesNotExistError: If given `branch_name` does not
            exist.
        :raise CommitDoesNotExistError: If commits for given `start` or
          `end` could not be found.

        """
        if self.is_empty():
            raise EmptyRepositoryError("There are no commits yet")
        self._validate_branch_name(branch_name)

        if start_id is not None:
            self._validate_commit_id(start_id)
        if end_id is not None:
            self._validate_commit_id(end_id)

        start_raw_id = self._get_commit_id(start_id)
        start_pos = self._commit_ids[start_raw_id] if start_id else None
        end_raw_id = self._get_commit_id(end_id)
        end_pos = max(0, self._commit_ids[end_raw_id]) if end_id else None

        if None not in [start_id, end_id] and start_pos > end_pos:
            raise RepositoryError(
                "Start commit '%s' cannot be after end commit '%s'" %
                (start_id, end_id))

        if end_pos is not None:
            end_pos += 1

        filter_ = []
        if branch_name:
            filter_.append({'branch_name': branch_name})
        if start_date and not end_date:
            filter_.append({'since': start_date})
        if end_date and not start_date:
            filter_.append({'until': end_date})
        if start_date and end_date:
            filter_.append({'since': start_date})
            filter_.append({'until': end_date})

        # if start_pos or end_pos:
        #     filter_.append({'start': start_pos})
        #     filter_.append({'end': end_pos})

        if filter_:
            revfilters = {
                'branch_name': branch_name,
                'since': start_date.strftime('%m/%d/%y %H:%M:%S') if start_date else None,
                'until': end_date.strftime('%m/%d/%y %H:%M:%S') if end_date else None,
                'start': start_pos,
                'end': end_pos,
            }
            commit_ids = self._get_all_commit_ids(filters=revfilters)

            # pure python stuff, it's slow due to walker walking whole repo
            # def get_revs(walker):
            #     for walker_entry in walker:
            #         yield walker_entry.commit.id
            # revfilters = {}
            # commit_ids = list(reversed(list(get_revs(self._repo.get_walker(**revfilters)))))
        else:
            commit_ids = self.commit_ids

        if start_pos or end_pos:
            commit_ids = commit_ids[start_pos: end_pos]

        return CollectionGenerator(self, commit_ids, pre_load=pre_load)

    def get_diff(
            self, commit1, commit2, path='', ignore_whitespace=False,
            context=3, path1=None):
        """
        Returns (git like) *diff*, as plain text. Shows changes introduced by
        ``commit2`` since ``commit1``.

        :param commit1: Entry point from which diff is shown. Can be
          ``self.EMPTY_COMMIT`` - in this case, patch showing all
          the changes since empty state of the repository until ``commit2``
        :param commit2: Until which commits changes should be shown.
        :param ignore_whitespace: If set to ``True``, would not show whitespace
          changes. Defaults to ``False``.
        :param context: How many lines before/after changed lines should be
          shown. Defaults to ``3``.
        """
        self._validate_diff_commits(commit1, commit2)
        if path1 is not None and path1 != path:
            raise ValueError("Diff of two different paths not supported.")

        flags = [
            '-U%s' % context, '--full-index', '--binary', '-p',
            '-M', '--abbrev=40']
        if ignore_whitespace:
            flags.append('-w')

        if commit1 == self.EMPTY_COMMIT:
            cmd = ['show'] + flags + [commit2.raw_id]
        else:
            cmd = ['diff'] + flags + [commit1.raw_id, commit2.raw_id]

        if path:
            cmd.extend(['--', path])

        stdout, __ = self.run_git_command(cmd)
        # If we used 'show' command, strip first few lines (until actual diff
        # starts)
        if commit1 == self.EMPTY_COMMIT:
            lines = stdout.splitlines()
            x = 0
            for line in lines:
                if line.startswith('diff'):
                    break
                x += 1
            # Append new line just like 'diff' command do
            stdout = '\n'.join(lines[x:]) + '\n'
        return GitDiff(stdout)

    def strip(self, commit_id, branch_name):
        commit = self.get_commit(commit_id=commit_id)
        if commit.merge:
            raise Exception('Cannot reset to merge commit')

        # parent is going to be the new head now
        commit = commit.parents[0]
        self._remote.set_refs('refs/heads/%s' % branch_name, commit.raw_id)

        self.commit_ids = self._get_all_commit_ids()
        self._rebuild_cache(self.commit_ids)

    def get_common_ancestor(self, commit_id1, commit_id2, repo2):
        if commit_id1 == commit_id2:
            return commit_id1

        if self != repo2:
            commits = self._remote.get_missing_revs(
                commit_id1, commit_id2, repo2.path)
            if commits:
                commit = repo2.get_commit(commits[-1])
                if commit.parents:
                    ancestor_id = commit.parents[0].raw_id
                else:
                    ancestor_id = None
            else:
                # no commits from other repo, ancestor_id is the commit_id2
                ancestor_id = commit_id2
        else:
            output, __ = self.run_git_command(
                ['merge-base', commit_id1, commit_id2])
            ancestor_id = re.findall(r'[0-9a-fA-F]{40}', output)[0]

        return ancestor_id

    def compare(self, commit_id1, commit_id2, repo2, merge, pre_load=None):
        repo1 = self
        ancestor_id = None

        if commit_id1 == commit_id2:
            commits = []
        elif repo1 != repo2:
            missing_ids = self._remote.get_missing_revs(commit_id1, commit_id2,
                                                        repo2.path)
            commits = [
                repo2.get_commit(commit_id=commit_id, pre_load=pre_load)
                for commit_id in reversed(missing_ids)]
        else:
            output, __ = repo1.run_git_command(
                ['log', '--reverse', '--pretty=format: %H', '-s',
                 '%s..%s' % (commit_id1, commit_id2)])
            commits = [
                repo1.get_commit(commit_id=commit_id, pre_load=pre_load)
                for commit_id in re.findall(r'[0-9a-fA-F]{40}', output)]

        return commits

    @LazyProperty
    def in_memory_commit(self):
        """
        Returns ``GitInMemoryCommit`` object for this repository.
        """
        return GitInMemoryCommit(self)

    def clone(self, url, update_after_clone=True, bare=False):
        """
        Tries to clone commits from external location.

        :param update_after_clone: If set to ``False``, git won't checkout
          working directory
        :param bare: If set to ``True``, repository would be cloned into
          *bare* git repository (no working directory at all).
        """
        # init_bare and init expect empty dir created to proceed
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        if bare:
            self._remote.init_bare()
        else:
            self._remote.init()

        deferred = '^{}'
        valid_refs = ('refs/heads', 'refs/tags', 'HEAD')

        return self._remote.clone(
            url, deferred, valid_refs, update_after_clone)

    def pull(self, url, commit_ids=None):
        """
        Tries to pull changes from external location. We use fetch here since
        pull in get does merges and we want to be compatible with hg backend so
        pull == fetch in this case
        """
        self.fetch(url, commit_ids=commit_ids)

    def fetch(self, url, commit_ids=None):
        """
        Tries to fetch changes from external location.
        """
        refs = None

        if commit_ids is not None:
            remote_refs = self._remote.get_remote_refs(url)
            refs = [
                ref for ref in remote_refs if remote_refs[ref] in commit_ids]
        self._remote.fetch(url, refs=refs)

    def set_refs(self, ref_name, commit_id):
        self._remote.set_refs(ref_name, commit_id)

    def remove_ref(self, ref_name):
        self._remote.remove_ref(ref_name)

    def _update_server_info(self):
        """
        runs gits update-server-info command in this repo instance
        """
        self._remote.update_server_info()

    def _current_branch(self):
        """
        Return the name of the current branch.

        It only works for non bare repositories (i.e. repositories with a
        working copy)
        """
        if self.bare:
            raise RepositoryError('Bare git repos do not have active branches')

        if self.is_empty():
            return None

        stdout, _ = self.run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        return stdout.strip()

    def _checkout(self, branch_name, create=False):
        """
        Checkout a branch in the working directory.

        It tries to create the branch if create is True, failing if the branch
        already exists.

        It only works for non bare repositories (i.e. repositories with a
        working copy)
        """
        if self.bare:
            raise RepositoryError('Cannot checkout branches in a bare git repo')

        cmd = ['checkout']
        if create:
            cmd.append('-b')
        cmd.append(branch_name)
        self.run_git_command(cmd, fail_on_stderr=False)

    def _local_clone(self, clone_path, branch_name):
        """
        Create a local clone of the current repo.
        """
        # N.B.(skreft): the --branch option is required as otherwise the shallow
        # clone will only fetch the active branch.
        cmd = ['clone', '--branch', branch_name, '--single-branch',
               self.path, os.path.abspath(clone_path)]
        self.run_git_command(cmd, fail_on_stderr=False)

    def _local_fetch(self, repository_path, branch_name):
        """
        Fetch a branch from a local repository.
        """
        repository_path = os.path.abspath(repository_path)
        if repository_path == self.path:
            raise ValueError('Cannot fetch from the same repository')

        cmd = ['fetch', '--no-tags', repository_path, branch_name]
        self.run_git_command(cmd, fail_on_stderr=False)

    def _last_fetch_heads(self):
        """
        Return the last fetched heads that need merging.

        The algorithm is defined at
        https://github.com/git/git/blob/v2.1.3/git-pull.sh#L283
        """
        if not self.bare:
            fetch_heads_path = os.path.join(self.path, '.git', 'FETCH_HEAD')
        else:
            fetch_heads_path = os.path.join(self.path, 'FETCH_HEAD')

        heads = []
        with open(fetch_heads_path) as f:
            for line in f:
                if '    not-for-merge   ' in line:
                    continue
                line = re.sub('\t.*', '', line, flags=re.DOTALL)
                heads.append(line)

        return heads

    def _local_pull(self, repository_path, branch_name):
        """
        Pull a branch from a local repository.
        """
        if self.bare:
            raise RepositoryError('Cannot pull into a bare git repository')
        # N.B.(skreft): The --ff-only option is to make sure this is a
        # fast-forward (i.e., we are only pulling new changes and there are no
        # conflicts with our current branch)
        # Additionally, that option needs to go before --no-tags, otherwise git
        # pull complains about it being an unknown flag.
        cmd = ['pull', '--ff-only', '--no-tags', repository_path, branch_name]
        self.run_git_command(cmd, fail_on_stderr=False)

    def _local_merge(self, merge_message, user_name, user_email, heads):
        """
        Merge the given head into the checked out branch.

        It will force a merge commit.

        Currently it raises an error if the repo is empty, as it is not possible
        to create a merge commit in an empty repo.

        :param merge_message: The message to use for the merge commit.
        :param heads: the heads to merge.
        """
        if self.bare:
            raise RepositoryError('Cannot merge into a bare git repository')

        if not heads:
            return

        if self.is_empty():
            # TODO(skreft): do somehting more robust in this case.
            raise RepositoryError(
                'Do not know how to merge into empty repositories yet')

        # N.B.(skreft): the --no-ff option is used to enforce the creation of a
        # commit message. We also specify the user who is doing the merge.
        cmd = ['-c', 'user.name=%s' % safe_str(user_name),
               '-c', 'user.email=%s' % safe_str(user_email),
               'merge', '--no-ff', '-m', safe_str(merge_message)]
        cmd.extend(heads)
        try:
            self.run_git_command(cmd, fail_on_stderr=False)
        except RepositoryError:
            # Cleanup any merge leftovers
            self.run_git_command(['merge', '--abort'], fail_on_stderr=False)
            raise

    def _local_push(
            self, source_branch, repository_path, target_branch,
            enable_hooks=False, rc_scm_data=None):
        """
        Push the source_branch to the given repository and target_branch.

        Currently it if the target_branch is not master and the target repo is
        empty, the push will work, but then GitRepository won't be able to find
        the pushed branch or the commits. As the HEAD will be corrupted (i.e.,
        pointing to master, which does not exist).

        It does not run the hooks in the target repo.
        """
        # TODO(skreft): deal with the case in which the target repo is empty,
        # and the target_branch is not master.
        target_repo = GitRepository(repository_path)
        if (not target_repo.bare and
                target_repo._current_branch() == target_branch):
            # Git prevents pushing to the checked out branch, so simulate it by
            # pulling into the target repository.
            target_repo._local_pull(self.path, source_branch)
        else:
            cmd = ['push', os.path.abspath(repository_path),
                   '%s:%s' % (source_branch, target_branch)]
            gitenv = {}
            if rc_scm_data:
                gitenv.update({'RC_SCM_DATA': rc_scm_data})

            if not enable_hooks:
                gitenv['RC_SKIP_HOOKS'] = '1'
            self.run_git_command(cmd, fail_on_stderr=False, extra_env=gitenv)

    def _get_new_pr_branch(self, source_branch, target_branch):
        prefix = 'pr_%s-%s_' % (source_branch, target_branch)
        pr_branches = []
        for branch in self.branches:
            if branch.startswith(prefix):
                pr_branches.append(int(branch[len(prefix):]))

        if not pr_branches:
            branch_id = 0
        else:
            branch_id = max(pr_branches) + 1

        return '%s%d' % (prefix, branch_id)

    def _merge_repo(self, shadow_repository_path, target_ref,
                    source_repo, source_ref, merge_message,
                    merger_name, merger_email, dry_run=False):
        if target_ref.commit_id != self.branches[target_ref.name]:
            return MergeResponse(
                False, False, None, MergeFailureReason.TARGET_IS_NOT_HEAD)

        shadow_repo = GitRepository(shadow_repository_path)
        shadow_repo._checkout(target_ref.name)
        shadow_repo._local_pull(self.path, target_ref.name)
        # Need to reload repo to invalidate the cache, or otherwise we cannot
        # retrieve the last target commit.
        shadow_repo = GitRepository(shadow_repository_path)
        if target_ref.commit_id != shadow_repo.branches[target_ref.name]:
            return MergeResponse(
                False, False, None, MergeFailureReason.TARGET_IS_NOT_HEAD)

        pr_branch = shadow_repo._get_new_pr_branch(
            source_ref.name, target_ref.name)
        shadow_repo._checkout(pr_branch, create=True)
        try:
            shadow_repo._local_fetch(source_repo.path, source_ref.name)
        except RepositoryError as e:
            log.exception('Failure when doing local fetch on git shadow repo')
            return MergeResponse(
                False, False, None, MergeFailureReason.MISSING_COMMIT)

        merge_commit_id = None
        merge_failure_reason = MergeFailureReason.NONE
        try:
            shadow_repo._local_merge(merge_message, merger_name, merger_email,
                                     [source_ref.commit_id])
            merge_possible = True
        except RepositoryError as e:
            log.exception('Failure when doing local merge on git shadow repo')
            merge_possible = False
            merge_failure_reason = MergeFailureReason.MERGE_FAILED

        if merge_possible and not dry_run:
            try:
                shadow_repo._local_push(
                    pr_branch, self.path, target_ref.name, enable_hooks=True,
                    rc_scm_data=self.config.get('rhodecode', 'RC_SCM_DATA'))
                merge_succeeded = True
                # Need to reload repo to invalidate the cache, or otherwise we
                # cannot retrieve the merge commit.
                shadow_repo = GitRepository(shadow_repository_path)
                merge_commit_id = shadow_repo.branches[pr_branch]
            except RepositoryError as e:
                log.exception(
                    'Failure when doing local push on git shadow repo')
                merge_succeeded = False
                merge_failure_reason = MergeFailureReason.PUSH_FAILED
        else:
            merge_succeeded = False

        return MergeResponse(
            merge_possible, merge_succeeded, merge_commit_id,
            merge_failure_reason)

    def _get_shadow_repository_path(self, workspace_id):
        # The name of the shadow repository must start with '.', so it is
        # skipped by 'rhodecode.lib.utils.get_filesystem_repos'.
        return os.path.join(
            os.path.dirname(self.path),
            '.__shadow_%s_%s' % (os.path.basename(self.path), workspace_id))

    def _maybe_prepare_merge_workspace(self, workspace_id, target_ref):
        shadow_repository_path = self._get_shadow_repository_path(workspace_id)
        if not os.path.exists(shadow_repository_path):
            self._local_clone(shadow_repository_path, target_ref.name)

        return shadow_repository_path

    def cleanup_merge_workspace(self, workspace_id):
        shadow_repository_path = self._get_shadow_repository_path(workspace_id)
        shutil.rmtree(shadow_repository_path, ignore_errors=True)
