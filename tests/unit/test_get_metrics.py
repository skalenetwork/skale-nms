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


from sla import ping

ID = 0
IP_GOOD = '8.8.8.8'
IP_BAD = '192.0.2.0'


def test_get_node_metrics_pos():
    ip = IP_GOOD
    metrics_ok = ping.get_node_metrics(ip)
    latency = metrics_ok['latency']
    downtime = metrics_ok['is_offline']
    print(metrics_ok)

    assert type(latency) is int
    assert latency >= 0
    assert type(downtime) is bool


def test_get_node_metrics_neg():
    ip = IP_BAD
    metrics_ok = ping.get_node_metrics(ip)
    latency = metrics_ok['latency']
    downtime = metrics_ok['is_offline']
    print(metrics_ok)

    assert latency == -1
    assert downtime is True
