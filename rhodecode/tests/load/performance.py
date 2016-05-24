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
This is a locustio based test scenario simulating users on the web interface.

To run it::

   locust -f rhodecode/tests/load/performance.py --no-web -c 5 -r 5

Discover details regarding the command with the ``--help`` parameter and the
documentation at http://docs.locust.io/en/latest/ .

With the environment variable `SEED` it is possible to create more or less
repeatable runs. They are not fully repeatable, since the response times from
the server vary and so two test runs with the same seed value will sooner or
later run out of sync.
"""

import logging
import os
import random
import re

from locust import HttpLocust, TaskSet, task


log = logging.getLogger('performance')

# List of repositories which shall be used during the test run
REPOSITORIES = [
    'vcs_test_git',
    'vcs_test_hg',
    'vcs_test_svn',
#    'linux',
#    'cpython',
#    'git',
]

HOST = 'http://localhost:5000'


# List of user accounts to login to the test system.
# Format: tuple(username, password)
USER_ACCOUNTS = [
    ('test_admin', 'test12'),
]

# Toggle this to show and aggregate results on individual URLs
SHOW_DETAILS = False

# Used to initialize pseudo random generators which are used to select
# the next task, to take a decision etc.
_seed = os.environ.get('SEED', None)

try:
    _seed = int(_seed)
except ValueError:
    pass

if (isinstance(_seed, basestring) and
        os.environ.get('PYTHONHASHSEED', None) == 'random'):
    print("Setting a SEED does not work if PYTHONHASHSEED is set to random.")
    print("Use a numeric value for SEED or unset PYTHONHASHSEED.")
    exit(1)

log.info("Using SEED %s", _seed)

_seeder = random.Random(_seed)


class BaseTaskSet(TaskSet):

    _decision = None
    _random = None

    def __init__(self, parent):
        super(BaseTaskSet, self).__init__(parent)
        log_name = "user.%s" % (id(self.locust), )
        self.log = log.getChild(log_name)

    @property
    def decision(self):
        if self._decision:
            return self._decision
        return self.parent.decision

    @property
    def random(self):
        if self._random:
            return self._random
        return self.parent.random

    def get_next_task(self):
        task = self.random.choice(self.tasks)
        self.log.debug("next task %s", task.__name__)
        return task

    def wait(self):
        millis = self.random.randint(self.min_wait, self.max_wait)
        seconds = millis / 1000.0
        self.log.debug("sleeping %s", seconds)
        self._sleep(seconds)


class BrowseLatestChanges(BaseTaskSet):
    """
    User browsing through the latest changes form the summary page
    """
    page_size = 10

    def on_start(self):
        self.repo = self.decision.choose_repository()
        self.page = 1
        self.response = self.client.get('/%s' % (self.repo, ))

    @task(20)
    def goto_next_page(self):
        self.page += 1
        self.get_changelog_summary()

    @task(5)
    def goto_prev_page(self):
        self.page -= 1
        if self.page < 0:
            self.interrupt()
        self.get_changelog_summary()

    @task(20)
    def open_commit(self):
        commits = get_commit_links(self.response.content)
        commit = self.decision.choose(commits, "commit")
        if not commit:
            return
        self.client.get(
            commit,
            name=self._commit_name(commit))

    def get_changelog_summary(self):
        summary = '/%s?size=%s&page=%s' % (
            self.repo, self.page_size, self.page)
        self.response = self.client.get(
            summary,
            headers={'X-PARTIAL-XHR': 'true'},
            name=self._changelog_summary_name(summary))

    @task(1)
    def stop(self):
        self.interrupt()

    def _commit_name(self, url):
        if SHOW_DETAILS:
            return url
        return '/%s/changeset/{{commit_id}}' % (self.repo, )

    def _changelog_summary_name(self, url):
        if SHOW_DETAILS:
            return url
        return '/%s?size={{size}}&page={{page}}' % (self.repo, )


class BrowseChangelog(BaseTaskSet):

    def on_start(self):
        self.repo = self.decision.choose_repository()
        self.page = 1
        self.open_changelog_page()

    @task(20)
    def goto_next_page(self):
        self.page += 1
        self.open_changelog_page()

    @task(5)
    def goto_prev_page(self):
        self.page -= 1
        self.open_changelog_page()

    @task(20)
    def open_commit(self):
        commits = get_commit_links(self.response.content)
        commit = self.decision.choose(commits, "commit")
        if not commit:
            return
        self.client.get(
            commit,
            name=self._commit_name(commit))

    def open_changelog_page(self):
        if self.page <= 0:
            self.interrupt()
        changelog = '/%s/changelog?page=%s' % (self.repo, self.page)
        self.response = self.client.get(
            changelog,
            name=self._changelog_page_name(changelog))

    @task(1)
    def stop(self):
        self.interrupt()

    def _commit_name(self, url):
        if SHOW_DETAILS:
            return url
        return '/%s/changeset/{{commit_id}}' % (self.repo, )

    def _changelog_page_name(self, url):
        if SHOW_DETAILS:
            return url
        return '/%s/changelog/?page={{page}}' % (self.repo, )


class BrowseFiles(BaseTaskSet):

    def on_start(self):
        self.stack = []
        self.repo = self.decision.choose_repository()
        self.fetch_directory()

    def fetch_directory(self, url=None):
        if not url:
            url = '/%s/files/tip/' % (self.repo, )
        response = self.client.get(url, name=self._url_name('dir', url=url))
        self.stack.append({
            'directories': get_directory_links(response.content, self.repo),
            'files': get_file_links(response.content, self.repo, 'files'),
            'files_raw': get_file_links(response.content, self.repo, 'raw'),
            'files_annotate': get_file_links(response.content, self.repo, 'annotate'),
        })

    @task(10)
    def browse_directory(self):
        dirs = self.stack[-1]['directories']
        if not dirs:
            return
        url = self.decision.choose(dirs, "directory")
        self.fetch_directory(url=url)

    @task(10)
    def browse_file(self):
        files = self.stack[-1]['files']
        if not files:
            return
        file_url = self.decision.choose(files, "file")
        self.client.get(file_url, name=self._url_name('file', file_url))

    @task(10)
    def browse_raw_file(self):
        files = self.stack[-1]['files_raw']
        if not files:
            return
        file_url = self.decision.choose(files, "file")
        self.client.get(file_url, name=self._url_name('file_raw', file_url))

    @task(10)
    def browse_annotate_file(self):
        files = self.stack[-1]['files_annotate']
        if not files:
            return
        file_url = self.decision.choose(files, "file")
        self.client.get(
            file_url, name=self._url_name('file_annotate', file_url))

    @task(5)
    def back_to_parent_directory(self):
        if not len(self.stack) > 1:
            return
        self.stack.pop()

    @task(1)
    def stop(self):
        self.interrupt()

    def _url_name(self, kind, url):
        if SHOW_DETAILS:
            return url
        return '/%s/%s/{{commit_id}}/{{path}}' % (self.repo, kind)


class UserBehavior(BaseTaskSet):

    tasks = [
        (BrowseLatestChanges, 1),
        (BrowseChangelog, 1),
        (BrowseFiles, 2),
    ]

    def on_start(self):
        seed = getattr(self.locust, "seed", None)
        self._decision = ChoiceMaker(random.Random(seed), log=self.log)
        self._random = random.Random(seed)
        user_account = self.decision.choose_user()
        data = {
            'username': user_account[0],
            'password': user_account[1],
        }
        response = self.client.post(
            '/_admin/login?came_from=/', data=data, allow_redirects=False)

        # Sanity check that the login worked out.
        # Successful login means we are redirected to "came_from".
        assert response.status_code == 302
        assert response.headers['location'] == self.locust.host + '/'

    @task(2)
    def browse_index_page(self):
        self.client.get('/')


class WebsiteUser(HttpLocust):
    host = HOST
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 1000

    def __init__(self):
        super(WebsiteUser, self).__init__()
        self.seed = _seeder.random()
        log.info("WebsiteUser with seed %s", self.seed)


class ChoiceMaker(object):

    def __init__(self, random, log=None):
        self._random = random
        self.log = log

    def choose(self, choices, kind=None):
        if len(choices) == 0:
            self.log.debug("nothing to choose from")
            return None

        item = self._random.choice(choices)
        self.log.debug("choosing %s %s", kind or "item", item)
        return item

    def choose_user(self):
        return self.choose(USER_ACCOUNTS, "user")

    def choose_repository(self):
        return self.choose(REPOSITORIES, "repository")


def get_commit_links(content):
    # TODO: find out a way to read the HTML and grab elements by selector
    links = re.findall(
        r'<a.*?class="message-link".*?href="(.*?)".*?/a>', content)
    return links


def get_directory_links(content, repo_name):
    return _get_links(content, 'browser-dir')


def get_file_links(content, repo_name, link_type):

    def _process(lnk, repo_name, link_type):
        if link_type == 'files':
            return lnk
        elif link_type == 'raw':
            return re.sub(r'%s/files/' % repo_name, r'%s/raw/' % repo_name, lnk)
        elif link_type == 'annotate':
            return re.sub(r'%s/files/' % repo_name, r'%s/annotate/' % repo_name, lnk)
    links = []
    for lnk in _get_links(content, 'browser-file'):
        links.append(_process(lnk, repo_name, link_type))
    return links


def _get_links(content, class_name):
    return re.findall(
        r'<a.*?class="' + class_name + r'.*?href="(.*?)".*?/a>',
        content)
