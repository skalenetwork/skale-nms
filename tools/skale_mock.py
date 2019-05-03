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

import struct
import socket


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
    return node_id, report_date, node_ip


class ValidatorsData:
    def get_validated_array(self, node_id=None, account=None):
        rep_date0 = 1556627743
        rep_date1 = 1556928000
        ip0 = '0.0.0.0'
        ip1 = '0.0.0.1'
        print(f'node id = {node_id}')
        bytes_node0 = node_to_bytes(node_id + 1, rep_date0, ip0)
        bytes_node1 = node_to_bytes(node_id + 2, rep_date1, ip1)
        return [bytes_node0, bytes_node1]

    def get_reward_period():
        return 600


class Web3:
    def toChecksumAddress(self, account=None):
        return account


class Skale:
    def __init__(self, skale_env, ip=None, ws_port=None, abi_filepath=None):
        self.validators_data = ValidatorsData()
        self.web3 = Web3()
        self.local_wallet = {'address': None}


def init_skale():
    skale = Skale(None)
    return skale


