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
Load tests of certain vcs operations which can be executed by the test runner.

To gather timing information, run like this::

   py.test rhodecode/tests/vcs/test_load.py --duration=0

To use this file with an old codebase which does not provide a compatible
fixture setup, make sure that py.test is installed inside of the environment
and copy this file in a place outside of the current repository::

   TEST_HG_REPO=~/tmp/repos/vcs-hg TEST_GIT_REPO=~/tmp/repos/vcs-git \
   py.test test_load.py --duration=0

"""
import os

import pytest

from rhodecode.lib.vcs import create_vcsserver_proxy
from rhodecode.lib.vcs.backends import get_backend, get_vcs_instance
from rhodecode.tests import TEST_HG_REPO, TEST_GIT_REPO


# Allows to inject different repository paths. Used to run this
# file with an pre-pytest codebase of rhodecode.
TEST_HG_REPO = os.environ.get('TEST_HG_REPO', TEST_HG_REPO)
TEST_GIT_REPO = os.environ.get('TEST_GIT_REPO', TEST_GIT_REPO)


@pytest.fixture(params=('hg', 'git'))
def repo(request, pylonsapp):
    repos = {
        'hg': TEST_HG_REPO,
        'git': TEST_GIT_REPO,
    }
    repo = get_vcs_instance(repos[request.param])
    return repo


@pytest.fixture
def server(pylonsapp):
    """
    Returns a proxy of the server object.
    """
    server_and_port = pylonsapp.config['vcs.server']
    protocol = pylonsapp.config['vcs.server.protocol']
    server = create_vcsserver_proxy(server_and_port, protocol)
    return server


def test_server_echo(server):
    resp = server.echo('a')
    assert resp == 'a'


def test_server_echo_no_data(server, repeat):
    for x in xrange(repeat):
        server.echo(None)


@pytest.mark.parametrize("payload", [
    {'a': 'dict', 'with': 'values'},
    [1, 2, 3, 4, 5] * 5,
    ['a', 1, 1.2, None, {}] * 5,
], ids=['dict', 'list-int', 'list-mix'])
def test_server_echo_small_payload(server, repeat, payload):
    for x in xrange(repeat):
        server.echo(payload)


@pytest.mark.parametrize("payload", [
    [{'a': 'dict', 'with': 'values'}] * 100,
    [1, 2, 3, 4, 5] * 100,
    ['a', 1, 1.2, None, {}] * 100,
], ids=['dict', 'list-int', 'list-mix'])
def test_server_echo_middle_payload(server, repeat, payload):
    for x in xrange(repeat):
        server.echo(payload)


@pytest.mark.parametrize("payload", [
    [{'a': 'dict', 'with': 'values'}] * 1000,
    [1, 2, 3, 4, 5] * 1000,
    ['a', 1, 1.2, None, {}] * 1000,
], ids=['dict', 'list-int', 'list-mix'])
def test_server_echo_large_payload(server, repeat, payload):
    for x in xrange(repeat):
        server.echo(payload)


def test_create_repo_object(repo, repeat):
    backend = get_backend(repo.alias)
    for x in xrange(repeat):
        repo = backend(repo.path)


def test_get_first_commit_of_repository(repo, repeat):
    for x in xrange(repeat):
        repo.get_commit(commit_idx=1)


def test_get_first_commits_slicing(repo, repeat):
    count_commits = repeat / 10
    commit = repo[0:count_commits]
    commit = list(commit)


def test_get_first_commits(repo, repeat):
    end_idx = repeat / 10
    start = repo.commit_ids[0]
    end = repo.commit_ids[end_idx]
    commit = repo.get_commits(start_id=start, end_id=end)
    commit = list(commit)


def test_fetch_file(repo, repeat):
    path = 'vcs/cli.py'
    tip = repo.get_commit()
    for x in xrange(repeat):
        tip.get_file_content(path=path)


def test_annotate_file(repo, repeat):
    path = 'vcs/cli.py'
    tip = repo.get_commit()
    for x in xrange(repeat / 10):
        annotation_generator = tip.get_file_annotate(path=path)
        list(annotation_generator)


def test_read_full_file_tree_using_walk(repo):
    tip = repo.get_commit()

    for topnode, dirs, files in tip.walk():
        for f in files:
            len(f.content)


def test_commit_diff(repo, repeat):
    tip = repo.get_commit()
    for x in xrange(repeat / 10):
        tip.diff()


def test_walk_changelog(repo, repeat):
    page_size = 20
    for page in xrange(repeat / 50):
        start = page * page_size
        end = start + page_size - 1
        list(repo[start:end])
