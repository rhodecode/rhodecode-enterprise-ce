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
from pyramid.response import Response
from pyramid.testing import DummyRequest
from rhodecode.lib.middleware.disable_vcs import (
    DisableVCSPagesWrapper, VCSServerUnavailable)


@pytest.mark.parametrize('url, should_raise', [
    ('/', False),
    ('/_admin/settings', False),
    ('/_admin/i_am_fine', False),
    ('/_admin/settings/mappings', True),
    ('/_admin/my_account/repos', True),
    ('/_admin/create_repository', True),
    ('/_admin/gists/1', True),
    ('/_admin/notifications/1', True),
])
def test_vcs_disabled(url, should_raise):
    wrapped_view = DisableVCSPagesWrapper(pyramid_view)
    request = DummyRequest(path=url)

    if should_raise:
        with pytest.raises(VCSServerUnavailable):
            response = wrapped_view(None, request)
    else:
        response = wrapped_view(None, request)
        assert response.status_int == 200

def pyramid_view(context, request):
    """
    A mock pyramid view to be used in the wrapper
    """
    return Response('success')
