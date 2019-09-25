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
import logging.handlers as py_handlers
import os
import sys
from logging import Formatter, StreamHandler

# from cmreslogging.handlers import CMRESHandler
from tools.config import LOG_BACKUP_COUNT, LOG_FILE_SIZE_BYTES, LOG_FOLDER, LOG_FORMAT
from tools.helper import TEST_DATA_DIR_PATH


def init_logger(log_file_path, agent_name):
    handlers = []

    formatter = Formatter(LOG_FORMAT)
    f_handler = py_handlers.RotatingFileHandler(log_file_path,
                                                maxBytes=LOG_FILE_SIZE_BYTES,
                                                backupCount=LOG_BACKUP_COUNT)

    f_handler.setFormatter(formatter)
    f_handler.setLevel(logging.INFO)
    handlers.append(f_handler)

    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    # stream_handler.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.INFO)
    handlers.append(stream_handler)

    # elastic_handler = CMRESHandler(hosts=[{'host': '138.197.195.58', 'port': 9200}],
    #
    #                        auth_type=CMRESHandler.AuthType.NO_AUTH,
    #                        es_index_name="skale_index",
    #                        es_additional_fields={'App': 'SLA', 'Container': agent_name})
    #
    # handlers.append(elastic_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)


def init_agent_logger(agent_name, node_id):
    log_path = get_log_filepath(agent_name, node_id)
    init_logger(log_path, agent_name)


def get_log_filepath(agent_name, node_id):

    if node_id is None:
        log_folder = LOG_FOLDER
        log_filename = agent_name.lower() + ".log"
    else:
        log_folder = TEST_DATA_DIR_PATH
        log_filename = agent_name.lower() + '_' + str(node_id) + ".log"
    log_filepath = os.path.join(log_folder, log_filename)

    return log_filepath
