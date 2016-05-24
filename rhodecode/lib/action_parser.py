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

import logging

from pylons import url
from pylons.i18n.translation import _
from webhelpers.html.builder import literal
from webhelpers.html.tags import link_to

from rhodecode.lib.utils2 import AttributeDict
from rhodecode.lib.vcs.backends.base import BaseCommit
from rhodecode.lib.vcs.exceptions import CommitDoesNotExistError


log = logging.getLogger(__name__)


def action_parser(user_log, feed=False, parse_cs=False):
    """
    This helper will action_map the specified string action into translated
    fancy names with icons and links

    :param user_log: user log instance
    :param feed: use output for feeds (no html and fancy icons)
    :param parse_cs: parse Changesets into VCS instances
    """
    ap = ActionParser(user_log, feed=False, parse_commits=False)
    return ap.callbacks()


class ActionParser(object):

    commits_limit = 3  # display this amount always
    commits_top_limit = 50  # show up to this amount of commits hidden

    def __init__(self, user_log, feed=False, parse_commits=False):
        self.user_log = user_log
        self.feed = feed
        self.parse_commits = parse_commits

        self.action = user_log.action
        self.action_params = ' '
        x = self.action.split(':', 1)
        if len(x) > 1:
            self.action, self.action_params = x

    def callbacks(self):
        action_str = self.action_map.get(self.action, self.action)
        if self.feed:
            action = action_str[0].replace('[', '').replace(']', '')
        else:
            action = action_str[0]\
                .replace('[', '<span class="journal_highlight">')\
                .replace(']', '</span>')

        action_params_func = _no_params_func
        if callable(action_str[1]):
            action_params_func = action_str[1]

        # returned callbacks we need to call to get
        return [
            lambda: literal(action), action_params_func,
            self.action_parser_icon]

    @property
    def action_map(self):

        # action : translated str, callback(extractor), icon
        action_map = {
            'user_deleted_repo': (
                _('[deleted] repository'),
                None, 'icon-trash'),
            'user_created_repo': (
                _('[created] repository'),
                None, 'icon-plus icon-plus-colored'),
            'user_created_fork': (
                _('[created] repository as fork'),
                None, 'icon-code-fork'),
            'user_forked_repo': (
                _('[forked] repository'),
                self.get_fork_name, 'icon-code-fork'),
            'user_updated_repo': (
                _('[updated] repository'),
                None, 'icon-pencil icon-pencil-colored'),
            'user_downloaded_archive': (
                _('[downloaded] archive from repository'),
                self.get_archive_name, 'icon-download-alt'),
            'admin_deleted_repo': (
                _('[delete] repository'),
                None, 'icon-trash'),
            'admin_created_repo': (
                _('[created] repository'),
                None, 'icon-plus icon-plus-colored'),
            'admin_forked_repo': (
                _('[forked] repository'),
                None, 'icon-code-fork icon-fork-colored'),
            'admin_updated_repo': (
                _('[updated] repository'),
                None, 'icon-pencil icon-pencil-colored'),
            'admin_created_user': (
                _('[created] user'),
                self.get_user_name, 'icon-user icon-user-colored'),
            'admin_updated_user': (
                _('[updated] user'),
                self.get_user_name, 'icon-user icon-user-colored'),
            'admin_created_users_group': (
                _('[created] user group'),
                self.get_users_group, 'icon-pencil icon-pencil-colored'),
            'admin_updated_users_group': (
                _('[updated] user group'),
                self.get_users_group, 'icon-pencil icon-pencil-colored'),
            'user_commented_revision': (
                _('[commented] on commit in repository'),
                self.get_cs_links, 'icon-comment icon-comment-colored'),
            'user_commented_pull_request': (
                _('[commented] on pull request for'),
                self.get_pull_request, 'icon-comment icon-comment-colored'),
            'user_closed_pull_request': (
                _('[closed] pull request for'),
                self.get_pull_request, 'icon-check'),
            'user_merged_pull_request': (
                _('[merged] pull request for'),
                self.get_pull_request, 'icon-check'),
            'push': (
                _('[pushed] into'),
                self.get_cs_links, 'icon-arrow-up'),
            'push_local': (
                _('[committed via RhodeCode] into repository'),
                self.get_cs_links, 'icon-pencil icon-pencil-colored'),
            'push_remote': (
                _('[pulled from remote] into repository'),
                self.get_cs_links, 'icon-arrow-up'),
            'pull': (
                _('[pulled] from'),
                None, 'icon-arrow-down'),
            'started_following_repo': (
                _('[started following] repository'),
                None, 'icon-heart icon-heart-colored'),
            'stopped_following_repo': (
                _('[stopped following] repository'),
                None, 'icon-heart-empty icon-heart-colored'),
        }
        return action_map

    def get_fork_name(self):
        repo_name = self.action_params
        _url = url('summary_home', repo_name=repo_name)
        return _('fork name %s') % link_to(self.action_params, _url)

    def get_user_name(self):
        user_name = self.action_params
        return user_name

    def get_users_group(self):
        group_name = self.action_params
        return group_name

    def get_pull_request(self):
        pull_request_id = self.action_params
        if self.is_deleted():
            repo_name = self.user_log.repository_name
        else:
            repo_name = self.user_log.repository.repo_name
        return link_to(
            _('Pull request #%s') % pull_request_id,
            url('pullrequest_show', repo_name=repo_name,
                pull_request_id=pull_request_id))

    def get_archive_name(self):
        archive_name = self.action_params
        return archive_name

    def action_parser_icon(self):
        tmpl = """<i class="%s" alt="%s"></i>"""
        ico = self.action_map.get(self.action, ['', '', ''])[2]
        return literal(tmpl % (ico, self.action))

    def get_cs_links(self):
        if self.is_deleted():
            return self.action_params

        repo_name = self.user_log.repository.repo_name
        commit_ids = self.action_params.split(',')
        commits = self.get_commits(commit_ids)

        link_generator = (
            self.lnk(commit, repo_name)
            for commit in commits[:self.commits_limit])
        commit_links = [" " + ', '.join(link_generator)]
        _op1, _name1 = _get_op(commit_ids[0])
        _op2, _name2 = _get_op(commit_ids[-1])

        commit_id_range = '%s...%s' % (_name1, _name2)

        compare_view = (
            ' <div class="compare_view tooltip" title="%s">'
            '<a href="%s">%s</a> </div>' % (
                _('Show all combined commits %s->%s') % (
                    commit_ids[0][:12], commit_ids[-1][:12]
                ),
                url('changeset_home', repo_name=repo_name,
                    revision=commit_id_range), _('compare view')
            )
        )

        if len(commit_ids) > self.commits_limit:
            more_count = len(commit_ids) - self.commits_limit
            commit_links.append(
                _(' and %(num)s more commits') % {'num': more_count}
            )

        if len(commits) > 1:
            commit_links.append(compare_view)
        return ''.join(commit_links)

    def get_commits(self, commit_ids):
        commits = []
        if not filter(lambda v: v != '', commit_ids):
            return commits

        repo = None
        if self.parse_commits:
            repo = self.user_log.repository.scm_instance()

        for commit_id in commit_ids[:self.commits_top_limit]:
            _op, _name = _get_op(commit_id)

            # we want parsed commits, or new log store format is bad
            if self.parse_commits:
                try:
                    commit = repo.get_commit(commit_id=commit_id)
                    commits.append(commit)
                except CommitDoesNotExistError:
                    log.error(
                        'cannot find commit id %s in this repository',
                        commit_id)
                    commits.append(commit_id)
                    continue
            else:
                fake_commit = AttributeDict({
                    'short_id': commit_id[:12],
                    'raw_id': commit_id,
                    'message': '',
                    'op': _op,
                    'ref_name': _name
                })
                commits.append(fake_commit)

        return commits

    def lnk(self, commit_or_id, repo_name):
        from rhodecode.lib.helpers import tooltip

        if isinstance(commit_or_id, (BaseCommit, AttributeDict)):
            lazy_cs = True
            if (getattr(commit_or_id, 'op', None) and
                    getattr(commit_or_id, 'ref_name', None)):
                lazy_cs = False
                lbl = '?'
                if commit_or_id.op == 'delete_branch':
                    lbl = '%s' % _('Deleted branch: %s') % commit_or_id.ref_name
                    title = ''
                elif commit_or_id.op == 'tag':
                    lbl = '%s' % _('Created tag: %s') % commit_or_id.ref_name
                    title = ''
                _url = '#'

            else:
                lbl = '%s' % (commit_or_id.short_id[:8])
                _url = url('changeset_home', repo_name=repo_name,
                           revision=commit_or_id.raw_id)
                title = tooltip(commit_or_id.message)
        else:
            # commit cannot be found/striped/removed etc.
            lbl = ('%s' % commit_or_id)[:12]
            _url = '#'
            title = _('Commit not found')
        if self.parse_commits:
            return link_to(lbl, _url, title=title, class_='tooltip')
        return link_to(lbl, _url, raw_id=commit_or_id.raw_id, repo_name=repo_name,
                       class_='lazy-cs' if lazy_cs else '')

    def is_deleted(self):
        return self.user_log.repository is None


def _no_params_func():
    return ""


def _get_op(commit_id):
    _op = None
    _name = commit_id
    if len(commit_id.split('=>')) == 2:
        _op, _name = commit_id.split('=>')
    return _op, _name
