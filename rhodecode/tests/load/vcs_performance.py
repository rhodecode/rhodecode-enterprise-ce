# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
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
VCS Performance measurement tool

Usage:

- Check that required vcs keys can be found in ~/.hgrc and ~/.netrc

- Start a local instance of RhodeCode Enterprise

- Launch the script:

    TMPDIR=/tmp python vcs_performance.py \
        --host=http://vm:5000 \
        --api-key=55c4a33688577da24183dcac5fde4dddfdbf18dc \
        --commits=10 --repositories=100 --log-level=info
"""

import argparse
import functools
import logging
import os
import shutil
import subprocess
import tempfile
import time
from itertools import chain

from api import RCApi, ApiError


log = logging.getLogger(__name__)


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


def mean(container):
    """Return the mean of the container."""
    if not container:
        return -1.0
    return sum(container) / len(container)


class Config(object):
    args = None

    def __init__(self):
        parser = argparse.ArgumentParser(description='Runs VCS load tests')
        parser.add_argument(
            '--host', dest='host', action='store', required=True,
            help='RhodeCode Enterprise host')
        parser.add_argument(
            '--api-key', dest='api_key', action='store', required=True,
            help='API Key')
        parser.add_argument(
            '--file-size', dest='file_size', action='store', required=False,
            default=1, type=int, help='File size in MB')
        parser.add_argument(
            '--repositories', dest='repositories', action='store',
            required=False, default=1, type=int,
            help='Number of repositories')
        parser.add_argument(
            '--commits', dest='commits', action='store', required=False,
            default=1, type=int, help='Number of commits')
        parser.add_argument(
            '--log-level', dest='log_level', action='store', required=False,
            default='error', help='Logging level')
        self.args = parser.parse_args()

    def __getattr__(self, attr):
        return getattr(self.args, attr)


class Repository(object):
    FILE_NAME_TEMPLATE = "test_{:09d}.bin"

    def __init__(self, name, base_path, api):
        self.name = name
        self.path = os.path.join(base_path, name)
        self.api = api

    def create(self):
        self._create_filesystem_repo(self.path)
        try:
            self.url = self.api.create_repo(
                self.name, self.TYPE, 'Performance tests')
        except ApiError as e:
            log.error('api: {}'.format(e))

    def delete(self):
        self._delete_filesystem_repo()
        try:
            self.api.delete_repo(self.name)
        except ApiError as e:
            log.error('api: {}'.format(e))

    def create_commits(self, number, file_size):
        for i in xrange(number):
            file_name = self.FILE_NAME_TEMPLATE.format(i)
            log.debug("Create commit {}".format(file_name))
            self._create_file(file_name, file_size)
            self._create_commit(file_name)

    @timed
    def push(self):
        raise NotImplementedError()

    @timed
    def clone(self, destination_path):
        raise NotImplementedError()

    @timed
    def pull(self):
        raise NotImplementedError()

    def _run(self, *args):
        command = [self.BASE_COMMAND] + list(args)
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process.communicate()

    def _create_file(self, name, size):
        file_name = os.path.join(self.path, name)
        with open(file_name, 'wb') as f:
            f.write(os.urandom(1024))

    def _delete_filesystem_repo(self):
        shutil.rmtree(self.path)

    def _create_filesystem_repo(self, path):
        raise NotImplementedError()

    def _create_commit(self, file_name):
        raise NotImplementedError()


class GitRepository(Repository):
    TYPE = 'git'
    BASE_COMMAND = 'git'

    @timed
    def push(self):
        os.chdir(self.path)
        self._run('push', '--set-upstream', self.url, 'master')

    @timed
    def clone(self, destination_path):
        self._run('clone', self.url, os.path.join(destination_path, self.name))

    @timed
    def pull(self, destination_path):
        path = os.path.join(destination_path, self.name)
        self._create_filesystem_repo(path)
        os.chdir(path)
        self._run('remote', 'add', 'origin', self.url)
        self._run('pull', 'origin', 'master')

    def _create_filesystem_repo(self, path):
        self._run('init', path)

    def _create_commit(self, file_name):
        os.chdir(self.path)
        self._run('add', file_name)
        self._run('commit', file_name, '-m', '"Add {}"'.format(file_name))


class HgRepository(Repository):
    TYPE = 'hg'
    BASE_COMMAND = 'hg'

    @timed
    def push(self):
        os.chdir(self.path)
        self._run('push', self.url)

    @timed
    def clone(self, destination_path):
        self._run('clone', self.url, os.path.join(destination_path, self.name))

    @timed
    def pull(self, destination_path):
        path = os.path.join(destination_path, self.name)
        self._create_filesystem_repo(path)
        os.chdir(path)
        self._run('pull', '-r', 'tip', self.url)

    def _create_filesystem_repo(self, path):
        self._run('init', path)

    def _create_commit(self, file_name):
        os.chdir(self.path)
        self._run('add', file_name)
        self._run('commit', file_name, '-m', '"Add {}"'.format(file_name))


class Benchmark(object):
    REPO_CLASSES = {
        'git': GitRepository,
        'hg': HgRepository
    }
    REPO_NAME = '{}_performance_{:03d}'

    def __init__(self, config):
        self.api = RCApi(api_key=config.api_key, rc_endpoint=config.host)
        self.source_path = tempfile.mkdtemp(suffix='vcsperformance')

        self.config = config
        self.git_repos = []
        self.hg_repos = []

        self._set_log_level()

    def start(self):
        self._create_repos()
        repos = {
            'git': self.git_repos,
            'hg': self.hg_repos
        }

        clone_destination_path = tempfile.mkdtemp(suffix='clone')
        pull_destination_path = tempfile.mkdtemp(suffix='pull')
        operations = [
            ('push', ),
            ('clone', clone_destination_path),
            ('pull', pull_destination_path)
        ]

        for operation in operations:
            for type_ in repos:
                times = self._measure(repos[type_], *operation)
                print("Mean {} {} time: {:.3f} sec.".format(
                    type_, operation[0], mean(times)))

    def cleanup(self):
        log.info("Cleaning up...")
        for repo in chain(self.git_repos, self.hg_repos):
            repo.delete()

    def _measure(self, repos, operation, *args):
        times = []
        for repo in repos:
            method = getattr(repo, operation)
            times.append(method(*args))
        return times

    def _create_repos(self):
        log.info("Creating repositories...")
        for i in xrange(self.config.repositories):
            self.git_repos.append(self._create_repo('git', i))
            self.hg_repos.append(self._create_repo('hg', i))

    def _create_repo(self, type_, id_):
        RepoClass = self.REPO_CLASSES[type_]
        repo = RepoClass(
            self.REPO_NAME.format(type_, id_), self.source_path, self.api)
        repo.create()
        repo.create_commits(self.config.commits, self.config.file_size)
        return repo

    def _set_log_level(self):
        try:
            log_level = getattr(logging, config.log_level.upper())
        except:
            log_level = logging.ERROR
        handler = logging.StreamHandler()
        log.addHandler(handler)
        log.setLevel(log_level)

if __name__ == '__main__':
    config = Config()
    benchmark = Benchmark(config)
    try:
        benchmark.start()
    finally:
        benchmark.cleanup()
