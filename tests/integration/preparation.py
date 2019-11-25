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

import os

from skale import Skale
from skale.utils.account_tools import send_ether, send_tokens
from skale.utils.web3_utils import init_web3, wait_receipt
from skale.wallets import Web3Wallet

from tools.config_storage import ConfigStorage
from tools.configs import LOCAL_WALLET_FILEPATH
from tools.configs.web3 import ABI_FILEPATH, ENDPOINT
from tools.helper import get_local_wallet_filepath

DIR_LOG = '/skale_node_data/log'
DIR_ABI = '/skale_vol/contracts_info'
TEST_EPOCH = 200
TEST_DELTA = 100
SKL_DEPOSIT = 100
ETH_AMOUNT = 1
IP_BASE = '10.1.0.'
TEST_PORT = 123


def init_skale(node_id=None):
    if node_id is None:
        wallet = None
    else:
        local_wallet_filepath = get_local_wallet_filepath(node_id)
        local_wallet = ConfigStorage(local_wallet_filepath)
        private_key = local_wallet['private_key']
        web3 = init_web3(ENDPOINT)
        wallet = Web3Wallet(private_key, web3)
    skale = Skale(ENDPOINT, ABI_FILEPATH, wallet)
    return skale


def generate_local_wallet(node_id):
    skale = init_skale()
    print('generating local wallet')
    account = skale.web3.eth.account.create()
    private_key = account.privateKey.hex()
    account_dict = {'address': account.address, 'private_key': private_key}
    print('---- account dict:')
    print(account_dict)

    local_wallet_config = ConfigStorage(LOCAL_WALLET_FILEPATH + str(node_id))
    local_wallet_config.update(account_dict)
    return {'address': account.address}


def init_skale_with_base_wallet():
    skale = init_skale()
    eth_private_key = os.environ.get('ETH_PRIVATE_KEY')
    sender_wallet = Web3Wallet(eth_private_key, skale.web3)
    skale.wallet = sender_wallet
    return skale


def create_node(node_id):

    generate_local_wallet(node_id)

    base_skale = init_skale_with_base_wallet()
    sender_wallet = base_skale.wallet

    eth_base_bal = base_skale.web3.eth.getBalance(sender_wallet.address)
    skl_base_bal = base_skale.token.contract.functions.balanceOf(sender_wallet.address).call()

    print(f'ETH balance of etherbase account : {eth_base_bal}')
    print(f'SKL balance of etherbase account: {skl_base_bal}')

    if eth_base_bal > ETH_AMOUNT and skl_base_bal > SKL_DEPOSIT:
        skale = init_skale(node_id)
        wallet = ConfigStorage(LOCAL_WALLET_FILEPATH + str(node_id))
        address = wallet['address']

        # transfer ETH and SKL
        send_ether(base_skale.web3, sender_wallet, address, ETH_AMOUNT)
        print(f'ETH balance after: {skale.web3.eth.getBalance(address)}')

        send_tokens(base_skale, sender_wallet, address, SKL_DEPOSIT)
        print(f'SKL balance after: {skale.token.contract.functions.balanceOf(address).call()}')

        # create node
        res = skale.manager.create_node(IP_BASE + str(node_id), TEST_PORT,
                                        'node_' + str(node_id))
        receipt = wait_receipt(skale.web3, res['tx'])
        print(f'create_node receipt: {receipt}')

    else:
        print('Insufficient funds!')


def get_active_ids():
    skale = init_skale()
    return skale.nodes_data.get_active_node_ids()


def create_set_of_nodes(first_node_id, nodes_number):

    active_ids = get_active_ids()
    print(active_ids)

    if first_node_id not in active_ids:

        print(f'Starting creating {nodes_number} nodes from id = {first_node_id}:')
        for node_id in range(first_node_id, first_node_id + nodes_number):
            print(f'--- creating node, id = {node_id}')
            create_node(node_id)
    else:
        print(f'Node with id = {first_node_id} is already exists! Try another start id...')


def accelerate_skale_manager():
    skale = init_skale_with_base_wallet()

    reward_period = skale.validators_data.get_reward_period()
    delta_period = skale.validators_data.get_delta_period()
    print(f'Existing times for SM: {reward_period}, {delta_period}')

    res = skale.constants.set_periods(TEST_EPOCH, TEST_DELTA)
    receipt = wait_receipt(skale.web3, res['tx'], retries=30, timeout=6)
    print(receipt)
    print("-------------------------")
    reward_period = skale.validators_data.get_reward_period()
    delta_period = skale.validators_data.get_delta_period()
    print(f'New times for SM: {reward_period}, {delta_period}')


def create_dirs():

    if not os.path.exists(DIR_LOG):
        os.makedirs(DIR_LOG)
    if not os.path.exists(DIR_ABI):
        os.makedirs(DIR_ABI)


if __name__ == '__main__':

    accelerate_skale_manager()
    global cur_node_id
    global nodes_count_before, nodes_count_to_add
    ids = get_active_ids()
    print(f'ids = {ids}')
    nodes_count_before = len(ids)
    cur_node_id = max(ids) + 1 if nodes_count_before else 0
    nodes_count_to_add = 2
    create_set_of_nodes(cur_node_id, nodes_count_to_add)
