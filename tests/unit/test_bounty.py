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

from bounty import bounty_agent as bounty
from tools import db
from tools.configs import LOCAL_WALLET_FILEPATH
from tools.config_storage import ConfigStorage
from tools.skale_mock import init_skale

ID = 0
IP_TEST = '0.0.0.0'

pytestmark = pytest.mark.skip("all tests until new mock functions are implemented")


def setup_module(module):
    prepare_wallets(2)


def prepare_wallets(count):
    account_dict = {"address": "0x0",
                    "private_key": "0x0"}
    for i in range(count):
        local_wallet_config = ConfigStorage(LOCAL_WALLET_FILEPATH + str(i))
        local_wallet_config.update(account_dict)


@pytest.fixture(scope="module")
def bounty_collector(request):
    skale = init_skale()
    _bounty_collector = bounty.BountyCollector(skale, ID)
    return _bounty_collector


@pytest.mark.skip(reason="skip to save time")
def test_get_bounty(bounty_collector):
    assert bounty_collector.get_bounty() == 1


@pytest.mark.skip(reason="skip to save time")
def test_bounty_job_saves_data(bounty_collector):
    db.clear_all_bounty_receipts()
    bounty_collector.job()
    assert db.get_count_of_bounty_receipt_records() == 1
