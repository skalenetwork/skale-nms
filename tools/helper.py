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
from distutils import util

from dotenv import load_dotenv
from skale import Skale
from tools.configs.web3 import ABI_FILEPATH
from tools.configs import LOCAL_WALLET_FILEPATH, LOG_FOLDER, NODE_DATA_PATH
from tools.config import TEST_DATA_DIR_PATH

is_test = os.environ.get("IS_TEST", "False")
is_test = bool(util.strtobool(is_test))

NETWORK = 'local'
# NETWORK = 'do'
ENV_FILE = ".env"

LOCK_FILE = "tx.lock"

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
    # log_filename = agent_name.lower() if node_id is None else agent_name.lower() \
    #                                                           + '_' + str(node_id)
    # log_filepath = os.path.join(LOG_FOLDER, log_filename + ".log")

    if node_id is None:  # production
        log_filename = agent_name.lower() + ".log"
    else:  # test
        log_filename = agent_name.lower() + '_' + str(node_id) + ".log"
    log_filepath = os.path.join(LOG_FOLDER, log_filename)
    return log_filepath


def get_local_wallet_filepath(node_id):

    if node_id is None:  # production
        return LOCAL_WALLET_FILEPATH
    else:  # test
        return LOCAL_WALLET_FILEPATH + str(node_id)


def init_skale():
    print(ENDPOINT, " --- ", ABI_FILEPATH)
    skale = Skale(ENDPOINT, ABI_FILEPATH)
    return skale
