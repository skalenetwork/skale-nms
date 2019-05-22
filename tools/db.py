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


import os

from dotenv import load_dotenv
from peewee import BooleanField, DateTimeField, IntegerField, Model, MySQLDatabase, CharField, fn

from tools.helper import TEST_DATA_DIR_PATH

ENV_FILE = ".env"
DOTENV_PATH = os.path.join(TEST_DATA_DIR_PATH, ENV_FILE)

load_dotenv(DOTENV_PATH)

user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
db_name = 'db_skale'
host = '127.0.0.1'
port = 3307

dbhandle = MySQLDatabase(
    db_name, user=user,
    password=password,
    host=host,
    port=port
)


class BaseModel(Model):
    class Meta:
        database = dbhandle


class Report(BaseModel):
    my_id = IntegerField()
    node_id = IntegerField()
    is_alive = BooleanField()
    latency = IntegerField()
    stamp = DateTimeField()


class Bounty(BaseModel):
    my_id = IntegerField()
    tx_dt = DateTimeField()
    bounty = IntegerField()
    downtime = IntegerField()
    latency = IntegerField()
    gas = IntegerField()
    stamp = DateTimeField()
    tx_hash = CharField()


def save_metrics_to_db(my_id, node_id, is_alive, latency):
    """ Save metrics (downtime and latency) to database"""
    report = Report(my_id=my_id,
                    node_id=node_id,
                    is_alive=is_alive,
                    latency=latency)
    report.save()


def save_events(tx_dt, tx_hash, my_id, bounty, latency, downtime, gas):
    """ Save bounty events data to database"""
    data = Bounty(my_id=my_id,
                  tx_dt=tx_dt,
                  bounty=bounty,
                  downtime=downtime,
                  latency=latency,
                  gas=gas,
                  tx_hash=tx_hash)

    data.save()


def get_month_metrics_for_node(my_id, node_id, start_date, end_date) -> dict:
    """ Returns a dict with aggregated month metrics - downtime and latency"""

    results = Report.select(fn.SUM(Report.is_alive).alias('sum'),
                            fn.AVG(Report.latency).alias('avg')).where((
                                Report.my_id == my_id) & (Report.node_id == node_id) & (
                                Report.stamp >= start_date) & (Report.stamp <= end_date))

    downtime = int(results[0].sum) if results[0].sum is not None else 0
    latency = results[0].avg if results[0].avg is not None else 0
    return {'downtime': downtime, 'latency': latency}


def clear_all_reports():
    nrows = Report.delete().execute()
    print(f'{nrows} records deleted')
