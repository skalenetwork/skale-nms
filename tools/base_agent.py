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

"""
Module contains BaseAgent class - base class for SLA and Bounty agents
"""
import json
import logging

import tenacity

from tools.configs import NODE_CONFIG_FILEPATH
from tools.exceptions import NodeNotFoundException
from tools.helper import check_node_id
from tools.logger import init_agent_logger


class BaseAgent:
    """Base class for SLA and Bounty agents"""

    def __init__(self, skale, node_id=None):
        self.agent_name = self.__class__.__name__
        init_agent_logger(self.agent_name, node_id)
        self.logger = logging.getLogger(__name__)

        self.logger.info(f'Initialization of {self.agent_name} ...')
        if node_id is None:
            self.id = self.get_id_from_config(NODE_CONFIG_FILEPATH)
            self.is_test_mode = False
        else:
            self.id = node_id
            self.is_test_mode = True
        self.skale = skale
        if not check_node_id(self.skale, self.id):
            err_msg = f'There is no Node with ID = {self.id} in SKALE manager'
            self.logger.error(err_msg)
            raise NodeNotFoundException(err_msg)
        self.logger.info(f'Node ID = {self.id}')
        self.logger.info(f'Initialization of {self.agent_name} is completed')

    @tenacity.retry(wait=tenacity.wait_fixed(10))
    def get_id_from_config(self, node_config_filepath) -> int:
        """Gets node ID from config file for agent initialization"""
        try:
            self.logger.debug('Reading node id from config file...')
            with open(node_config_filepath) as json_file:
                data = json.load(json_file)
            return data['node_id']
        except KeyError as err:
            self.logger.warning(
                f'Cannot read a node id (KeyError) - is the node already registered?'
            )
            raise err
        except FileNotFoundError as err:
            self.logger.warning(
                f'Cannot read a node id - config file is not found'
            )
            raise err
        except Exception as err:
            self.logger.exception(f'Cannot read config from the file: {err}')
            raise err
