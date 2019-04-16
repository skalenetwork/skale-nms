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
#   but WITHOUT ANY WARRANTY; without even the implied warranty off
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import socket

import skale.utils.helper as Helper

from tools.config import LOCAL_WALLET_FILENAME
from tools.config_storage import ConfigStorage
from tools.helper import TEST_DATA_DIR, init_skale

TEST_LOCAL_WALLET_PATH = os.path.join(TEST_DATA_DIR, LOCAL_WALLET_FILENAME)
skale = init_skale()
print(TEST_LOCAL_WALLET_PATH)


def get_node_info(node_id: int = None) -> tuple:
    """
    Returns a tuple of node properties: account, reward_date
    """
    node = skale.nodes_data.get(node_id)
    print(node)
    print(socket.inet_ntoa(node['ip']))
    account = Helper.public_key_to_address(node['publicKey'].hex())
    return account, node['last_reward_date']


class MyError(Exception):
    pass


def get_validated_nodes(node_id: int = None, account: str = None) -> None:
    """
    Returns a list of nodes to validate - node node_id, report date, ip address
    """
    if node_id is not None:
        # self.id = node_id
        account, reward_date = get_node_info(node_id)
    try:
        # nodes_in_bytes_array = skale.validators.get_validated_array(node_id, account)
        nodes_in_bytes_array = skale.validators_data.get_validated_array(node_id, account)
    except Exception as err:
        print(f'Cannot get a list of nodes for validating {str(err)}')
        raise
        # return None

    print(f'Number of nodes for validating: {len(nodes_in_bytes_array)}')

    nodes = []
    for node_in_bytes in nodes_in_bytes_array:
        node_id = int.from_bytes(node_in_bytes[:14], byteorder='big')
        report_date = int.from_bytes(node_in_bytes[14:28], byteorder='big')
        node_ip = socket.inet_ntoa(node_in_bytes[28:])

        print('---------------------------------')
        print(node_id)
        print(report_date)
        print(node_ip)

        nodes.append({'id': node_id, 'ip': node_ip, 'rep_date': report_date})
    return nodes


def get_event(event):
    print('Got it!')


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
    # todo: pass optional extra_entropy
    account = skale.web3.eth.account.create()
    private_key = account.privateKey.hex()
    print(f'private_key:    {private_key}')
    account_dict = {'address': account.address, 'private_key': private_key}
    print('---- dict:')
    print(account_dict)

    local_wallet_config = ConfigStorage(TEST_LOCAL_WALLET_PATH + str(node_id))
    local_wallet_config.update(account_dict)

    print(f'local wallet address: {account.address}')
    return {'address': account.address}


def get_ip(first):

    base_ip = '10.1.0.'

    last = 255
    for _i in range(first, last):
        # print(base_ip + str(i))
        yield base_ip + str(_i)


def create_node(node_id):

    generate_local_wallet(node_id)

    wallet = ConfigStorage(TEST_LOCAL_WALLET_PATH + str(node_id))
    address = wallet['address']

    eth_private_key = os.environ.get('ETH_PRIVATE_KEY')

    db_address = Helper.private_key_to_address(eth_private_key)

    db_address = skale.web3.toChecksumAddress(db_address)
    sender_wallet = {'address': db_address,
                     'private_key': eth_private_key}

    deposit = 100000000000000000000
    eth_amount = 10000000000000000000
    # eth_amount = 1000000000000000000000

    print(f'ETH balance of etherbase account : {skale.web3.eth.getBalance(db_address)}')
    print(f'SKL balance of etherbase account: {skale.token.contract.functions.balanceOf(db_address).call()}')

    eth_base_bal = skale.web3.eth.getBalance(db_address)
    skl_base_bal = skale.token.contract.functions.balanceOf(db_address).call()

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
        print('receipt SKL transfer')
        print(receipt)

        # transfer ETH
        tx = Helper.send_eth(skale.web3, address, eth_amount, sender_wallet)
        receipt = Helper.await_receipt(skale.web3, tx)

        print('receipt ETH transfer')
        print(receipt)

        print(f'ETH balance after: {skale.web3.eth.getBalance(address)}')
        print(f'SKL balance after: {skale.token.contract.functions.balanceOf(address).call()}')
        print(wallet['address'])

        # create node
        res = skale.manager.create_node('10.1.0.' + str(node_id), int(56), 'node_' + str(node_id), wallet)
        print(f'create_node res: {res}')

        receipt = Helper.await_receipt(skale.web3, res['tx'])  # todo: return tx and wait for the receipt in async mode
        print(f'create_node receipt: {receipt}')
        # time.sleep(5)

    else:
        print('Insufficient funds!')


def get_active_ids():
    return skale.nodes_data.get_active_node_ids()


def create_set_of_nodes(first_node_id, nodes_number):

    active_ids = get_active_ids()
    print(active_ids)

    if first_node_id not in active_ids:

        print(f'Starting creating {nodes_number} nodes from id = {first_node_id}:')
        for _node_id in range(first_node_id, first_node_id + nodes_number):
            print(f'--- creating node, id = {_node_id}')
            create_node(_node_id)
            # print(f'--- Details for the node with id = {_node_id}:')
    #         try:
    #             get_node_info(_node_id)
    #             print(get_validated_nodes(_node_id))
    #         except Exception as err:
    #             print(f'Error: {err}')
    else:
        print(f'Node with id = {first_node_id} is already exists! Try another start id...')


if __name__ == '__main__':

    # active_ids = skale.nodes_data.get_active_node_ids()
    # print(active_ids)

    # _node_id = 5

    _first_node_id = 0
    _nodes_number = 2
    # create_set_of_nodes(_first_node_id, _nodes_number)
    eth_private_key = os.environ.get('ETH_PRIVATE_KEY')
    db_address = Helper.private_key_to_address(eth_private_key)

    db_address = skale.web3.toChecksumAddress(db_address)
    sender_wallet = {'address': db_address,
                     'private_key': eth_private_key}

    deposit = 200000000000000000000
    eth_amount = 10000000000000000000  # 10 ETH

    print(f'ETH balance of etherbase account : {skale.web3.eth.getBalance(db_address)}')
    print(f'SKL balance of etherbase account: {skale.token.contract.functions.balanceOf(db_address).call()}')
