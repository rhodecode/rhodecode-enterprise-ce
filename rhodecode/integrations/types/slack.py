# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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

from __future__ import unicode_literals

import re
import logging
import requests
import colander
from celery.task import task
from mako.template import Template

from rhodecode import events
from rhodecode.translation import lazy_ugettext
from rhodecode.lib import helpers as h
from rhodecode.lib.celerylib import run_task
from rhodecode.lib.colander_utils import strip_whitespace
from rhodecode.integrations.types.base import IntegrationTypeBase
from rhodecode.integrations.schema import IntegrationSettingsSchemaBase

log = logging.getLogger()


class SlackSettingsSchema(IntegrationSettingsSchemaBase):
    service = colander.SchemaNode(
        colander.String(),
        title=lazy_ugettext('Slack service URL'),
        description=h.literal(lazy_ugettext(
            'This can be setup at the '
            '<a href="https://my.slack.com/services/new/incoming-webhook/">'
            'slack app manager</a>')),
        default='',
        placeholder='https://hooks.slack.com/services/...',
        preparer=strip_whitespace,
        validator=colander.url,
        widget='string'
    )
    username = colander.SchemaNode(
        colander.String(),
        title=lazy_ugettext('Username'),
        description=lazy_ugettext('Username to show notifications coming from.'),
        missing='Rhodecode',
        preparer=strip_whitespace,
        widget='string',
        placeholder='Rhodecode'
    )
    channel = colander.SchemaNode(
        colander.String(),
        title=lazy_ugettext('Channel'),
        description=lazy_ugettext('Channel to send notifications to.'),
        missing='',
        preparer=strip_whitespace,
        widget='string',
        placeholder='#general'
    )
    icon_emoji = colander.SchemaNode(
        colander.String(),
        title=lazy_ugettext('Emoji'),
        description=lazy_ugettext('Emoji to use eg. :studio_microphone:'),
        missing='',
        preparer=strip_whitespace,
        widget='string',
        placeholder=':studio_microphone:'
    )


repo_push_template = Template(r'''
*${data['actor']['username']}* pushed to \
%if data['push']['branches']:
${len(data['push']['branches']) > 1 and 'branches' or 'branch'} \
${', '.join('<%s|%s>' % (branch['url'], branch['name']) for branch in data['push']['branches'])} \
%else:
unknown branch \
%endif
in <${data['repo']['url']}|${data['repo']['repo_name']}>
>>>
%for commit in data['push']['commits']:
<${commit['url']}|${commit['short_id']}> - ${commit['message_html']|html_to_slack_links}
%endfor
''')


class SlackIntegrationType(IntegrationTypeBase):
    key = 'slack'
    display_name = lazy_ugettext('Slack')
    SettingsSchema = SlackSettingsSchema
    valid_events = [
        events.PullRequestCloseEvent,
        events.PullRequestMergeEvent,
        events.PullRequestUpdateEvent,
        events.PullRequestReviewEvent,
        events.PullRequestCreateEvent,
        events.RepoPushEvent,
        events.RepoCreateEvent,
    ]

    def send_event(self, event):
        if event.__class__ not in self.valid_events:
            log.debug('event not valid: %r' % event)
            return

        if event.name not in self.settings['events']:
            log.debug('event ignored: %r' % event)
            return

        data = event.as_dict()

        text = '*%s* caused a *%s* event' % (
            data['actor']['username'], event.name)

        log.debug('handling slack event for %s' % event.name)

        if isinstance(event, events.PullRequestEvent):
            text = self.format_pull_request_event(event, data)
        elif isinstance(event, events.RepoPushEvent):
            text = self.format_repo_push_event(data)
        elif isinstance(event, events.RepoCreateEvent):
            text = self.format_repo_create_event(data)
        else:
            log.error('unhandled event type: %r' % event)

        run_task(post_text_to_slack, self.settings, text)

    @classmethod
    def settings_schema(cls):
        schema = SlackSettingsSchema()
        schema.add(colander.SchemaNode(
            colander.Set(),
            widget='checkbox_list',
            choices=sorted([e.name for e in cls.valid_events]),
            description="Events activated for this integration",
            default=[e.name for e in cls.valid_events],
            name='events'
        ))
        return schema

    def format_pull_request_event(self, event, data):
        action = {
            events.PullRequestCloseEvent: 'closed',
            events.PullRequestMergeEvent: 'merged',
            events.PullRequestUpdateEvent: 'updated',
            events.PullRequestReviewEvent: 'reviewed',
            events.PullRequestCreateEvent: 'created',
        }.get(event.__class__, '<unknown action>')

        return ('Pull request <{url}|#{number}> ({title}) '
                '{action} by {user}').format(
            user=data['actor']['username'],
            number=data['pullrequest']['pull_request_id'],
            url=data['pullrequest']['url'],
            title=data['pullrequest']['title'],
            action=action
        )

    def format_repo_push_event(self, data):
        result = repo_push_template.render(
            data=data,
            html_to_slack_links=html_to_slack_links,
        )
        return result

    def format_repo_create_msg(self, data):
        return '<{}|{}> ({}) repository created by *{}*'.format(
            data['repo']['url'],
            data['repo']['repo_name'],
            data['repo']['repo_type'],
            data['actor']['username'],
        )


def html_to_slack_links(message):
    return re.compile(r'<a .*?href=["\'](.+?)".*?>(.+?)</a>').sub(
        r'<\1|\2>', message)


@task(ignore_result=True)
def post_text_to_slack(settings, text):
    log.debug('sending %s to slack %s' % (text, settings['service']))
    resp = requests.post(settings['service'], json={
        "channel": settings.get('channel', ''),
        "username": settings.get('username', 'Rhodecode'),
        "text": text,
        "icon_emoji": settings.get('icon_emoji', ':studio_microphone:')
    })
    resp.raise_for_status()  # raise exception on a failed request
