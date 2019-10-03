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

import secrets
import socket
import struct
from datetime import datetime, timezone

from hexbytes import HexBytes

REWARD_PERIOD = 600
MOCK_IP = '0.0.0.0'


def node_to_bytes(node_id, date, node_ip):
    b_id = node_id.to_bytes(14, byteorder='big')
    b_date = date.to_bytes(14, byteorder='big')
    int_ip = struct.unpack("!I", socket.inet_aton(node_ip))[0]
    b_ip = int_ip.to_bytes(4, byteorder='big')
    return b_id + b_date + b_ip


def bytes_to_node(node_in_bytes):
    node_id = int.from_bytes(node_in_bytes[:14], byteorder='big')
    report_date = int.from_bytes(node_in_bytes[14:28], byteorder='big')
    node_ip = socket.inet_ntoa(node_in_bytes[28:])
    return {'id': node_id, 'ip': node_ip, 'rep_date': report_date}


def generate_random_hash():
    str_hash = secrets.token_hex(32)
    rand_hash = HexBytes(str_hash)
    return rand_hash


# Set of classes for mocking sla/bounty features of skale.py for testing without real SCs


class ValidatorsData:
    def get_validated_array(self, node_id=None, account=None):
        # now = datetime.utcnow().timestamp()
        now = int(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp())
        rep_date0 = now
        rep_date1 = now + REWARD_PERIOD
        bytes_node0 = node_to_bytes(node_id + 1, rep_date0, MOCK_IP)
        bytes_node1 = node_to_bytes(node_id + 2, rep_date1, MOCK_IP)
        return [bytes_node0, bytes_node1]

    def get_reward_period(self):
        return REWARD_PERIOD


class BountyEvent:
    def processReceipt(self, receipt):
        h_receipt = []
        args = {}
        args['time'] = 11111111
        args['nodeIndex'] = 0
        args['bounty'] = 222222
        args['averageLatency'] = 100
        args['averageDowntime'] = 0
        args['gasSpend'] = 33333
        h_receipt.append({'args': args})
        return tuple(h_receipt)


class Events:
    def BountyGot(self):
        receipt = BountyEvent()
        return receipt


class Contract:
    def __init__(self):
        self.events = Events()


class Manager:
    def __init__(self):
        self.contract = Contract()

    def send_verdict(self, my_node_id, target_node_id, downtime, latency, wallet):
        return {'tx': 0x0}

    def get_bounty(self, id, local_wallet):
        return {'tx': 0x0}


class NodesData:
    def get(self, node_id=None):
        utc_now = datetime.utcnow()
        last_reward_date = utc_now.replace(tzinfo=timezone.utc).timestamp() - REWARD_PERIOD - 10
        return {'last_reward_date': last_reward_date}

# reward_date = self.skale.nodes_data.get(self.id)['last_reward_date'] + reward_period


class Eth:
    def getTransactionReceipt(self, tx):
        return {'status': 1, 'transactionHash': generate_random_hash(), 'gasUsed': 10000}

    def getBalance(self, address):
        return 2000000


class Web3:
    def __init__(self):
        self.eth = Eth()

    def toChecksumAddress(self, account=None):
        return account


class Token:
    def get_balance(self, address):
        return 1000000


class Skale:
    """Mock class for testing SLA and Bounty agents"""
    def __init__(self, skale_env, ip=None, ws_port=None, abi_filepath=None):
        self.validators_data = ValidatorsData()
        self.web3 = Web3()
        self.local_wallet = {'address': None}
        self.manager = Manager()
        self.nodes_data = NodesData()
        self.token = Token()


def init_skale():
    skale = Skale(None)
    return skale
