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

import pytest

from sla import sla_agent as sla
from tools import db
from tools.configs import LOCAL_WALLET_FILEPATH
from tools.config_storage import ConfigStorage
from tools.skale_mock import init_skale, MOCK_IP

ID = 0


def setup_module(module):
    prepare_wallets(2)


@pytest.fixture(scope="module")
def monitor(request):
    print("\nskale setup")
    skale = init_skale()
    _validator = sla.Monitor(skale, ID)
    return _validator


# @pytest.mark.skip(reason="skip to save time")
def test_get_validated_nodes(monitor):
    nodes = monitor.get_validated_nodes(monitor.skale)
    print(f'nodes = {nodes}')
    assert type(nodes) is list
    assert len(nodes) == 2
    assert nodes[0]['ip'] == MOCK_IP
    assert nodes[1]['ip'] == MOCK_IP
    assert nodes[0]['id'] == 1
    assert nodes[1]['id'] == 2


# @pytest.mark.skip(reason="skip to save time")
def test_get_reported_nodes(monitor):
    nodes = monitor.get_validated_nodes(monitor.skale)
    reported_nodes = monitor.get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    print(f'rep nodes = {reported_nodes}')
    assert len(reported_nodes) == 1
    assert reported_nodes[0]['id'] == 1

    err_send_verdicts_status = monitor.send_reports(reported_nodes)
    assert err_send_verdicts_status == 0


# @pytest.mark.skip(reason="skip to save time")
def test_report_saved_to_db(monitor):
    db.clear_all_reports()
    assert db.get_count_of_report_records() == 0
    monitor.monitor_job()
    assert db.get_count_of_report_records() == 2


# @pytest.mark.skip(reason="skip to save time")
def prepare_wallets(count):
    account_dict = {"address": "0x0",
                    "private_key": "0x0"}
    for i in range(count):
        local_wallet_config = ConfigStorage(LOCAL_WALLET_FILEPATH + str(i))
        local_wallet_config.update(account_dict)
