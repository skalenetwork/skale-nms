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
"""
SLA agent runs on every node of Skale network, periodically gets a list of nodes to validate from SC,
checks its health metrics and sends transactions with average metrics to CS when it's time to send it
"""

import socket
import sys
from datetime import datetime, timedelta

from skale.utils.helper import await_receipt

from database import db
from sla import ping
from tools import base_agent
from tools.helper import init_skale


class Validator(base_agent.BaseAgent):

    def __init__(self, skale, node_id=None):
        super().__init__(skale, node_id)

    def get_validated_nodes(self) -> list:
        """Returns a list of nodes to validate - node node_id, report date, ip address"""

        account = self.skale.web3.toChecksumAddress(self.local_wallet['address'])

        # get raw binary data list from Skale Manager SC
        try:
            nodes_in_bytes_array = self.skale.validators_data.get_validated_array(self.id, account)
        except Exception as err:
            self.logger.error(f'Cannot get a list of nodes for validating: {str(err)}', exc_info=True)
            raise
        # extract  node id, report date and ip from binary
        nodes = []
        for node_in_bytes in nodes_in_bytes_array:
            node_id = int.from_bytes(node_in_bytes[:14], byteorder='big')
            report_date = int.from_bytes(node_in_bytes[14:28], byteorder='big')
            node_ip = socket.inet_ntoa(node_in_bytes[28:])

            nodes.append({'id': node_id, 'ip': node_ip, 'rep_date': report_date})
        return nodes

    def show_validated_nodes(self, nodes):
        self.logger.info(f'Number of nodes to validate: {len(nodes)}')
        for node in nodes:
            self.logger.debug(f'id: {node["id"]}, ip: {node["ip"]}')

    def validate_and_get_reported_nodes(self, nodes) -> list:
        """Validate nodes and returns a list of nodes to be reported"""

        self.logger.info('Validating nodes:')
        if len(nodes) == 0:
            self.logger.info(f'- No nodes to validate')
        else:
            self.logger.info(f'Number of nodes for validating: {len(nodes)}')
            self.logger.info(f'Nodes for validating: {nodes}')

        nodes_for_report = []
        for node in nodes:
            test_ip = '8.8.8.8'
            host = test_ip if self.is_test_mode else node['ip']
            metrics = ping.get_node_metrics(host)
            # metrics = sim.generate_node_metrics()  # use to simulate metrics for some tests
            db.save_metrics_to_db(self.id, node['id'], metrics['is_alive'], metrics['latency'])

            # Check report date of current validated node
            rep_date = datetime.utcfromtimestamp(node['rep_date'])
            now = datetime.utcnow()
            self.logger.debug(f'now date: {now}')
            self.logger.debug(f'report date: {rep_date}')
            if rep_date < now:
                # Forming a list of nodes that already need to be reported
                nodes_for_report.append({'id': node['id'], 'rep_date': node['rep_date']})
        return nodes_for_report

    def send_verdicts(self, nodes_for_report):
        """Send verdicts for every node from nodes_for_report"""

        self.logger.info('Sending Verdicts:')
        if len(nodes_for_report) == 0:
            self.logger.info(f'- No nodes for sending verdicts about')
        else:
            self.logger.info(f'Number of nodes for report: {len(nodes_for_report)}')
            self.logger.info(f'Nodes for report: {nodes_for_report}')
        for node in nodes_for_report:
            reward_period = self.skale.validators_data.get_reward_period()
            start_date = node['rep_date'] - timedelta(seconds=reward_period)
            metrics = db.get_month_metrics_for_node(self.id, node['id'], start_date, node['rep_date'])

            self.logger.info(f'Sending verdict for node #{node["id"]}')
            self.logger.debug(f'wallet = {self.local_wallet["address"]}    {self.local_wallet["private_key"]}')
            try:
                res = self.skale.manager.send_verdict(self.id, node['id'], metrics['downtime'],
                                                      int(metrics['latency']), self.local_wallet)
            except Exception as err:
                self.logger.error(f'Failed send verdict for the node #{node["id"]}. Error: {str(err)}', exc_info=True)
                break

            receipt = await_receipt(self.skale.web3, res['tx'])
            if receipt['status'] == 1:
                self.logger.info('The verdict was successfully sent')
            if receipt['status'] == 0:
                self.logger.info('The verdict was not sent - transaction failed')
            self.logger.info(f'Receipt: {receipt}')

    def job(self) -> None:
        """
        Periodic job
        """
        self.logger.debug('___________________________')
        self.logger.debug('New periodic job started...')
        try:
            nodes = self.get_validated_nodes()
        except Exception as err:
            self.logger.error(f'Failed to get list of validated nodes {str(err)}')
            nodes = []

        nodes_for_report = self.validate_and_get_reported_nodes(nodes)

        self.send_verdicts(nodes_for_report)
        self.logger.debug('Periodic job finished...')


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1].isdecimal():
        node_id = int(sys.argv[1])
    else:
        node_id = None

    skale = init_skale()
    validator = Validator(skale, node_id)
    validator.run()
