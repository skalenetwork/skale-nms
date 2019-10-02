#   -*- coding: utf-8 -*-
#
#   This file is part of SLA
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

import skale.utils.helper as Helper
from skale.utils.helper import await_receipt, private_key_to_address

from tools.config import LOCAL_WALLET_FILENAME
from tools.config_storage import ConfigStorage
from tools.helper import TEST_DATA_DIR_PATH, init_skale

TEST_LOCAL_WALLET_PATH = os.path.join(TEST_DATA_DIR_PATH, LOCAL_WALLET_FILENAME)
TEST_EPOCH = 100
TEST_DELTA = 50

skale = init_skale()


def get_eth_nonce(web3, address):
    return web3.eth.getTransactionCount(address)


def get_nonce(skale, address):
    lib_nonce = skale.nonces.get(address)
    if not lib_nonce:
        lib_nonce = get_eth_nonce(skale.web3, address)
        skale.nonces.get(address)
    else:
        lib_nonce += lib_nonce
    return lib_nonce


def sign_and_send(skale, method, gas_amount, wallet):
    eth_nonce = get_nonce(skale, wallet['address'])
    txn = method.buildTransaction({
        'gas': gas_amount,
        'nonce': eth_nonce
    })
    signed_txn = skale.web3.eth.account.signTransaction(txn, private_key=wallet['private_key'])
    tx = skale.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f'{method.__class__.__name__} - transaction_hash: {skale.web3.toHex(tx)}')
    return tx


def generate_local_wallet(node_id):
    print('generating local wallet')
    account = skale.web3.eth.account.create()
    private_key = account.privateKey.hex()
    account_dict = {'address': account.address, 'private_key': private_key}
    print('---- account dict:')
    print(account_dict)

    local_wallet_config = ConfigStorage(TEST_LOCAL_WALLET_PATH + str(node_id))
    local_wallet_config.update(account_dict)

    print(f'local wallet address: {account.address}')
    return {'address': account.address}


def create_node(node_id):

    deposit = 100000000000000000000  # 100 SKL
    eth_amount = 10000000000000000000  # 10 ETH
    # eth_amount = 1000000000000000000000  # 1000 ETH

    generate_local_wallet(node_id)

    wallet = ConfigStorage(TEST_LOCAL_WALLET_PATH + str(node_id))
    address = wallet['address']

    eth_private_key = os.environ.get('ETH_PRIVATE_KEY')
    eth_base_account = Helper.private_key_to_address(eth_private_key)
    eth_base_account = skale.web3.toChecksumAddress(eth_base_account)
    sender_wallet = {'address': eth_base_account,
                     'private_key': eth_private_key}

    eth_base_bal = skale.web3.eth.getBalance(eth_base_account)
    skl_base_bal = skale.token.contract.functions.balanceOf(eth_base_account).call()

    print(f'ETH balance of etherbase account : {eth_base_bal}')
    print(f'SKL balance of etherbase account: {skl_base_bal}')

    if eth_base_bal > eth_amount and skl_base_bal > deposit:

        print(f'ETH balance before: {skale.web3.eth.getBalance(address)}')
        print(f'SKL balance before: {skale.token.contract.functions.balanceOf(address).call()}')

        # transfer SKL
        op = skale.token.contract.functions.transfer(address, deposit)
        gas = 90000
        tx_skl = sign_and_send(skale, op, gas, sender_wallet)
        receipt = Helper.await_receipt(skale.web3, tx_skl)
        # print(f'receipt of SKL transfer: {receipt}')

        # transfer ETH
        tx = Helper.send_eth(skale.web3, address, eth_amount, sender_wallet)
        receipt = Helper.await_receipt(skale.web3, tx)
        # print(f'receipt of ETH transfer: {receipt}')

        print(f'ETH balance after: {skale.web3.eth.getBalance(address)}')
        print(f'SKL balance after: {skale.token.contract.functions.balanceOf(address).call()}')
        print(wallet['address'])

        # create node
        ip_base = '10.1.0.'
        test_port = 56
        res = skale.manager.create_node(ip_base + str(node_id), test_port,
                                        'node_' + str(node_id), wallet)
        print(f'create_node res: {res}')

        receipt = Helper.await_receipt(skale.web3, res['tx'])
        print(f'create_node receipt: {receipt}')

    else:
        print('Insufficient funds!')


def get_active_ids():
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
    pr_key = os.environ.get('ETH_PRIVATE_KEY')
    account = skale.web3.toChecksumAddress(private_key_to_address(pr_key))

    reward_period = skale.validators_data.get_reward_period()
    delta_period = skale.validators_data.get_delta_period()
    print(reward_period, delta_period)

    wallet = {'address': account, 'private_key': pr_key}
    res = skale.constants.set_periods(TEST_EPOCH, TEST_DELTA, wallet)
    receipt = await_receipt(skale.web3, res['tx'], retries=30, timeout=6)
    print(receipt)
    print("-------------------------")
    reward_period = skale.validators_data.get_reward_period()
    delta_period = skale.validators_data.get_delta_period()
    print(reward_period, delta_period)
