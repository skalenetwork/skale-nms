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

import os

SKALE_VOLUME_PATH = '/skale_vol'
NODE_DATA_PATH = '/skale_node_data'

CONFIG_FOLDER_NAME = 'config'
LOG_FOLDER_NAME = 'log'

CUSTOM_CONTRACTS_FILENAME = 'data.json'
DKG_CONTRACT_DATA_FILENAME = 'dkg_contract_data.json'

# project dirs

HERE = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.join(HERE, os.pardir)
PROJECT_CONFIG_FOLDER = os.path.join(PROJECT_DIR, 'config')
PROJECT_TOOLS_FOLDER = os.path.join(PROJECT_DIR, 'tools')
PROJECT_LOG_FOLDER = os.path.join(PROJECT_DIR, LOG_FOLDER_NAME)

CONTAINERS_FILENAME = 'containers.json'
PROJECT_CONTAINERS_FILEPATH = os.path.join(PROJECT_CONFIG_FOLDER, CONTAINERS_FILENAME)

BUILD_LOG_FILENAME = 'build.log'
BUILD_LOG_PATH = os.path.join(PROJECT_LOG_FOLDER, BUILD_LOG_FILENAME)

PROJECT_ABI_FILEPATH = os.path.join(PROJECT_CONFIG_FOLDER, CUSTOM_CONTRACTS_FILENAME)


# node data

# logs

LOG_FOLDER = os.path.join(NODE_DATA_PATH, LOG_FOLDER_NAME)

ADMIN_LOG_FILENAME = 'admin.log'
ADMIN_LOG_PATH = os.path.join(LOG_FOLDER, ADMIN_LOG_FILENAME)

DEBUG_LOG_FILENAME = 'debug.log'
DEBUG_LOG_PATH = os.path.join(LOG_FOLDER, DEBUG_LOG_FILENAME)

LOG_FILE_SIZE_MB = 100
LOG_FILE_SIZE_BYTES = LOG_FILE_SIZE_MB * 1000000

LOG_BACKUP_COUNT = 3

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# schains

SCHAINS_DIR_NAME = 'schains'
SCHAINS_DIR_PATH = os.path.join(NODE_DATA_PATH, SCHAINS_DIR_NAME)
DATA_DIR_NAME = 'data_dir'

HEALTHCHECK_FILENAME = 'HEALTH_CHECK'
HEALTHCHECK_STATUSES = {'-1': 'not inited', '-2': 'wrong value', '0': 'fail', '1': 'passing', '2': 'passed'}

# other

LOCAL_WALLET_FILENAME = 'local_wallet.json'
LOCAL_WALLET_FILEPATH = os.path.join(NODE_DATA_PATH, LOCAL_WALLET_FILENAME)

DB_FILENAME = 'skale.db'
DB_FILE = os.path.join(NODE_DATA_PATH, DB_FILENAME)

TOKENS_FILENAME = 'tokens.json'
TOKENS_FILEPATH = os.path.join(NODE_DATA_PATH, TOKENS_FILENAME)

FLASK_SECRET_KEY_FILENAME = 'flask_db_key.txt'
FLASK_SECRET_KEY_FILE = os.path.join(NODE_DATA_PATH, FLASK_SECRET_KEY_FILENAME)

NODE_CONFIG_FILENAME = 'node_config.json'
NODE_CONFIG_FILEPATH = os.path.join(NODE_DATA_PATH, NODE_CONFIG_FILENAME)


# skale vol

CONFIG_FOLDER = os.path.join(SKALE_VOLUME_PATH, CONFIG_FOLDER_NAME)

# CUSTOM_CONTRACTS_PATH = os.path.join(NODE_DATA_PATH, CUSTOM_CONTRACTS_FILENAME)
CUSTOM_CONTRACTS_PATH = os.path.join(CONFIG_FOLDER, CUSTOM_CONTRACTS_FILENAME) # todo: tmp - store contracts data in skale_vol
DKG_CONTRACT_DATA_PATH = os.path.join(NODE_DATA_PATH, DKG_CONTRACT_DATA_FILENAME)

BASE_SCHAIN_CONFIG_FILENAME = 'schain_base_config.json'

CONTAINERS_FILEPATH = os.path.join(CONFIG_FOLDER, CONTAINERS_FILENAME)
BASE_SCHAIN_CONFIG_FILEPATH = os.path.join(CONFIG_FOLDER, BASE_SCHAIN_CONFIG_FILENAME)

PROXY_ABI_FILENAME = 'proxy.json'
MAINNET_PROXY_PATH = os.path.join(CONFIG_FOLDER, PROXY_ABI_FILENAME)

# server

EVENTS_POLL_INTERVAL = 5

# docker

SKALE_PREFIX = 'skalelabshub'
CONTAINER_NAME_PREFIX = 'skale_'
DOCKER_USERNAME = os.environ.get('DOCKER_USERNAME')
DOCKER_PASSWORD = os.environ.get('DOCKER_PASSWORD')

CONTAINER_FORCE_STOP_TIMEOUT = 20

TEST_PWD = 11111111

PORTS_PER_SCHAIN = 11

LOG_TYPES = ['base', 'schain']
SCHAIN_LOG_NAME = 'skaled.log'
SCHAIN_LOG_PATTERN = '*.log'

# sChain config

SCHAIN_OWNER_ALLOC = 1000000000000000000000
# NODE_OWNER_ALLOC = 1000000000000000000
NODE_OWNER_ALLOC = 1000000000000000000000  # todo: tmp!

# ktm

KTM_CONFIG_NAME = 'ktm'
