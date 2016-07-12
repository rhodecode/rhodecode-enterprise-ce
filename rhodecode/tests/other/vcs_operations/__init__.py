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
Base for test suite for making push/pull operations.

.. important::

   You must have git >= 1.8.5 for tests to work fine. With 68b939b git started
   to redirect things to stderr instead of stdout.
"""

from os.path import join as jn
from subprocess import Popen, PIPE
import logging
import os
import tempfile

from rhodecode.tests import GIT_REPO, HG_REPO

DEBUG = True
RC_LOG = os.path.join(tempfile.gettempdir(), 'rc.log')
REPO_GROUP = 'a_repo_group'
HG_REPO_WITH_GROUP = '%s/%s' % (REPO_GROUP, HG_REPO)
GIT_REPO_WITH_GROUP = '%s/%s' % (REPO_GROUP, GIT_REPO)

log = logging.getLogger(__name__)


class Command(object):

    def __init__(self, cwd):
        self.cwd = cwd
        self.process = None

    def execute(self, cmd, *args):
        """
        Runs command on the system with given ``args``.
        """

        command = cmd + ' ' + ' '.join(args)
        if DEBUG:
            log.debug('*** CMD %s ***' % (command,))

        env = dict(os.environ)
        # Delete coverage variables, as they make the test fail for Mercurial
        for key in env.keys():
            if key.startswith('COV_CORE_'):
                del env[key]

        self.process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE,
                             cwd=self.cwd, env=env)
        stdout, stderr = self.process.communicate()
        if DEBUG:
            log.debug('STDOUT:%s' % (stdout,))
            log.debug('STDERR:%s' % (stderr,))
        return stdout, stderr

    def assert_returncode_success(self):
        assert self.process.returncode == 0


def _add_files_and_push(vcs, dest, clone_url=None, **kwargs):
    """
    Generate some files, add it to DEST repo and push back
    vcs is git or hg and defines what VCS we want to make those files for
    """
    # commit some stuff into this repo
    cwd = path = jn(dest)
    added_file = jn(path, '%ssetup.py' % tempfile._RandomNameSequence().next())
    Command(cwd).execute('touch %s' % added_file)
    Command(cwd).execute('%s add %s' % (vcs, added_file))
    author_str = 'Marcin Kuźminski <me@email.com>'

    git_ident = "git config user.name {} && git config user.email {}".format(
            'Marcin Kuźminski', 'me@email.com')

    for i in xrange(kwargs.get('files_no', 3)):
        cmd = """echo 'added_line%s' >> %s""" % (i, added_file)
        Command(cwd).execute(cmd)
        if vcs == 'hg':
            cmd = """hg commit -m 'commited new %s' -u '%s' %s """ % (
                i, author_str, added_file
            )
        elif vcs == 'git':
            cmd = """%s && git commit -m 'commited new %s' %s""" % (
                git_ident, i, added_file)
        Command(cwd).execute(cmd)

    # PUSH it back
    stdout = stderr = None
    if vcs == 'hg':
        stdout, stderr = Command(cwd).execute(
            'hg push --verbose', clone_url)
    elif vcs == 'git':
        stdout, stderr = Command(cwd).execute(
            """%s && git push --verbose %s master""" % (
                git_ident, clone_url))

    return stdout, stderr


def _check_proper_git_push(
        stdout, stderr, branch='master', should_set_default_branch=False):
    # Note: Git is writing most information to stderr intentionally
    assert 'fatal' not in stderr
    assert 'rejected' not in stderr
    assert 'Pushing to' in stderr
    assert '%s -> %s' % (branch, branch) in stderr

    if should_set_default_branch:
        assert "Setting default branch to %s" % branch in stderr
    else:
        assert "Setting default branch" not in stderr


def _check_proper_clone(stdout, stderr, vcs):
    if vcs == 'hg':
        assert 'requesting all changes' in stdout
        assert 'adding changesets' in stdout
        assert 'adding manifests' in stdout
        assert 'adding file changes' in stdout

        assert stderr == ''

    if vcs == 'git':
        assert '' == stdout
        assert 'Cloning into' in stderr
        assert 'abort:' not in stderr
        assert 'fatal:' not in stderr
