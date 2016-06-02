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
from colander import Invalid  # noqa


class GroupNameType(colander.String):
    SEPARATOR = '/'

    def deserialize(self, node, cstruct):
        result = super(GroupNameType, self).deserialize(node, cstruct)
        return self._replace_extra_slashes(result)

    def _replace_extra_slashes(self, path):
        path = path.split(self.SEPARATOR)
        path = [item for item in path if item]
        return self.SEPARATOR.join(path)


class RepoGroupSchema(colander.Schema):
    group_name = colander.SchemaNode(GroupNameType())


class RepoSchema(colander.Schema):
    repo_name = colander.SchemaNode(GroupNameType())


class SearchParamsSchema(colander.MappingSchema):
    search_query = colander.SchemaNode(
        colander.String(),
        missing='')
    search_type = colander.SchemaNode(
        colander.String(),
        missing='content',
        validator=colander.OneOf(['content', 'path', 'commit', 'repository']))
    search_sort = colander.SchemaNode(
        colander.String(),
        missing='newfirst',
        validator=colander.OneOf(
            ['oldfirst', 'newfirst']))
    page_limit = colander.SchemaNode(
        colander.Integer(),
        missing=10,
        validator=colander.Range(1, 500))
    requested_page = colander.SchemaNode(
        colander.Integer(),
        missing=1)

