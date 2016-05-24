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

from rhodecode.lib import graphmod


# pylint: disable=protected-access


def test_get_edge_color_multiple_parents():
    node_color = 1
    parent_color = 2
    assert graphmod._get_edge_color(
        'parent', 2, node_color, {'parent': parent_color}) == parent_color


def test_get_edge_color_multiple_unknown_parent():
    node_color = 1
    assert graphmod._get_edge_color('parent', 2, node_color, {}) == node_color


def test_get_edge_color_single_parent():
    node_color = 1
    assert graphmod._get_edge_color('parent', 1, node_color, {}) == node_color


def test_colored_linear():
    dag = [('node3', ['node2']), ('node2', ['node1']), ('node1', [])]
    expected_result = [
        ((0, 1), [(0, 0, 1)]),
        ((0, 1), [(0, 0, 1)]),
        ((0, 1), []),
    ]
    assert list(graphmod._colored(dag)) == expected_result


def test_colored_diverging_branch():
    dag = [('node3', ['node1']), ('node2', ['node1']), ('node1', [])]
    expected_result = [
        ((0, 1), [(0, 0, 1)]),
        ((1, 2), [(0, 0, 1), (1, 0, 2)]),
        ((0, 1), []),
    ]
    assert list(graphmod._colored(dag)) == expected_result


def test_colored_merged_branch():
    dag = [
        ('node4', ['node2', 'node3']),
        ('node3', ['node1']),
        ('node2', ['node1']),
        ('node1', []),
    ]
    expected_result = [
        ((0, 1), [(0, 0, 1), (0, 1, 2)]),
        ((1, 2), [(0, 0, 1), (1, 1, 2)]),
        ((0, 1), [(0, 0, 1), (1, 0, 2)]),
        ((0, 2), []),
    ]
    assert list(graphmod._colored(dag)) == expected_result
