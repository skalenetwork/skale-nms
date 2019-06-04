#   -*- coding: utf-8 -*-
#
#   This file is part of SLA
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sla import sla_agent as sla
from tests import preparation
from tools.helper import init_skale


def setup_module(module):
    global nodes_count_before, nodes_count_to_add
    ids = preparation.get_active_ids()
    print(f'ids = {ids}')
    nodes_count_before = len(ids)
    max_id = max(ids) if len(ids) else -1
    print(f'max_id = {max_id}')
    print(f'nodes count before = {nodes_count_before}')
    nodes_count_to_add = 2
    preparation.create_set_of_nodes(max_id + 1, nodes_count_to_add)


def test_nodes_are_created():

    nodes_count_after = len(preparation.get_active_ids())
    print(f'wait nodes_number = {nodes_count_before + nodes_count_to_add}')
    print(f'got nodes_number = {nodes_count_after}')

    assert nodes_count_after == nodes_count_before + nodes_count_to_add


def test_get_validated_nodes():
    skale = init_skale()
    cur_nodes_count = nodes_count_before + nodes_count_to_add
    cur_node_id = cur_nodes_count - 2
    print(f'cur_node = {cur_node_id}')
    monitor = sla.Monitor(skale, cur_node_id)
    nodes = monitor.get_validated_nodes()
    print(f'nodes = {nodes}')
    assert type(nodes) is list
    assert any(node.get('id') == cur_nodes_count - 1 for node in nodes)
