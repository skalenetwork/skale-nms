#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
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

import time
from datetime import datetime
from tools.configs import LONG_LINE
import pytest

from bounty import bounty_agent
from sla import sla_agent as sla
from tests.integration.preparation import (
    TEST_DELTA, TEST_EPOCH, TEST_BOUNTY_DELAY, accelerate_skale_manager, create_dirs,
    create_set_of_nodes, get_active_ids, init_skale)
from tools import db
from tools.config_storage import ConfigStorage
from tools.exceptions import GetBountyTxFailedException
from tools.helper import check_node_id

FAKE_IP = '10.1.0.1'
FAKE_REPORT_DATE = 1567690544


def setup_module(module):
    create_dirs()
    accelerate_skale_manager()
    global cur_node_id
    global nodes_count_before, nodes_count_to_add
    ids = get_active_ids()
    print(f'ids = {ids}')
    nodes_count_before = len(ids)
    cur_node_id = max(ids) + 1 if nodes_count_before else 0
    # cur_node_id = 0
    nodes_count_to_add = 2
    create_set_of_nodes(cur_node_id, nodes_count_to_add)
    print('now after nodes creation:')
    print(datetime.utcnow())


@pytest.fixture(scope="module")
def monitor(request):
    print("\nskale setup")
    skale = init_skale(cur_node_id)
    print(f'\ncur_node = {cur_node_id}')
    _monitor = sla.Monitor(skale, cur_node_id)

    return _monitor


@pytest.fixture(scope="module")
def bounty_collector(request):
    print("\nskale setup")
    skale = init_skale(cur_node_id)
    print(f'\ncur_node = {cur_node_id}')
    _bounty_collector = bounty_agent.BountyCollector(skale, cur_node_id)

    return _bounty_collector


def test_nodes_are_created():

    nodes_count_after = len(get_active_ids())
    print(f'\nwait nodes_number = {nodes_count_before + nodes_count_to_add}')
    print(f'got nodes_number = {nodes_count_after}')

    assert nodes_count_after == nodes_count_before + nodes_count_to_add


def test_check_node_id(bounty_collector):
    skale = bounty_collector.skale
    assert check_node_id(skale, 0)
    assert check_node_id(skale, 1)
    assert not check_node_id(skale, 100)


def test_get_validated_nodes(monitor):
    nodes = monitor.get_validated_nodes(monitor.skale)
    print(f'\n Validated nodes = {nodes}')
    assert type(nodes) is list
    assert any(node.get('id') == cur_node_id + 1 for node in nodes)


def test_send_reports_neg(monitor):
    print(f'--- Gas Price = {monitor.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{monitor.skale.web3.eth.getBalance(monitor.skale.wallet.address)}')

    nodes = monitor.get_validated_nodes(monitor.skale)
    reported_nodes = monitor.get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'\nrep nodes = {reported_nodes}')
    assert len(reported_nodes) == 0

    print(LONG_LINE)
    print(f'report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'now: {datetime.utcnow()}')

    fake_nodes = [{'id': 1, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    err_status = monitor.send_reports(fake_nodes)
    assert err_status == 1

    fake_nodes = [{'id': 2, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    err_status = monitor.send_reports(fake_nodes)
    assert err_status == 1


def test_get_bounty_neg(bounty_collector):
    print(f'--- Gas Price = {bounty_collector.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{bounty_collector.skale.web3.eth.getBalance(bounty_collector.skale.wallet.address)}')

    with pytest.raises(GetBountyTxFailedException):
        bounty_collector.get_bounty()


def test_get_reported_nodes_pos(monitor):

    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} sec')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    nodes = monitor.get_validated_nodes(monitor.skale)
    print(LONG_LINE)
    print(f'report date: {datetime.utcfromtimestamp(nodes[0]["rep_date"])}')
    print(f'now: {datetime.utcnow()}')
    reported_nodes = monitor.get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')

    # assert len(reported_nodes) == 1
    # assert reported_nodes[0]['id'] == 1
    assert any(node.get('id') == cur_node_id + 1 for node in reported_nodes)


def test_send_reports_pos(monitor):
    print(f'--- Gas Price = {monitor.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{monitor.skale.web3.eth.getBalance(monitor.skale.wallet.address)}')

    reported_nodes = monitor.get_reported_nodes(monitor.nodes)
    db.clear_all_reports()
    assert monitor.send_reports(reported_nodes) == 0
    # monitor.monitor_job()
    # assert db.get_count_of_report_records() == 1


def test_bounty_job_saves_data(bounty_collector):
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
    print(f'--- Gas Price = {bounty_collector.skale.web3.eth.gasPrice}')
    print(f'ETH balance of account : '
          f'{bounty_collector.skale.web3.eth.getBalance(bounty_collector.skale.wallet.address)}')

    db.clear_all_bounty_receipts()
    skale = bounty_collector.skale
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
