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

import pytest

from bounty import bounty_agent
from sla import sla_agent as sla
from tests.integration.preparation import (TEST_DELTA, TEST_EPOCH, accelerate_skale_manager,
                                           create_set_of_nodes, get_active_ids, create_dirs)
from tools import db
from tools.config_storage import ConfigStorage
from tools.helper import init_skale

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
    skale = init_skale()
    print(f'\ncur_node = {cur_node_id}')
    _monitor = sla.Monitor(skale, cur_node_id)

    return _monitor


@pytest.fixture(scope="module")
def bounty_collector(request):
    print("\nskale setup")
    skale = init_skale()
    print(f'\ncur_node = {cur_node_id}')
    _bounty_collector = bounty_agent.BountyCollector(skale, cur_node_id)

    return _bounty_collector


def test_nodes_are_created():

    nodes_count_after = len(get_active_ids())
    print(f'\nwait nodes_number = {nodes_count_before + nodes_count_to_add}')
    print(f'got nodes_number = {nodes_count_after}')

    assert nodes_count_after == nodes_count_before + nodes_count_to_add


def test_get_validated_nodes(monitor):
    # skale = init_skale()

    nodes = monitor.get_validated_nodes()
    print(f'nodes = {nodes}')
    assert type(nodes) is list
    assert any(node.get('id') == cur_node_id + 1 for node in nodes)


def test_get_reported_nodes_neg(monitor):

    nodes = monitor.get_validated_nodes()
    reported_nodes = monitor.get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')
    assert len(reported_nodes) == 0

    print('\n+++++++++++++++++++++++++++++')
    print('report date:')
    print(datetime.utcfromtimestamp(nodes[0]['rep_date']))
    print('now:')
    print(datetime.utcnow())

    fake_nodes = [{'id': 1, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    err_send_verdicts_count = monitor.send_reports(fake_nodes)
    assert err_send_verdicts_count == 1

    fake_nodes = [{'id': 2, 'ip': FAKE_IP, 'rep_date': FAKE_REPORT_DATE}]
    err_send_verdicts_count = monitor.send_reports(fake_nodes)
    assert err_send_verdicts_count == 1


def test_get_bounty_neg(bounty_collector):
    status = bounty_collector.get_bounty()
    assert status == 0


def test_get_reported_nodes_pos(monitor):
    print(f'Sleep for {TEST_EPOCH - TEST_DELTA} sec')
    time.sleep(TEST_EPOCH - TEST_DELTA)
    nodes = monitor.get_validated_nodes()
    print('\n+++++++++++++++++++++++++++++')
    print('report date:')
    print(datetime.utcfromtimestamp(nodes[0]['rep_date']))
    print('now:')
    print(datetime.utcnow())
    reported_nodes = monitor.get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')

    # assert len(reported_nodes) == 1
    # assert reported_nodes[0]['id'] == 1
    assert any(node.get('id') == cur_node_id + 1 for node in reported_nodes)

    err_send_verdicts_status = monitor.send_reports(reported_nodes)
    assert err_send_verdicts_status == 0


def test_bounty_job_saves_data(bounty_collector):
    print(f'Sleep for {TEST_DELTA} sec')
    time.sleep(TEST_DELTA)
    db.clear_all_bounty_receipts()
    bounty_collector.job()
    assert db.get_count_of_bounty_receipt_records() == 1


@pytest.mark.skip(reason="skip to save time")
def test_get_bounty_pos(bounty_collector):
    print(f'Sleep for {TEST_EPOCH} sec')
    time.sleep(TEST_EPOCH)
    db.clear_all_bounty_receipts()
    status = bounty_collector.get_bounty()
    assert status == 1
    assert db.get_count_of_bounty_receipt_records() == 1


def test_get_id_from_config(monitor):
    config_file_name = 'test_node_config'
    node_index = 1
    config_node = ConfigStorage(config_file_name)
    config_node.update({'node_id': node_index})
    node_id = monitor.get_id_from_config(config_file_name)
    assert node_id == node_index
