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

from bounty import bounty_agent as bounty
from tools import db
from tools.config import LOCAL_WALLET_FILENAME
from tools.config_storage import ConfigStorage
from tools.helper import TEST_DATA_DIR_PATH
from tools.skale_mock import init_skale

TEST_LOCAL_WALLET_PATH = os.path.join(TEST_DATA_DIR_PATH, LOCAL_WALLET_FILENAME)
ID = 0
IP_TEST = '0.0.0.0'


def setup_module(module):
    prepare_wallets(2)


def test_get_bounty():
    skale = init_skale()
    db.clear_all_bounty_receipts()
    bounty_collector = bounty.BountyCollector(skale, ID)
    # assert bounty_collector.get_bounty() == 1
    bounty_collector.job()
    assert db.get_count_of_bounty_receipt_records() == 1


def prepare_wallets(count):
    account_dict = {"address": "0x0",
                    "private_key": "0x0"}
    for i in range(count):
        local_wallet_config = ConfigStorage(TEST_LOCAL_WALLET_PATH + str(i))
        local_wallet_config.update(account_dict)
