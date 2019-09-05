#   -*- coding: utf-8 -*-
#
#   This file is part of SLA
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import time
from datetime import datetime

import pytest
from skale.utils.helper import await_receipt, private_key_to_address

from sla import sla_agent as sla
from tests.integration import preparation
from tools.helper import init_skale

TEST_EPOCH = 200
TEST_DELTA = 100


def setup_module(module):
    global cur_node_id
    cur_node_id = 0
#     global nodes_count_before, nodes_count_to_add
#     ids = preparation.get_active_ids()
#     print(f'ids = {ids}')
#     nodes_count_before = len(ids)
#     max_id = max(ids) if len(ids) else -1
#     print(f'max_id = {max_id}')
#     print(f'nodes count before = {nodes_count_before}')
#     nodes_count_to_add = 2
#     preparation.create_set_of_nodes(max_id + 1, nodes_count_to_add)


@pytest.fixture(scope="module")
def monitor(request):
    print("\nskale setup")
    skale = init_skale()
    accelerate_skale_manager(skale)
    print(f'\ncur_node = {cur_node_id}')
    _monitor = sla.Monitor(skale, cur_node_id)

    return _monitor


def accelerate_skale_manager(skale):
    pr_key = os.environ.get('ETH_PRIVATE_KEY')
    account = skale.web3.toChecksumAddress(private_key_to_address(pr_key))

    reward_period = skale.validators_data.get_reward_period()
    delta_period = skale.validators_data.get_delta_period()
    print(reward_period, delta_period)

    wallet = {'address': account, 'private_key': pr_key}
    res = skale.constants.set_periods(TEST_EPOCH, TEST_DELTA, wallet)
    receipt = await_receipt(skale.web3, res['tx'], retries=30, timeout=6)
    print(receipt)
    print("-------------------------")
    reward_period = skale.validators_data.get_reward_period()
    delta_period = skale.validators_data.get_delta_period()
    print(reward_period, delta_period)


# def test_nodes_are_created():
#
#     nodes_count_after = len(preparation.get_active_ids())
#     print(f'\nwait nodes_number = {nodes_count_before + nodes_count_to_add}')
#     print(f'got nodes_number = {nodes_count_after}')
#
#     assert nodes_count_after == nodes_count_before + nodes_count_to_add


def test_get_validated_nodes(monitor):
    # skale = init_skale()

    nodes = monitor.get_validated_nodes()
    print(f'nodes = {nodes}')
    assert type(nodes) is list
    assert any(node.get('id') == cur_node_id + 1 for node in nodes)


def test_validate_and_get_reported_nodes_neg(monitor):

    nodes = monitor.get_validated_nodes()
    reported_nodes = monitor.validate_and_get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')
    assert len(reported_nodes) == 0

    fake_nodes = [{'id': 1, 'ip': '10.1.0.1', 'rep_date': 1567690544}]
    err_send_verdicts_count = monitor.send_reports(fake_nodes)
    assert err_send_verdicts_count == 1

    fake_nodes = [{'id': 2, 'ip': '10.1.0.1', 'rep_date': 1567690544}]
    err_send_verdicts_count = monitor.send_reports(fake_nodes)
    assert err_send_verdicts_count == 1


def test_validate_and_get_reported_nodes_pos(monitor):
    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} min')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    nodes = monitor.get_validated_nodes()
    reported_nodes = monitor.validate_and_get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')

    # assert len(reported_nodes) == 1
    assert reported_nodes[0]['id'] == 1

    err_send_verdicts_count = monitor.send_reports(reported_nodes)
    assert err_send_verdicts_count == 0
