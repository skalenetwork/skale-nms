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

import os
import pytest

from sla import sla_agent as sla
from tools.config import LOCAL_WALLET_FILENAME
from tools.config_storage import ConfigStorage
from tools.helper import TEST_DATA_DIR_PATH
from tools.skale_mock import init_skale

TEST_LOCAL_WALLET_PATH = os.path.join(TEST_DATA_DIR_PATH, LOCAL_WALLET_FILENAME)
ID = 0
IP_TEST = '0.0.0.0'


def setup_module(module):
    prepare_wallets(2)


@pytest.fixture(scope="module")
def monitor(request):
    print("\nskale setup")
    skale = init_skale()
    _validator = sla.Monitor(skale, ID)
    return _validator


def test_get_validated_nodes(monitor):
    nodes = monitor.get_validated_nodes()
    assert type(nodes) is list
    assert len(nodes) == 2
    assert nodes[0]['ip'] == IP_TEST
    assert nodes[0]['id'] == 1
    assert nodes[1]['id'] == 2


def test_get_reported_nodes(monitor):
    nodes = monitor.get_validated_nodes()
    reported_nodes = monitor.validate_and_get_reported_nodes(nodes)
    assert type(reported_nodes) is list

    err_send_verdicts_count = monitor.send_reports(reported_nodes)
    assert err_send_verdicts_count == 0
    monitor.job()


def prepare_wallets(count):
    account_dict = {"address": "0x0",
                    "private_key": "0x0"}
    for i in range(count):
        local_wallet_config = ConfigStorage(TEST_LOCAL_WALLET_PATH + str(i))
        local_wallet_config.update(account_dict)
