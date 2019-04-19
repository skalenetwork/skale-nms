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

#########################################
# Context manager for a database (MySQL)
#########################################

import os

from dotenv import load_dotenv
from peewee import BooleanField, DateTimeField, IntegerField, Model, MySQLDatabase, fn

dotenv_path = '.env'
load_dotenv(dotenv_path)

user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
db_name = 'test'
host = '127.0.0.1'

dbhandle = MySQLDatabase(
    db_name, user=user,
    password=password,
    host=host
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


def save_metrics_to_db(my_id, node_id, is_alive, latency):
    """ Save metrics (downtime and latency) to database"""
    report = Report(my_id=my_id,
                    node_id=node_id,
                    is_alive=is_alive,
                    latency=latency)
    report.save()


def get_month_metrics_for_node(my_id, node_id, start_date, end_date) -> dict:
    """ Returns a dict with aggregated month metrics - downtime and latency"""

    results = Report.select(fn.SUM(Report.is_alive).alias('sum'),
                            fn.AVG(Report.latency).alias('avg')).where((
                                Report.my_id == my_id) & (Report.node_id == node_id) & (
                                Report.stamp >= start_date) & (Report.stamp <= end_date))

    return {'downtime': results[0].sum, 'latency': results[0].avg}


def clear_all_reports():
    nrows = Report.delete().execute()
    print(f'{nrows} records deleted')
