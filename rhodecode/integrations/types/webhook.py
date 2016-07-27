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

import logging
import requests
import colander
from celery.task import task
from mako.template import Template

from rhodecode import events
from rhodecode.translation import lazy_ugettext
from rhodecode.integrations.types.base import IntegrationTypeBase
from rhodecode.integrations.schema import IntegrationSettingsSchemaBase

log = logging.getLogger(__name__)


class WebhookSettingsSchema(IntegrationSettingsSchemaBase):
    url = colander.SchemaNode(
        colander.String(),
        title=lazy_ugettext('Webhook URL'),
        description=lazy_ugettext('URL of the webhook to receive POST event.'),
        default='',
        validator=colander.url,
        placeholder='https://www.example.com/webhook',
        widget='string'
    )
    secret_token = colander.SchemaNode(
        colander.String(),
        title=lazy_ugettext('Secret Token'),
        description=lazy_ugettext('String used to validate received payloads.'),
        default='',
        placeholder='secret_token',
        widget='string'
    )


class WebhookIntegrationType(IntegrationTypeBase):
    key = 'webhook'
    display_name = lazy_ugettext('Webhook')
    valid_events = [
        events.PullRequestCloseEvent,
        events.PullRequestMergeEvent,
        events.PullRequestUpdateEvent,
        events.PullRequestCommentEvent,
        events.PullRequestReviewEvent,
        events.PullRequestCreateEvent,
        events.RepoPushEvent,
        events.RepoCreateEvent,
    ]

    @classmethod
    def settings_schema(cls):
        schema = WebhookSettingsSchema()
        schema.add(colander.SchemaNode(
            colander.Set(),
            widget='checkbox_list',
            choices=sorted([e.name for e in cls.valid_events]),
            description="Events activated for this integration",
            name='events'
        ))
        return schema

    def send_event(self, event):
        log.debug('handling event %s with webhook integration %s',
            event.name, self)

        if event.__class__ not in self.valid_events:
            log.debug('event not valid: %r' % event)
            return

        if event.name not in self.settings['events']:
            log.debug('event ignored: %r' % event)
            return

        data = event.as_dict()
        post_to_webhook(data, self.settings)


@task(ignore_result=True)
def post_to_webhook(data, settings):
    log.debug('sending event:%s to webhook %s', data['name'], settings['url'])
    resp = requests.post(settings['url'], json={
        'token': settings['secret_token'],
        'event': data
    })
    resp.raise_for_status()  # raise exception on a failed request
