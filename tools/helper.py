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

import logging
import os
from datetime import datetime

from skale import Skale
from skale.utils.web3_utils import init_web3
from skale.wallets import RPCWallet, Web3Wallet

from tools.config_storage import ConfigStorage
from tools.configs import ENV, LOCAL_WALLET_FILEPATH
from tools.configs.web3 import ABI_FILEPATH, ENDPOINT

logger = logging.getLogger(__name__)


def init_skale(node_id=None):
    if node_id is None:
        wallet = RPCWallet(os.environ['TM_URL']) if ENV != 'DEV' else None
    else:
        local_wallet_filepath = get_local_wallet_filepath(node_id)
        local_wallet = ConfigStorage(local_wallet_filepath)
        private_key = local_wallet['private_key']
        web3 = init_web3(ENDPOINT)
        wallet = Web3Wallet(private_key, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
    return skale


def run_agent(args, agent_class):
    if len(args) > 1 and args[1].isdecimal():
        node_id = int(args[1])
    else:
        node_id = None

    skale = init_skale(node_id)
    agent = agent_class(skale, node_id)
    agent.run()


def get_local_wallet_filepath(node_id):
    if node_id is None:  # production
        return LOCAL_WALLET_FILEPATH
    else:  # test
        return LOCAL_WALLET_FILEPATH + str(node_id)


def find_block_for_tx_stamp(skale, tx_stamp, lo=0, hi=None):
    """Return nearest block number to given transaction timestamp"""
    count = 0
    if hi is None:
        hi = skale.web3.eth.blockNumber
    while lo < hi:
        mid = (lo + hi) // 2
        block_data = skale.web3.eth.getBlock(mid)
        midval = datetime.utcfromtimestamp(block_data['timestamp'])
        if midval < tx_stamp:
            lo = mid + 1
        elif midval > tx_stamp:
            hi = mid
        else:
            return mid
        count += 1
    print(f'Number of iterations = {count}')
    return lo


def check_node_id(skale, node_id):
    return node_id in skale.nodes_data.get_active_node_ids()
