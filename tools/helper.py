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

from skale import Skale

from tools.configs import LOCAL_WALLET_FILEPATH
from tools.configs.web3 import ABI_FILEPATH, ENDPOINT

logger = logging.getLogger(__name__)


def get_local_wallet_filepath(node_id):

    if node_id is None:  # production
        return LOCAL_WALLET_FILEPATH
    else:  # test
        return LOCAL_WALLET_FILEPATH + str(node_id)


def init_skale():
    skale = Skale(ENDPOINT, ABI_FILEPATH)
    return skale
