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
Module to test the performance of pull, push and clone operations.

It works by replaying a group of commits to the repo.
"""

import argparse
import collections
import ConfigParser
import functools
import itertools
import os
import pprint
import shutil
import subprocess
import sys
import time

import api


def mean(container):
    """Return the mean of the container."""
    if not container:
        return -1.0
    return sum(container) / len(container)


def keep_cwd(f):
    """Decorator that keeps track of the starting working directory."""
    @functools.wraps(f)
    def wrapped_f(*args, **kwargs):
        cur_dir = os.getcwd()
        try:
            return f(*args, **kwargs)
        finally:
            os.chdir(cur_dir)

    return wrapped_f


def timed(f):
    """Decorator that returns the time it took to execute the function."""
    @functools.wraps(f)
    def wrapped_f(*args, **kwargs):
        start_time = time.time()
        try:
            f(*args, **kwargs)
        finally:
            return time.time() - start_time

    return wrapped_f


def execute(*popenargs, **kwargs):
    """Extension of subprocess.check_output to support writing to stdin."""
    input = kwargs.pop('stdin', None)
    stdin = None
    if input:
        stdin = subprocess.PIPE
    #if 'stderr' not in kwargs:
    #    kwargs['stderr'] = subprocess.PIPE
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdin=stdin, stdout=subprocess.PIPE,
                               *popenargs, **kwargs)
    output, error = process.communicate(input=input)
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        print cmd, output, error
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output


def get_repo_name(repo_url):
    """Extract the repo name from its url."""
    repo_url = repo_url.rstrip('/')
    return repo_url.split('/')[-1].split('.')[0]


class TestPerformanceBase(object):
    def __init__(self, base_dir, repo_url, n_commits, max_commits,
                 skip_commits):
        self.repo_url = repo_url
        self.repo_name = get_repo_name(self.repo_url)
        self.upstream_repo_name = '%s_upstream' % self.repo_name
        self.base_dir = os.path.abspath(base_dir)
        self.n_commits = n_commits
        self.max_commits = max_commits
        self.skip_commits = skip_commits
        self.push_times = []
        self.pull_times = []
        self.empty_pull_times = []
        self.clone_time = -1.0
        self.last_commit = None

        self.cloned_repo = ''
        self.pull_repo = ''
        self.orig_repo = ''

    def run(self):
        try:
            self.test()
        except Exception as error:
            print error
        finally:
            self.cleanup()

            print 'Clone time     :', self.clone_time
            print 'Push time      :', mean(self.push_times)
            print 'Pull time      :', mean(self.pull_times)
            print 'Empty pull time:', mean(self.empty_pull_times)

            return {
                'clone': self.clone_time,
                'push': mean(self.push_times),
                'pull': mean(self.pull_times),
                'empty_pull': mean(self.empty_pull_times),
            }

    @keep_cwd
    def test(self):
        os.chdir(self.base_dir)

        self.orig_repo = os.path.join(self.base_dir, self.repo_name)
        if not os.path.exists(self.orig_repo):
            self.clone_repo(self.repo_url, default_only=True)

        upstream_url = self.create_repo(self.upstream_repo_name, self.repo_type)

        self.add_remote(self.orig_repo, upstream_url)

        self.pull_repo = os.path.join(self.base_dir, '%s_pull' % self.repo_name)
        self.clone_repo(upstream_url, self.pull_repo)

        commits = self.get_commits(self.orig_repo)
        self.last_commit = commits[-1]
        if self.skip_commits:
            self.push(
                self.orig_repo, commits[self.skip_commits - 1], 'upstream')
        commits = commits[self.skip_commits:self.max_commits]

        print 'Working with %d commits' % len(commits)
        for i in xrange(self.n_commits - 1, len(commits), self.n_commits):
            commit = commits[i]
            print 'Processing commit %s (%d)' % (commit, i + 1)
            self.push_times.append(
                self.push(self.orig_repo, commit, 'upstream'))
            self.check_remote_last_commit_is(commit, upstream_url)

            self.pull_times.append(self.pull(self.pull_repo))
            self.check_local_last_commit_is(commit, self.pull_repo)

            self.empty_pull_times.append(self.pull(self.pull_repo))

        self.cloned_repo = os.path.join(self.base_dir,
                                        '%s_clone' % self.repo_name)
        self.clone_time = self.clone_repo(upstream_url, self.cloned_repo)

    def cleanup(self):
        try:
            self.delete_repo(self.upstream_repo_name)
        except api.ApiError:
            # Continue in case we could not delete the repo. Maybe we did not
            # create it in the first place.
            pass

        shutil.rmtree(self.pull_repo, ignore_errors=True)
        shutil.rmtree(self.cloned_repo, ignore_errors=True)

        if os.path.exists(self.orig_repo):
            self.remove_remote(self.orig_repo)


class RhodeCodeMixin(object):
    """Mixin providing the methods to create and delete repos in RhodeCode."""
    def __init__(self, api_key):
        self.api = api.RCApi(api_key=api_key)

    def create_repo(self, repo_name, repo_type):
        return self.api.create_repo(repo_name, repo_type,
                                    'Repo for perfomance testing')

    def delete_repo(self, repo_name):
        return self.api.delete_repo(repo_name)


class GitMixin(object):
    """Mixin providing the git operations."""
    @timed
    def clone_repo(self, repo_url, destination=None, default_only=False):
        args = ['git', 'clone']
        if default_only:
            args.extend(['--branch', 'master', '--single-branch'])
        args.append(repo_url)
        if destination:
            args.append(destination)
        execute(args)

    @keep_cwd
    def add_remote(self, repo, remote_url, remote_name='upstream'):
        self.remove_remote(repo, remote_name)
        os.chdir(repo)
        execute(['git', 'remote', 'add', remote_name, remote_url])

    @keep_cwd
    def remove_remote(self, repo, remote_name='upstream'):
        os.chdir(repo)
        remotes = execute(['git', 'remote']).split('\n')
        if remote_name in remotes:
            execute(['git', 'remote', 'remove', remote_name])

    @keep_cwd
    def get_commits(self, repo, branch='master'):
        os.chdir(repo)
        commits_list = execute(
            ['git', 'log', '--first-parent', branch, '--pretty=%H'])
        return commits_list.strip().split('\n')[::-1]

    @timed
    def push(self, repo, commit, remote_name=None):
        os.chdir(repo)
        try:
            execute(['git', 'reset', '--soft', commit])
            args = ['git', 'push']
            if remote_name:
                args.append(remote_name)
            execute(args)
        finally:
            execute(['git', 'reset', '--soft', 'HEAD@{1}'])

    @timed
    def pull(self, repo):
        os.chdir(repo)
        execute(['git', 'pull'])

    def _remote_last_commit(self, repo_url):
        output = execute(['git', 'ls-remote', repo_url, 'HEAD'])
        return output.split()[0]

    def check_remote_last_commit_is(self, commit, repo_url):
        last_remote_commit = self._remote_last_commit(repo_url)
        if last_remote_commit != commit:
            raise Exception('Push did not work, expected commit %s but got %s' %
                            (commit, last_remote_commit))

    @keep_cwd
    def _local_last_commit(self, repo):
        os.chdir(repo)
        return execute(['git', 'rev-parse', 'HEAD']).strip()

    def check_local_last_commit_is(self, commit, repo):
        last_local_commit = self._local_last_commit(repo)
        if last_local_commit != commit:
            raise Exception('Pull did not work, expected commit %s but got %s' %
                            (commit, last_local_commit))


class HgMixin(object):
    """Mixin providing the mercurial operations."""
    @timed
    def clone_repo(self, repo_url, destination=None, default_only=False):
        args = ['hg', 'clone']
        if default_only:
            args.extend(['--branch', 'default'])
        args.append(repo_url)
        if destination:
            args.append(destination)
        execute(args)

    @keep_cwd
    def add_remote(self, repo, remote_url, remote_name='upstream'):
        self.remove_remote(repo, remote_name)
        os.chdir(repo)
        hgrc = ConfigParser.RawConfigParser()
        hgrc.read('.hg/hgrc')
        hgrc.set('paths', remote_name, remote_url)
        with open('.hg/hgrc', 'w') as f:
            hgrc.write(f)

    @keep_cwd
    def remove_remote(self, repo, remote_name='upstream'):
        os.chdir(repo)
        hgrc = ConfigParser.RawConfigParser()
        hgrc.read('.hg/hgrc')
        hgrc.remove_option('paths', remote_name)
        with open('.hg/hgrc', 'w') as f:
            hgrc.write(f)

    @keep_cwd
    def get_commits(self, repo, branch='default'):
        os.chdir(repo)
        # See http://stackoverflow.com/questions/15376649/is-there-a-mercurial-equivalent-to-git-log-first-parent
        commits_list = execute(['hg', 'log', '--branch', branch, '--template',
                                '{node}\n', '--follow-first'])
        return commits_list.strip().split('\n')[::-1]

    @timed
    def push(self, repo, commit, remote_name=None):
        os.chdir(repo)
        args = ['hg', 'push', '--rev', commit, '--new-branch']
        if remote_name:
            args.append(remote_name)
        execute(args)

    @timed
    def pull(self, repo):
        os.chdir(repo)
        execute(['hg', '--config', 'alias.pull=pull', 'pull', '-u'])

    def _remote_last_commit(self, repo_url):
        return execute(['hg', 'identify', repo_url])[:12]

    def check_remote_last_commit_is(self, commit, repo_url):
        last_remote_commit = self._remote_last_commit(repo_url)
        if not commit.startswith(last_remote_commit):
            raise Exception('Push did not work, expected commit %s but got %s' %
                            (commit, last_remote_commit))

    @keep_cwd
    def _local_last_commit(self, repo):
        os.chdir(repo)
        return execute(['hg', 'identify'])[:12]

    def check_local_last_commit_is(self, commit, repo):
        last_local_commit = self._local_last_commit(repo)
        if not commit.startswith(last_local_commit):
            raise Exception('Pull did not work, expected commit %s but got %s' %
                            (commit, last_local_commit))


class GitTestPerformance(GitMixin, RhodeCodeMixin, TestPerformanceBase):
    def __init__(self, base_dir, repo_url, n_commits, max_commits, skip_commits,
                 api_key):
        TestPerformanceBase.__init__(self, base_dir, repo_url, n_commits,
                                     max_commits, skip_commits)
        RhodeCodeMixin.__init__(self, api_key)
        self.repo_type = 'git'


class HgTestPerformance(HgMixin, RhodeCodeMixin, TestPerformanceBase):
    def __init__(self, base_dir, repo_url, n_commits, max_commits, skip_commits,
                 api_key):
        TestPerformanceBase.__init__(self, base_dir, repo_url, n_commits,
                                     max_commits, skip_commits)
        RhodeCodeMixin.__init__(self, api_key)
        self.repo_type = 'hg'


def get_test(base_dir, repo_url, repo_type, step, max_commits, skip_commits,
             api_key):
    max_commits = min(10 * step,
                      int((max_commits - skip_commits) / step) * step)
    max_commits += skip_commits
    if repo_type == 'git':
        return GitTestPerformance(
            base_dir, repo_url, step, max_commits, skip_commits, api_key)
    elif repo_type == 'hg':
        return HgTestPerformance(
            base_dir, repo_url, step, max_commits, skip_commits, api_key)


def main(argv):
    parser = argparse.ArgumentParser(
        description='Performance tests for push/pull/clone for git and ' +
                    'mercurial repos.')
    parser.add_argument(
        '--tests', dest='tests', action='store', required=False, default='all',
        help='The tests to run. Default: all. But could be any comma ' +
             'separated list with python, hg, kernel or git')
    parser.add_argument(
        '--sizes', dest='sizes', action='store', required=False,
        default='1,10,100,1000,2500',
        help='The sizes to use. Default: 1,10,100,1000,2500')
    parser.add_argument(
        '--dir', dest='dir', action='store', required=True,
        help='The dir where to store the repos')
    parser.add_argument(
        '--api-key', dest='api_key', action='store', required=True,
        help='The api key of RhodeCode')
    options = parser.parse_args(argv[1:])
    print options

    test_config = {
        'python': {
            'url': 'https://hg.python.org/cpython/',
            'limit': 23322,
            'type': 'hg',
            # Do not time the first commit, as it is HUGE!
            'skip': 1,
        },
        'hg': {
            'url': 'http://selenic.com/hg',
            'limit': 14396,
            'type': 'hg',
        },
        'kernel': {
            'url': 'https://github.com/torvalds/linux.git',
            'limit': 46271,
            'type': 'git',
        },
        'git': {
            'url': 'https://github.com/git/git.git',
            'limit': 13525,
            'type': 'git',
        }

    }

    test_names = options.tests.split(',')
    if test_names == ['all']:
        test_names = test_config.keys()
    if not set(test_names) <= set(test_config.keys()):
        print ('Invalid tests: only %s are valid but specified %s' %
               (test_config.keys(), test_names))
        return 1

    sizes = options.sizes.split(',')
    sizes = map(int, sizes)

    base_dir = options.dir
    api_key = options.api_key
    results = collections.defaultdict(dict)
    for test_name, size in itertools.product(test_names, sizes):
        test = get_test(base_dir,
                        test_config[test_name]['url'],
                        test_config[test_name]['type'],
                        size,
                        test_config[test_name]['limit'],
                        test_config[test_name].get('skip', 0),
                        api_key)
        print '*' * 80
        print 'Running performance test: %s with size %d' % (test_name, size)
        print '*' * 80
        results[test_name][size] = test.run()
    pprint.pprint(dict(results))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
