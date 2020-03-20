#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
#
#   Copyright (C) 2019-2020 SKALE Labs
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

"""
SLA agent runs on every node of SKALE network, periodically gets a list of nodes to validate
from SC, checks its health metrics and sends transactions with average metrics to CS when it's time
to send it
"""
from skale.utils.web3_utils import TransactionFailedError
import socket
import sys
import threading
import time
from datetime import datetime

import schedule
from skale.manager_client import spawn_skale_lib

from sla.metrics import get_metrics_for_node, get_ping_node_results
from tools import base_agent, db
from tools.configs import GOOD_IP, LONG_DOUBLE_LINE, LONG_LINE, MONITOR_PERIOD, REPORT_PERIOD
from tools.helper import run_agent


class Monitor(base_agent.BaseAgent):

    def __init__(self, skale, node_id=None):
        super().__init__(skale, node_id)
        self.nodes = self.get_validated_nodes(skale)
        self.reward_period = self.skale.constants_holder.get_reward_period()

    def get_validated_nodes(self, skale) -> list:
        """Returns a list of nodes to validate - node node_id, report date, ip address"""

        # get raw binary data list from SKALE Manager SC
        try:
            nodes_in_bytes_array = skale.monitors_data.get_checked_array(self.id)
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

    def validate_nodes(self, skale, nodes):
        """Validate nodes and returns a list of nodes to be reported"""
        self.logger.info(LONG_LINE)
        if len(nodes) == 0:
            self.logger.info(f'No nodes to be monitored')
        else:
            self.logger.info(f'Number of nodes for monitoring: {len(nodes)}')
            self.logger.info(f'The nodes to be monitored : {nodes}')

        for node in nodes:
            if not get_ping_node_results(GOOD_IP)['is_offline']:
                metrics = get_metrics_for_node(skale, node, self.is_test_mode)
                self.logger.info(f'Received metrics from node ID = {node["id"]}: {metrics}')
                try:
                    db.save_metrics_to_db(self.id, node['id'],
                                          metrics['is_offline'], metrics['latency'])
                except Exception as err:
                    self.logger.error(f'Couldn\'t save metrics to database - '
                                      f'is mysql container running? {err}')
            else:
                self.logger.error(f'Couldn\'t ping 8.8.8.8 - skipping monitoring node {node["id"]}')

    def get_reported_nodes(self, nodes) -> list:
        """Returns a list of nodes to be reported"""

        last_block_number = self.skale.web3.eth.blockNumber
        block_data = self.skale.web3.eth.getBlock(last_block_number)
        block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
        self.logger.info(f'Timestamp of current block: {block_timestamp}')

        nodes_for_report = []
        for node in nodes:
            # Check report date of current validated node
            rep_date = datetime.utcfromtimestamp(node['rep_date'])
            self.logger.info(f'Report date for node id={node["id"]}: {rep_date}')
            if rep_date < block_timestamp:
                # Forming a list of nodes that already need to be reported
                nodes_for_report.append({'id': node['id'], 'rep_date': node['rep_date']})
        return nodes_for_report

    def send_reports(self, nodes_for_report):
        """Send reports for every node from nodes_for_report"""

        self.logger.info(LONG_LINE)
        err_status = 0

        ids = []
        latencies = []
        downtimes = []
        for node in nodes_for_report:
            start_date = node['rep_date'] - self.reward_period
            try:
                self.logger.info(f'Getting month metrics for node id = {node["id"]}:')
                self.logger.info(f'Start date: {datetime.utcfromtimestamp(start_date)}')
                self.logger.info(f'End date: {datetime.utcfromtimestamp(node["rep_date"])}')
                metrics = db.get_month_metrics_for_node(self.id, node['id'],
                                                        datetime.utcfromtimestamp(start_date),
                                                        datetime.utcfromtimestamp(node['rep_date']))
                self.logger.info(f'Epoch metrics for node id = {node["id"]}: {metrics}')
                ids.append(node['id'])
                downtimes.append(metrics['downtime'])
                latencies.append(metrics['latency'])
            except Exception as err:
                self.logger.error(f'Failed getting month metrics from db: {err}')
                self.logger.info(f'Report on node id = {node["id"]} cannot be sent!')
        if len(ids) == len(downtimes) == len(latencies) and len(ids) != 0:
            try:
                res_tx = self.skale.manager.send_verdicts(self.id, ids, downtimes,
                                                          latencies, wait_for=True)
                tx_hash = res_tx.receipt['transactionHash'].hex()
                if res_tx.receipt['status'] == 1:
                    self.logger.info('The report was successfully sent')
                    h_receipt = self.skale.monitors.contract.events.VerdictWasSent(
                    ).processReceipt(res_tx.receipt)
                    self.logger.info(LONG_LINE)
                    self.logger.info(h_receipt)
                    args = h_receipt[0]['args']
                    try:
                        db.save_report_event(datetime.utcfromtimestamp(args['time']),
                                             str(tx_hash), args['fromMonitorIndex'],
                                             args['toNodeIndex'], args['downtime'],
                                             args['latency'], res_tx.receipt["gasUsed"])
                    except Exception as err:
                        self.logger.exception(f'Failed to save report event data. {err}')
                if res_tx.receipt['status'] == 0:
                    self.logger.info('The report was not sent - transaction failed')
                    err_status = 1
                self.logger.debug(f'Receipt: {res_tx.receipt}')
                self.logger.info(LONG_DOUBLE_LINE)
            except TransactionFailedError as err:
                self.logger.info(f'An error occurred while sending report. Error: {err}')
                raise
            except Exception as err:
                self.logger.exception(f'An error occurred while sending report. Error: {err}')

        return err_status

    def monitor_job(self) -> None:
        """
        Periodic job for monitoring nodes
        """
        self.logger.info('New monitor job started...')
        skale = spawn_skale_lib(self.skale)
        try:
            self.nodes = self.get_validated_nodes(skale)
        except Exception as err:
            self.logger.exception(f'Failed to get list of monitored nodes. Error: {err}')
            self.logger.info('Monitoring nodes from previous job list')

        self.validate_nodes(skale, self.nodes)

        self.logger.info('Monitor job finished...')

    def report_job(self) -> None:
        """
        Periodic job for sending reports
        """
        self.logger.info('New report job started...')
        nodes_for_report = self.get_reported_nodes(self.nodes)

        if len(nodes_for_report) > 0:
            self.logger.info(f'Number of nodes for reporting: {len(nodes_for_report)}')
            self.logger.info(f'The nodes to be reported on: {nodes_for_report}')
            self.send_reports(nodes_for_report)
        else:
            self.logger.info(f'- No nodes to be reported on')

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

    run_agent(sys.argv, Monitor)
