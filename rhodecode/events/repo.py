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

from rhodecode.model.db import Repository, Session
from rhodecode.events import RhodecodeEvent


class RepoEvent(RhodecodeEvent):
    """
    Base class for events acting on a repository.

    :param repo: a :class:`Repository` instance
    """
    def __init__(self, repo):
        self.repo = repo


class RepoPreCreateEvent(RepoEvent):
    """
    An instance of this class is emitted as an :term:`event` before a repo is
    created.
    """
    name = 'repo-pre-create'


class RepoCreatedEvent(RepoEvent):
    """
    An instance of this class is emitted as an :term:`event` whenever a repo is
    created.
    """
    name = 'repo-created'


class RepoPreDeleteEvent(RepoEvent):
    """
    An instance of this class is emitted as an :term:`event` whenever a repo is
    created.
    """
    name = 'repo-pre-delete'


class RepoDeletedEvent(RepoEvent):
    """
    An instance of this class is emitted as an :term:`event` whenever a repo is
    created.
    """
    name = 'repo-deleted'


class RepoVCSEvent(RepoEvent):
    """
    Base class for events triggered by the VCS
    """
    def __init__(self, repo_name, extras):
        self.repo = Repository.get_by_repo_name(repo_name)
        if not self.repo:
            raise Exception('repo by this name %s does not exist' % repo_name)
        self.extras = extras
        super(RepoVCSEvent, self).__init__(self.repo)


class RepoPrePullEvent(RepoVCSEvent):
    """
    An instance of this class is emitted as an :term:`event` before commits
    are pulled from a repo.
    """
    name = 'repo-pre-pull'


class RepoPullEvent(RepoVCSEvent):
    """
    An instance of this class is emitted as an :term:`event` after commits
    are pulled from a repo.
    """
    name = 'repo-pull'


class RepoPrePushEvent(RepoVCSEvent):
    """
    An instance of this class is emitted as an :term:`event` before commits
    are pushed to a repo.
    """
    name = 'repo-pre-push'


class RepoPushEvent(RepoVCSEvent):
    """
    An instance of this class is emitted as an :term:`event` after commits
    are pushed to a repo.

    :param extras: (optional) dict of data from proxied VCS actions
    """
    name = 'repo-push'

    def __init__(self, repo_name, pushed_commit_ids, extras):
        super(RepoPushEvent, self).__init__(repo_name, extras)
        self.pushed_commit_ids = pushed_commit_ids

