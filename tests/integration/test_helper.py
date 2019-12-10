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

from datetime import datetime

from tools.helper import find_block_for_tx_stamp, init_skale


def test_find_block_for_tx_stamp():

    skale = init_skale()
    block_number = skale.web3.eth.blockNumber
    utc_now = datetime.utcnow()
    last_block_number = find_block_for_tx_stamp(skale, utc_now)
    block_data = skale.web3.eth.getBlock(last_block_number)
    block_timestamp = str(datetime.utcfromtimestamp(block_data['timestamp']))

    assert type(last_block_number) == int
    assert last_block_number >= 0
    assert last_block_number >= block_number
    assert datetime.strptime(block_timestamp, '%Y-%m-%d %H:%M:%S') <= utc_now
