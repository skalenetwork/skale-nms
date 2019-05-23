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

from sla import ping, sim
from sla import sla_agent as sla
from tools.config import LOCAL_WALLET_FILENAME
from tools.config_storage import ConfigStorage
from tools.helper import TEST_DATA_DIR_PATH
from tools.skale_mock import init_skale

TEST_LOCAL_WALLET_PATH = os.path.join(TEST_DATA_DIR_PATH, LOCAL_WALLET_FILENAME)
ID = 0
IP_GOOD = '8.8.8.8'
IP_BAD = '192.0.2.0'


def setup_module(module):
    prepare_wallets(2)


def test_get_node_metrics_pos():
    ip = IP_GOOD
    metrics_ok = ping.get_node_metrics(ip)
    latency = metrics_ok['latency']
    downtime = metrics_ok['is_alive']
    print(metrics_ok)

    assert type(latency) is float
    assert latency >= 0
    assert type(downtime) is bool


def test_get_node_metrics_neg():
    ip = IP_BAD
    metrics_ok = ping.get_node_metrics(ip)
    latency = metrics_ok['latency']
    downtime = metrics_ok['is_alive']
    print(metrics_ok)

    assert type(latency) is int
    assert latency == 10000
    assert downtime is False


def test_generate_node_metrics():
    metrics = sim.generate_node_metrics()
    latency = metrics['latency']
    downtime = metrics['is_alive']
    print(metrics)

    assert latency >= 20
    assert latency <= 210
    assert type(downtime) is bool


def test_sla_with_mock_skale():
    skale = init_skale()
    validator = sla.Validator(skale, ID)
    nodes = validator.get_validated_nodes()
    assert type(nodes) is list
    reported_nodes = validator.validate_and_get_reported_nodes(nodes)
    assert type(reported_nodes) is list
    err_send_verdicts_count = validator.send_verdicts(reported_nodes)
    assert err_send_verdicts_count == 0
    validator.job()


def prepare_wallets(count):
    account_dict = {"address": "0x0",
                    "private_key": "0x0"}
    for i in range(count):
        local_wallet_config = ConfigStorage(TEST_LOCAL_WALLET_PATH + str(i))
        local_wallet_config.update(account_dict)
