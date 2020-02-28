#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
#
#   Copyright (C) 2019-2020 SKALE Labs
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

import time
from datetime import datetime

import pytest
from skale.utils.web3_utils import TransactionFailedError

from bounty import bounty_agent
from sla import sla_agent as sla
from tests.constants import FAKE_IP, FAKE_REPORT_DATE, N_TEST_NODES
from tests.integration.prepare_validator import (
    TEST_BOUNTY_DELAY, TEST_DELTA, TEST_EPOCH, create_dirs, create_set_of_nodes,
    get_active_ids, init_skale
)
from tools import db
from tools.config_storage import ConfigStorage
from tools.configs import LONG_LINE
from tools.helper import check_node_id

skale = init_skale()


def setup_module(module):
    create_dirs()
    global cur_node_id
    global nodes_count_before, nodes_count_to_add
    ids = get_active_ids(skale)
    print(f'ids = {ids}')
    nodes_count_before = len(ids)
    cur_node_id = max(ids) + 1 if nodes_count_before else 0
    nodes_count_to_add = N_TEST_NODES
    create_set_of_nodes(skale, cur_node_id, nodes_count_to_add)
    print(f'Time just after nodes creation: {datetime.utcnow()}')


@pytest.fixture(scope="module")
def monitor(request):
    print(f'\nInit Monitor for_node ID = {cur_node_id}')
    _monitor = sla.Monitor(skale, cur_node_id)

    return _monitor


@pytest.fixture(scope="module")
def bounty_collector(request):
    print(f'\nInit Bounty collector for_node ID = {cur_node_id}')
    _bounty_collector = bounty_agent.BountyCollector(skale, cur_node_id)

    return _bounty_collector


def test_nodes_are_created():

    nodes_count_after = len(get_active_ids(skale))
    print(f'\nwait nodes_number = {nodes_count_before + nodes_count_to_add}')
    print(f'got nodes_number = {nodes_count_after}')

    assert nodes_count_after == nodes_count_before + nodes_count_to_add


def test_check_node_id():
    assert check_node_id(skale, cur_node_id)
    assert check_node_id(skale, cur_node_id + 1)
    assert not check_node_id(skale, 100)


def test_get_validated_nodes(monitor):
    nodes = monitor.get_validated_nodes(skale)
    print(f'\n Validated nodes = {nodes}')
    assert type(nodes) is list
    assert any(node.get('id') == cur_node_id + 1 for node in nodes)


def test_send_reports_neg(monitor):
    print(f'--- Gas Price = {monitor.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{monitor.skale.web3.eth.getBalance(monitor.skale.wallet.address)}')

    nodes = monitor.get_validated_nodes(skale)
    reported_nodes = monitor.get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'\nrep nodes = {reported_nodes}')
    assert len(reported_nodes) == 0

    print(LONG_LINE)
    print(f'Report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'Now date: {datetime.utcnow()}')

    fake_nodes = [{'id': 1, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    with pytest.raises(TransactionFailedError):
        monitor.send_reports(fake_nodes)

    fake_nodes = [{'id': 2, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    with pytest.raises(TransactionFailedError):
        monitor.send_reports(fake_nodes)


def test_get_bounty_neg(bounty_collector):
    last_block_number = skale.web3.eth.blockNumber
    block_data = skale.web3.eth.getBlock(last_block_number)
    block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
    reward_date = bounty_collector.get_reward_date()
    print(f'Reward date: {reward_date}')
    print(f'Timestamp: {block_timestamp}')

    print(f'--- Gas Price = {bounty_collector.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{bounty_collector.skale.web3.eth.getBalance(bounty_collector.skale.wallet.address)}')

    with pytest.raises(TransactionFailedError):
        bounty_collector.get_bounty()


def test_get_reported_nodes_pos(monitor):

    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} sec')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    nodes = monitor.get_validated_nodes(skale)
    print(LONG_LINE)
    print(f'report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'now: {datetime.utcnow()}')
    reported_nodes = monitor.get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')

    assert any(node.get('id') == cur_node_id + 1 for node in reported_nodes)


def test_send_reports_pos(monitor):
    print(f'--- Gas Price = {monitor.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{monitor.skale.web3.eth.getBalance(skale.wallet.address)}')

    reported_nodes = monitor.get_reported_nodes(monitor.nodes)
    db.clear_all_reports()
    assert monitor.send_reports(reported_nodes) == 0
    # monitor.monitor_job()
    # assert db.get_count_of_report_records() == 1


def test_bounty_job_saves_data(bounty_collector):
    last_block_number = skale.web3.eth.blockNumber
    block_data = skale.web3.eth.getBlock(last_block_number)
    block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
    reward_date = bounty_collector.get_reward_date()
    print(f'Reward date: {reward_date}')
    print(f'Timestamp: {block_timestamp}')

    print(f'--- Gas Price = {bounty_collector.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{bounty_collector.skale.web3.eth.getBalance(bounty_collector.skale.wallet.address)}')

    print(f'\nSleep for {TEST_DELTA} sec')
    time.sleep(TEST_DELTA + TEST_BOUNTY_DELAY)  # plus delay to wait next block after end of epoch
    db.clear_all_bounty_receipts()
    bounty_collector.job()
    assert db.get_count_of_bounty_receipt_records() == 1


@pytest.mark.skip(reason="skip to save time")
def test_get_bounty_pos(bounty_collector):
    print(f'--- Gas Price = {bounty_collector.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{bounty_collector.skale.web3.eth.getBalance(bounty_collector.skale.wallet.address)}')

    print(f'\nSleep for {TEST_EPOCH} sec')
    time.sleep(TEST_EPOCH)
    db.clear_all_bounty_receipts()
    status = bounty_collector.get_bounty()
    assert status == 1
    assert db.get_count_of_bounty_receipt_records() == 1


def test_get_bounty_second_time(bounty_collector):
    last_block_number = skale.web3.eth.blockNumber
    block_data = skale.web3.eth.getBlock(last_block_number)
    block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
    reward_date = bounty_collector.get_reward_date()
    print(f'Reward date: {reward_date}')
    print(f'Timestamp: {block_timestamp}')

    print(f'--- Gas Price = {bounty_collector.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{bounty_collector.skale.web3.eth.getBalance(bounty_collector.skale.wallet.address)}')

    db.clear_all_bounty_receipts()
    bounty_collector2 = bounty_agent.BountyCollector(skale, cur_node_id)
    print(f'\nSleep for {TEST_EPOCH} sec')
    time.sleep(TEST_EPOCH + TEST_BOUNTY_DELAY)  # plus delay to wait next block after end of epoch
    bounty_collector2.job()
    assert db.get_count_of_bounty_receipt_records() == 1


def test_get_id_from_config(monitor):
    config_file_name = 'test_node_config'
    node_index = 1
    config_node = ConfigStorage(config_file_name)
    config_node.update({'node_id': node_index})
    node_id = monitor.get_id_from_config(config_file_name)
    assert node_id == node_index
