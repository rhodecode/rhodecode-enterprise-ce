# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016  RhodeCode GmbH
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
Model for integrations
"""


import logging
import traceback

from pylons import tmpl_context as c
from pylons.i18n.translation import _, ungettext
from sqlalchemy import or_
from sqlalchemy.sql.expression import false, true
from mako import exceptions

import rhodecode
from rhodecode import events
from rhodecode.lib import helpers as h
from rhodecode.lib.caching_query import FromCache
from rhodecode.lib.utils import PartialRenderer
from rhodecode.model import BaseModel
from rhodecode.model.db import Integration, User
from rhodecode.model.meta import Session
from rhodecode.integrations import integration_type_registry

log = logging.getLogger(__name__)


class IntegrationModel(BaseModel):

    cls = Integration

    def __get_integration(self, integration):
        if isinstance(integration, Integration):
            return integration
        elif isinstance(integration, (int, long)):
            return self.sa.query(Integration).get(integration)
        else:
            if integration:
                raise Exception('integration must be int, long or Instance'
                                ' of Integration got %s' % type(integration))

    def delete(self, integration):
        try:
            integration = self.__get_integration(integration)
            if integration:
                Session().delete(integration)
                return True
        except Exception:
            log.error(traceback.format_exc())
            raise
        return False

    def get_integration_handler(self, integration):
        TypeClass = integration_type_registry.get(integration.integration_type)
        if not TypeClass:
            log.error('No class could be found for integration type: {}'.format(
                integration.integration_type))
            return None

        return TypeClass(integration.settings)

    def send_event(self, integration, event):
        """ Send an event to an integration """
        handler = self.get_integration_handler(integration)
        if handler:
            handler.send_event(event)

    def get_integrations(self, repo=None):
        if repo:
            return self.sa.query(Integration).filter(
                Integration.repo_id==repo.repo_id).all()

        # global integrations
        return self.sa.query(Integration).filter(
            Integration.repo_id==None).all()

    def get_for_event(self, event, cache=False):
        """
        Get integrations that match an event
        """
        query = self.sa.query(Integration).filter(Integration.enabled==True)

        if isinstance(event, events.RepoEvent): # global + repo integrations
            query = query.filter(
                        or_(Integration.repo_id==None,
                            Integration.repo_id==event.repo.repo_id))
            if cache:
                query = query.options(FromCache(
                    "sql_cache_short",
                    "get_enabled_repo_integrations_%i" % event.repo.repo_id))
        else: # only global integrations
            query = query.filter(Integration.repo_id==None)
            if cache:
                query = query.options(FromCache(
                    "sql_cache_short", "get_enabled_global_integrations"))

        return query.all()
