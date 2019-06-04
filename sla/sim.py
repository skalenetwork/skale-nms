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

import random


def generate_node_metrics(false_downtime_coeff=0.015, min_latency=20, max_latency=210) -> dict:
    """Generates random node metrics (downtime and latency)"""

    is_dead = random.random() > false_downtime_coeff
    latency = float(random.randint(min_latency, max_latency))
    return {'is_dead': is_dead, 'latency': latency}


if __name__ == '__main__':

    for i in range(10):
        print(generate_node_metrics())
