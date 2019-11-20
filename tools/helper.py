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
from datetime import datetime
from tools.config_storage import ConfigStorage
import requests
from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3

from tools.configs import LOCAL_WALLET_FILEPATH
from tools.configs.web3 import ABI_FILEPATH, ENDPOINT

PORT = '3007'
HEALTH_REQ_URL = '/healthchecks/containers'

logger = logging.getLogger(__name__)


def init_skale(node_id=None):
    # return Skale(ENDPOINT, ABI_FILEPATH)
    local_wallet_filepath = get_local_wallet_filepath(node_id)
    local_wallet = ConfigStorage(local_wallet_filepath)
    private_key = local_wallet['private_key']
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(private_key, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
    return skale


def get_local_wallet_filepath(node_id):

    if node_id is None:  # production
        return LOCAL_WALLET_FILEPATH
    else:  # test
        return LOCAL_WALLET_FILEPATH + str(node_id)


def find_block_for_tx_stamp(skale, tx_stamp, lo=0, hi=None):
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
    print(f'number of iters = {count}')
    return lo


def get_containers_healthcheck(host, test_mode):
    if test_mode:
        return 0
    url = 'http://' + host + ':' + PORT + HEALTH_REQ_URL
    print(url)
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        print(f'Could not connect to {url}')
        return 1

    if response.status_code != requests.codes.ok:
        print('Request failed, status code:', response.status_code)
        return 1

    json = response.json()
    if json['res'] != 1:
        for error in response.json()['errors']:
            print(error)
        return 1
    else:
        data = json['data']
    for container in data:
        if not container['state']['Running']:
            return 1
    return 0


def check_node_id(skale, node_id):
    return node_id in skale.nodes_data.get_active_node_ids()
