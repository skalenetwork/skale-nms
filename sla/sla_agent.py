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
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
SLA agent runs on every node of SKALE network, periodically gets a list of nodes to validate
from SC, checks its health metrics and sends transactions with average metrics to CS when it's time
to send it
"""

import os
import socket
import sys
import threading
import time
from datetime import datetime

import schedule
from filelock import FileLock, Timeout
from skale.utils.helper import await_receipt

from sla import ping
from tools import base_agent, db
from tools.configs import MONITOR_PERIOD, REPORT_PERIOD, GOOD_IP, LOCK_FILEPATH, LONG_DOUBLE_LINE, \
    LONG_LINE
from tools.helper import get_containers_healthcheck, init_skale


class Monitor(base_agent.BaseAgent):

    def __init__(self, skale, node_id=None):
        super().__init__(skale, node_id)
        self.nodes = self.get_validated_nodes()

    def get_validated_nodes(self) -> list:
        """Returns a list of nodes to validate - node node_id, report date, ip address"""

        account = self.skale.web3.toChecksumAddress(self.local_wallet['address'])

        # get raw binary data list from SKALE Manager SC
        try:
            nodes_in_bytes_array = self.skale.validators_data.get_validated_array(self.id, account)
        except Exception as err:
            self.logger.error(f'Cannot get a list of nodes for validating: {str(err)}',
                              exc_info=True)
            raise
        # extract  node id, report date and ip from binary
        nodes = []
        for node_in_bytes in nodes_in_bytes_array:
            node_id = int.from_bytes(node_in_bytes[:14], byteorder='big')
            report_date = int.from_bytes(node_in_bytes[14:28], byteorder='big')
            node_ip = socket.inet_ntoa(node_in_bytes[28:])

            nodes.append({'id': node_id, 'ip': node_ip, 'rep_date': report_date})
        return nodes

    def validate_nodes(self, nodes):
        """Validate nodes and returns a list of nodes to be reported"""
        self.logger.info(LONG_LINE)
        if len(nodes) == 0:
            self.logger.info(f'No nodes to be monitored')
        else:
            self.logger.info(f'Number of nodes for monitoring: {len(nodes)}')
            self.logger.info(f'The nodes to be monitored : {nodes}')

        for node in nodes:
            host = GOOD_IP if self.is_test_mode else node['ip']
            if os.system("ping -c 1 " + GOOD_IP + " > /dev/null") == 0:
                metrics = ping.get_node_metrics(host)
                # metrics = sim.generate_node_metrics()  # use to simulate metrics for some tests
                healthcheck = get_containers_healthcheck(host, self.is_test_mode)
                if healthcheck:
                    metrics['is_offline'] = True
                self.logger.info(f'Received metrics from node ID = {node["id"]}: {metrics}')
                db.save_metrics_to_db(self.id, node['id'],
                                      metrics['is_offline'], metrics['latency'])
            else:
                self.logger.error(f'Couldn\'t ping 8.8.8.8 - skipping monitoring node {node["id"]}')

    def get_reported_nodes(self, nodes) -> list:
        """Returns a list of nodes to be reported"""
        nodes_for_report = []
        for node in nodes:
            # Check report date of current validated node
            rep_date = datetime.utcfromtimestamp(node['rep_date'])
            now = datetime.utcnow()
            self.logger.debug(f'now date: {now}')
            self.logger.debug(f'report date: {rep_date}')
            if rep_date < now:
                # Forming a list of nodes that already need to be reported
                nodes_for_report.append({'id': node['id'], 'rep_date': node['rep_date']})
        return nodes_for_report

    def send_reports(self, nodes_for_report):
        """Send reports for every node from nodes_for_report"""

        self.logger.info(LONG_LINE)
        if len(nodes_for_report) == 0:
            self.logger.info(f'- No nodes to be reported on')
        else:
            self.logger.info(f'Number of nodes for reporting: {len(nodes_for_report)}')
            self.logger.info(f'The nodes to be reported on: {nodes_for_report}')
        err_status = 0

        ids = []
        latencies = []
        downtimes = []

        for node in nodes_for_report:
            reward_period = self.skale.validators_data.get_reward_period()
            start_date = node['rep_date'] - reward_period
            try:
                metrics = db.get_month_metrics_for_node(self.id, node['id'],
                                                        datetime.utcfromtimestamp(start_date),
                                                        datetime.utcfromtimestamp(node['rep_date']))
                self.logger.info(f'Epoch metrics: {metrics}')
                ids.append(node['id'])
                downtimes.append(metrics['downtime'])
                latencies.append(metrics['latency'])
            except Exception as err:
                self.logger.exception(f'Failed getting month metrics from db: {err}')

        lock = FileLock(LOCK_FILEPATH, timeout=1)
        self.logger.debug('Acquiring lock')
        try:
            with lock.acquire():
                res = self.skale.manager.send_verdicts(self.id, ids, downtimes,
                                                       latencies, self.local_wallet)
                receipt = await_receipt(self.skale.web3, res['tx'], retries=30, timeout=6)
                if receipt['status'] == 1:
                    self.logger.info('The report was successfully sent')
                    h_receipt = self.skale.validators.contract.events.VerdictWasSent(
                    ).processReceipt(receipt)
                    self.logger.info(LONG_LINE)
                    self.logger.info(h_receipt)
                    args = h_receipt[0]['args']
                    db.save_report_event(datetime.utcfromtimestamp(args['time']),
                                         str(res['tx'].hex()), args['fromValidatorIndex'],
                                         args['toNodeIndex'], args['downtime'], args['latency'],
                                         receipt["gasUsed"])
                if receipt['status'] == 0:
                    self.logger.info('The report was not sent - transaction failed')
                    err_status = 1
                self.logger.debug(f'Receipt: {receipt}')
                self.logger.info(LONG_DOUBLE_LINE)
        except Timeout:
            self.logger.info('Another agent currently holds the lock')
        except Exception as err:
            self.logger.error(f'Failed send report on the node #{node["id"]}. Error: '
                              f'{str(err)}', exc_info=True)

        return err_status

    def monitor_job(self) -> None:
        """
        Periodic job for monitoring nodes
        """
        self.logger.info('New monitor job started...')
        try:
            self.nodes = self.get_validated_nodes()
        except Exception as err:
            self.logger.error(f'Failed to get list of monitored nodes {str(err)}')

        self.validate_nodes(self.nodes)

        self.logger.info('Monitor job finished...')

    def report_job(self) -> None:
        """
        Periodic job for sending reports
        """
        self.logger.info('New report job started...')
        nodes_for_report = self.get_reported_nodes(self.nodes)

        if len(nodes_for_report) > 0:
            self.send_reports(nodes_for_report)

        self.logger.info('Report job finished...')

    def run_threaded(self, job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()

    def run(self) -> None:
        """Starts agent"""
        self.logger.debug(f'{self.agent_name} started')
        self.run_threaded(self.monitor_job)
        self.run_threaded(self.report_job)
        schedule.every(MONITOR_PERIOD).minutes.do(self.run_threaded, self.monitor_job)
        schedule.every(REPORT_PERIOD).minutes.do(self.run_threaded, self.report_job)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1].isdecimal():
        node_id = int(sys.argv[1])
    else:
        node_id = None

    skale = init_skale()
    monitor = Monitor(skale, node_id)
    monitor.run()
