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

from datetime import datetime, timedelta

from tools import db


def setup_module(module):
    db.clear_all_reports()


def test_get_month_metrics():
    db.save_metrics_to_db(0, 1, 'true', 40)
    db.save_metrics_to_db(0, 1, 'true', 60)
    now = datetime.utcnow()
    data = db.get_month_metrics_for_node(0, 1, now - timedelta(minutes=1), now)
    print(data)
    assert data['latency'] == 50
    assert data['downtime'] == 2


def test_clear_all_reports():
    db.clear_all_reports()
    now = datetime.utcnow()
    data = db.get_month_metrics_for_node(0, 1, now - timedelta(minutes=1), now)
    print(data)
    assert data['latency'] == 0
    assert data['downtime'] == 0
