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

from rhodecode.api.views import depracated_api
from rhodecode.lib.ext_json import json
from rhodecode.api.tests.utils import (
    build_data, api_call)


@pytest.mark.usefixtures("testuser_api", "app")
class TestCommitComment(object):
    def test_deprecated_message_in_docstring(self):
        docstring = depracated_api.changeset_comment.__doc__
        assert '.. deprecated:: 3.4.0' in docstring
        assert 'Please use method `comment_commit` instead.' in docstring

    def test_deprecated_message_in_retvalue(self):

        id_, params = build_data(
            self.apikey, 'show_ip')
        response = api_call(self.app, params)

        expected = {
            'id': id_,
            'error': None,
            'result': json.loads(response.body)['result'],
            'DEPRECATION_WARNING':
                'DEPRECATED METHOD Please use method `get_ip` instead.'
        }
        assert expected == json.loads(response.body)

    # def test_calls_comment_commit(self, backend, no_notifications):
    #     data = {
    #         'repoid': backend.repo_name,
    #         'status': ChangesetStatus.STATUS_APPROVED,
    #         'message': 'Approved',
    #         'revision': 'tip'
    #     }
    #     with patch.object(repo_api, 'changeset_commit') as comment_mock:
    #         id_, params = build_data(self.apikey, 'comment_commit', **data)
    #         api_call(self.app, params)
    #
    #     _, call_args = comment_mock.call_args
    #     data['commit_id'] = data.pop('revision')
    #     for key in data:
    #         assert call_args[key] == data[key]

    # def test_warning_log_contains_deprecation_message(self):
    #     api = self.SampleApi()
    #     with patch.object(utils, 'log') as log_mock:
    #         api.api_method()
    #
    #     assert log_mock.warning.call_count == 1
    #     call_args = log_mock.warning.call_args[0]
    #     assert (
    #         call_args[0] ==
    #         'DEPRECATED API CALL on function %s, please use `%s` instead')
    #     assert call_args[1].__name__ == 'api_method'
    #     assert call_args[2] == 'new_method'