# -*- coding: utf-8 -*-

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

import colander
import pytest

from rhodecode.model.validation_schema import GroupNameType


class TestGroupNameType(object):
    @pytest.mark.parametrize('given, expected', [
        ('//group1/group2//', 'group1/group2'),
        ('//group1///group2//', 'group1/group2'),
        ('group1/group2///group3', 'group1/group2/group3')
    ])
    def test_replace_extra_slashes_cleans_up_extra_slashes(
            self, given, expected):
        type_ = GroupNameType()
        result = type_._replace_extra_slashes(given)
        assert result == expected

    def test_deserialize_cleans_up_extra_slashes(self):
        class TestSchema(colander.Schema):
            field = colander.SchemaNode(GroupNameType())

        schema = TestSchema()
        cleaned_data = schema.deserialize(
            {'field': '//group1/group2///group3//'})
        assert cleaned_data['field'] == 'group1/group2/group3'
