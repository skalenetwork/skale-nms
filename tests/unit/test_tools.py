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

from tools.config_storage import ConfigStorage
from tools.configs import LOCAL_WALLET_FILEPATH
from tools.configs.logs import LOG_FOLDER
from tools.helper import get_local_wallet_filepath
from tools.logger import get_log_filepath

TEST_DIR1 = 'test_node1'
TEST_DIR2 = 'test_node2'


def test_config_storage():
    config_node1 = ConfigStorage(TEST_DIR1)
    config_node1.update({'node_id': 1})
    node_id = config_node1['node_id']
    assert node_id == 1

    node_id = config_node1.safe_get('node_id')
    assert node_id == 1

    node_id = config_node1.safe_get('wrong_node_id')
    assert node_id is None

    config_node2 = ConfigStorage(TEST_DIR2, {'node_id': 2})
    node_id = config_node2['node_id']
    assert node_id == 2

    config_node2.update({'node_id': 3})
    node_id = config_node2['node_id']
    assert node_id == 3

    config_node2['node_id'] = 4
    node_id = config_node2['node_id']
    assert node_id == 4

    test_config = config_node2.get()
    node_id = test_config['node_id']
    assert node_id == 4


def test_get_local_wallet_filepath():
    node_id = 1
    assert get_local_wallet_filepath(None) == LOCAL_WALLET_FILEPATH
    assert get_local_wallet_filepath(node_id) == LOCAL_WALLET_FILEPATH + str(node_id)


def test_get_log_filepath():
    assert get_log_filepath('AGENT', None) == os.path.join(LOG_FOLDER, 'agent.log')
    assert get_log_filepath('aGenT', 1) == os.path.join(LOG_FOLDER, 'agent_1.log')


def teardown_module(module):
    os.remove(TEST_DIR1)
    os.remove(TEST_DIR2)
