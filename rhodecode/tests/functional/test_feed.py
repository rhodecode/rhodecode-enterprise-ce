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

from rhodecode.model.db import User
from rhodecode.tests import *


class TestFeedController(TestController):

    def test_rss(self, backend):
        self.log_user()
        response = self.app.get(url(controller='feed', action='rss',
                                    repo_name=backend.repo_name))

        assert response.content_type == "application/rss+xml"
        assert """<rss version="2.0">""" in response

    def test_rss_with_auth_token(self, backend):
        auth_token = User.get_first_admin().feed_token
        assert auth_token != ''
        response = self.app.get(url(controller='feed', action='rss',
                                    repo_name=backend.repo_name, auth_token=auth_token))

        assert response.content_type == "application/rss+xml"
        assert """<rss version="2.0">""" in response

    def test_atom(self, backend):
        self.log_user()
        response = self.app.get(url(controller='feed', action='atom',
                                    repo_name=backend.repo_name))

        assert response.content_type == """application/atom+xml"""
        assert """<?xml version="1.0" encoding="utf-8"?>""" in response

        tag1 = '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en-us">'
        tag2 = '<feed xml:lang="en-us" xmlns="http://www.w3.org/2005/Atom">'
        assert tag1 in response or tag2 in response
