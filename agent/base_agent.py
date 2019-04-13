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

"""
Module contains BaseAgent class - base class for SLA and Bounty agents
"""
import json
import logging
import logging.handlers as py_handlers
import sys
import time

import schedule
import tenacity

from agent import helper
from tools.config import LOG_BACKUP_COUNT, LOG_FILE_SIZE_BYTES, LOG_FORMAT, NODE_CONFIG_FILEPATH
from tools.config_storage import ConfigStorage


class BaseAgent:
    """Base class for SLA and Bounty agents"""

    def __init__(self, skale, node_id=None):
        self.agent_name = self.__class__.__name__

        log_filepath = helper.get_log_filepath(self.agent_name, node_id)

        self.logger = logging.getLogger(self.agent_name)
        self.logger.setLevel(logging.DEBUG)

        try:
            fh = py_handlers.RotatingFileHandler(
                log_filepath,
                maxBytes=LOG_FILE_SIZE_BYTES,
                backupCount=LOG_BACKUP_COUNT)
            formatter = logging.Formatter(LOG_FORMAT)
            fh.setFormatter(formatter)

            self.logger.addHandler(fh)
        except Exception as err:
            self.logger.error(f"Cannot log into the file: {err}")

        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)

        self.logger.info(f"Initialization of {self.agent_name} started...")
        self.id = node_id if node_id else self.get_id_from_config()
        local_wallet_filepath = helper.get_local_wallet_filepath(node_id)
        self.local_wallet = ConfigStorage(local_wallet_filepath)

        self.account = self.local_wallet['address']
        self.skale = skale
        self.logger.debug(f"Node ID = {self.id}")
        self.logger.debug(f"Account = {self.account}")
        self.logger.info(f"Initialization of {self.agent_name} is completed")

    @tenacity.retry(
        wait=tenacity.wait_fixed(10),
        retry=tenacity.retry_if_exception_type(KeyError) | tenacity.retry_if_exception_type(FileNotFoundError))
    def get_id_from_config(self) -> int:
        """Gets node ID from config file for agent initialization"""
        try:
            self.logger.debug("Reading node id from config file...")
            with open(NODE_CONFIG_FILEPATH) as json_file:
                data = json.load(json_file)
            return data["node_id"]
        except KeyError as err:
            self.logger.warning(
                f"Cannot read a node id (KeyError) - is the node already installed?"
            )
            raise err
        except FileNotFoundError as err:
            self.logger.warning(
                f"Cannot read a node id (FileNotFoundError) - is the node already installed?"
            )
            raise err
        except Exception as err:
            self.logger.exception(f"Cannot read config from the file: {err}")
            raise err

    def job(self) -> None:
        """Periodic job"""
        pass

    def run(self) -> None:
        """Starts running agent"""
        self.logger.info(f"{self.agent_name} started")
        self.job()
        schedule.every(1).minutes.do(self.job)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    pass
