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

import pytest
import requests
from mock import Mock, patch

from rhodecode import events
from rhodecode.model.db import Session, Integration
from rhodecode.model.integration import IntegrationModel
from rhodecode.integrations.types.base import IntegrationTypeBase


class TestIntegrationType(IntegrationTypeBase):
    """ Test integration type class """

    key = 'test-integration'
    display_name = 'Test integration type'

    def __init__(self, settings):
        super(IntegrationTypeBase, self).__init__(settings)
        self.sent_events = [] # for testing

    def send_event(self, event):
        self.sent_events.append(event)


@pytest.fixture
def repo_integration_stub(request, repo_stub):
    settings = {'test_key': 'test_value'}
    integration = IntegrationModel().create(
        TestIntegrationType, settings=settings, repo=repo_stub, enabled=True,
        name='test repo integration')

    @request.addfinalizer
    def cleanup():
        IntegrationModel().delete(integration)

    return integration


@pytest.fixture
def global_integration_stub(request):
    settings = {'test_key': 'test_value'}
    integration = IntegrationModel().create(
        TestIntegrationType, settings=settings, enabled=True,
        name='test global integration')

    @request.addfinalizer
    def cleanup():
        IntegrationModel().delete(integration)

    return integration


def test_delete_repo_with_integration_deletes_integration(repo_integration_stub):
    Session().delete(repo_integration_stub.repo)
    Session().commit()
    Session().expire_all()
    assert Integration.get(repo_integration_stub.integration_id) is None

