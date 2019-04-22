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

import logging
import os
from distutils import util

import yaml
from skale import BlockchainEnv, Skale

from tools.config import CUSTOM_CONTRACTS_PATH, LOCAL_WALLET_FILENAME, LOCAL_WALLET_FILEPATH, LOG_FOLDER, PROJECT_DIR

# NETWORK = 'aws_test'
NETWORK = 'do'
ENV_FILE = "envs.yml"
ABI_FILE = "data.json"
TEST_DATA_DIR = "test_data"
TEST_DATA_DIR_PATH = os.path.join(PROJECT_DIR, TEST_DATA_DIR)

logger = logging.getLogger(__name__)


def get_log_filepath(agent_name, node_id):

    if node_id is None:
        log_folder = LOG_FOLDER
        log_filename = agent_name.lower() + ".log"
    else:
        log_folder = TEST_DATA_DIR_PATH
        log_filename = agent_name.lower() + '_' + str(node_id) + ".log"
    log_filepath = os.path.join(log_folder, log_filename)

    return log_filepath


def get_local_wallet_filepath(node_id):

    if node_id is None:
        local_wallet_filepath = LOCAL_WALLET_FILEPATH
    else:
        local_wallet_filepath = os.path.join(TEST_DATA_DIR_PATH, LOCAL_WALLET_FILENAME) + str(node_id)
    print(local_wallet_filepath)

    return local_wallet_filepath


def init_skale():

    rpc_ip = os.environ.get("RPC_IP")
    rpc_port = os.environ.get("RPC_PORT")

    if rpc_ip is None:
        env_file_path = os.path.join(TEST_DATA_DIR_PATH, ENV_FILE)
        with open(env_file_path, 'r') as stream:
            try:
                envs = yaml.load(stream)
            except yaml.YAMLError as err:
                print(err)
            rpc_ip = envs[NETWORK]['ip']
            rpc_port = envs[NETWORK]['ws_port']

    rpc_port = int(rpc_port)

    is_test = os.environ.get("IS_TEST", "False")
    is_test = bool(util.strtobool(is_test))
    abi_filepath = os.path.join(TEST_DATA_DIR_PATH, ABI_FILE) if is_test else CUSTOM_CONTRACTS_PATH
    skale = Skale(BlockchainEnv.CUSTOM, rpc_ip, rpc_port, abi_filepath)

    return skale
