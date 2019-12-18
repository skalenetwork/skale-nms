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


from peewee import BooleanField, CharField, CompositeKey, DateTimeField, IntegerField, Model, \
    MySQLDatabase, fn

from tools.configs.db import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

print(f'DB HOST = {DB_HOST}')


dbhandle = MySQLDatabase(
    DB_NAME, user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


class BaseModel(Model):
    class Meta:
        database = dbhandle


class Report(BaseModel):
    my_id = IntegerField()
    target_id = IntegerField()
    is_offline = BooleanField()
    latency = IntegerField()
    stamp = DateTimeField()


class BountyEvent(BaseModel):
    my_id = IntegerField()
    tx_dt = DateTimeField()
    tx_hash = CharField()
    block_number = IntegerField()
    bounty = CharField()
    downtime = IntegerField()
    latency = IntegerField()
    gas_used = IntegerField()

    class Meta:
        db_table = 'bounty_event'


class ReportEvent(BaseModel):
    my_id = IntegerField()
    target_id = IntegerField()
    tx_dt = DateTimeField()
    tx_hash = CharField()
    downtime = IntegerField()
    latency = IntegerField()
    gas_used = IntegerField()

    class Meta:
        db_table = 'report_event'


class BountyStats(BaseModel):
    tx_hash = CharField()
    eth_balance_before = CharField()
    eth_balance = CharField()
    skl_balance_before = CharField()
    skl_balance = CharField()

    class Meta:
        db_table = 'bounty_stats'
        primary_key = CompositeKey('tx_hash')


@dbhandle.connection_context()
def save_metrics_to_db(my_id, target_id, is_offline, latency):
    """ Save metrics (downtime and latency) to database"""
    report = Report(my_id=my_id,
                    target_id=target_id,
                    is_offline=is_offline,
                    latency=latency)
    report.save()


@dbhandle.connection_context()
def save_bounty_event(tx_dt, tx_hash, block_number, my_id, bounty, downtime, latency, gas_used):
    """ Save bounty events data to database"""
    data = BountyEvent(my_id=my_id,
                       tx_dt=tx_dt,
                       bounty=bounty,
                       downtime=downtime,
                       latency=latency,
                       gas_used=gas_used,
                       tx_hash=tx_hash,
                       block_number=block_number)

    data.save()


@dbhandle.connection_context()
def save_report_event(tx_dt, tx_hash, my_id, target_id, downtime, latency, gas_used):
    """ Save bounty events data to database"""
    data = ReportEvent(my_id=my_id,
                       target_id=target_id,
                       tx_dt=tx_dt,
                       downtime=downtime,
                       latency=latency,
                       gas_used=gas_used,
                       tx_hash=tx_hash)

    data.save()


@dbhandle.connection_context()
def save_bounty_stats(
        tx_hash,
        eth_bal_before,
        skl_bal_before,
        eth_bal,
        skl_bal):
    """ Save bounty receipt data to database"""
    data = BountyStats(tx_hash=tx_hash,
                       eth_balance_before=eth_bal_before,
                       skl_balance_before=skl_bal_before,
                       eth_balance=eth_bal,
                       skl_balance=skl_bal
                       )
    data.save(force_insert=True)


@dbhandle.connection_context()
def get_month_metrics_for_node(my_id, target_id, start_date, end_date) -> dict:
    """ Returns a dict with aggregated month metrics - downtime and latency"""

    downtime_results = Report.select(
        fn.SUM(
            Report.is_offline).alias('sum')).where(
        (Report.my_id == my_id) & (
                Report.target_id == target_id) & (
            Report.stamp >= start_date) & (
            Report.stamp <= end_date))

    latency_results = Report.select(
        fn.AVG(
            Report.latency).alias('avg')).where(
        (Report.my_id == my_id) & (
                Report.target_id == target_id) & (
            Report.stamp >= start_date) & (
            Report.stamp <= end_date) & (
            Report.latency >= 0))
    if downtime_results[0].sum is None:
        print(f'Sum result from db is None')
    downtime = int(
        downtime_results[0].sum) if downtime_results[0].sum is not None else 0
    latency = latency_results[0].avg if latency_results[0].avg is not None else 0
    return {'downtime': downtime, 'latency': latency}


@dbhandle.connection_context()
def clear_all_reports():
    nrows = Report.delete().execute()
    print(f'{nrows} records deleted')


@dbhandle.connection_context()
def clear_all_bounty_receipts():
    nrows = BountyStats.delete().execute()
    print(f'{nrows} records deleted')


@dbhandle.connection_context()
def get_count_of_bounty_receipt_records():
    return BountyStats.select().count()


@dbhandle.connection_context()
def get_count_of_report_records():
    return Report.select().count()


@dbhandle.connection_context()
def get_bounty_max_block_number():
    return BountyEvent.select(fn.MAX(BountyEvent.block_number)).scalar()
