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

import logging
import os
from distutils import util

from dotenv import load_dotenv
from skale import Skale

from tools.config import (
    CUSTOM_CONTRACTS_PATH, LOCAL_WALLET_FILENAME, LOCAL_WALLET_FILEPATH, LOG_FOLDER,
    NODE_DATA_PATH, PROJECT_DIR)

NETWORK = 'local'
# NETWORK = 'do'
ENV_FILE = ".env"
ABI_FILE = "data.json"
LOCK_FILE = "tx.lock"
TEST_DATA_DIR = "test_data"
TEST_DATA_DIR_PATH = os.path.join(PROJECT_DIR, TEST_DATA_DIR)
DOTENV_PATH = os.path.join(TEST_DATA_DIR_PATH, ENV_FILE)


load_dotenv(DOTENV_PATH)
ENDPOINT = os.environ['ENDPOINT']

logger = logging.getLogger(__name__)


def get_lock_filepath():
    is_test = os.environ.get("IS_TEST", "False")
    is_test = bool(util.strtobool(is_test))
    lock_path = os.path.join(TEST_DATA_DIR_PATH, LOCK_FILE) if is_test \
        else os.path.join(NODE_DATA_PATH, LOCK_FILE)
    return lock_path


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
        local_wallet_filepath = os.path.join(TEST_DATA_DIR_PATH, LOCAL_WALLET_FILENAME) + \
                                str(node_id)
    print(local_wallet_filepath)

    return local_wallet_filepath


def init_skale():

    is_test = os.environ.get("IS_TEST", "False")
    is_test = bool(util.strtobool(is_test))
    abi_filepath = os.path.join(TEST_DATA_DIR_PATH, ABI_FILE) if is_test else CUSTOM_CONTRACTS_PATH
    print('\n++++++++++++++++++++++++++++++++++++++++++')
    print(f' PATH = {abi_filepath}')
    print(f' endpoint = {ENDPOINT}')
    skale = Skale(ENDPOINT, abi_filepath)
    print(f'init completed')
    return skale
