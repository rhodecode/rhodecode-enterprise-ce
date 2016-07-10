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

import logging
from rhodecode.integrations.registry import IntegrationTypeRegistry
from rhodecode.integrations.types import slack

log = logging.getLogger(__name__)


# TODO: dan: This is currently global until we figure out what to do about
# VCS's not having a pyramid context - move it to pyramid app configuration
# includeme level later to allow per instance integration setup
integration_type_registry = IntegrationTypeRegistry()
integration_type_registry.register_integration_type(slack.SlackIntegrationType)

def integrations_event_handler(event):
    """
    Takes an event and passes it to all enabled integrations
    """
    from rhodecode.model.integration import IntegrationModel

    integration_model = IntegrationModel()
    integrations = integration_model.get_for_event(event)
    for integration in integrations:
        try:
            integration_model.send_event(integration, event)
        except Exception:
            log.exception(
                'failure occured when sending event %s to integration %s' % (
                    event, integration))


def includeme(config):
    config.include('rhodecode.integrations.routes')
