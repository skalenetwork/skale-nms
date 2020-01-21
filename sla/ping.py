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

import pingparsing


def get_node_metrics(host) -> dict:
    """Returns a node host metrics (downtime and latency)"""

    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination_host = host
    transmitter.ping_option = '-w1'
    transmitter.count = 3
    result = transmitter.ping()

    if ping_parser.parse(
            result).as_dict()['rtt_avg'] is None or ping_parser.parse(
                result).as_dict()['packet_loss_count'] > 0:
        is_dead = True
        latency = -1
        print('No connection to host!')
    else:
        is_dead = False
        latency = int((ping_parser.parse(result).as_dict()['rtt_avg']) * 1000)
        # print('Ping ok!')

    return {'is_offline': is_dead, 'latency': latency}
