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
from datetime import datetime

import skale.utils.helper as helper

from agent import base_agent
from agent.helper import init_skale
from database import db
from sla import ping


class Validator(base_agent.BaseAgent):

    def __init__(self, skale, node_id=None):
        super().__init__(skale, node_id)
        self.nodes = []
        self.nodes_for_report = []

    def get_validated_nodes(self, node_id: int = None, account: str = None) -> list:
        """
        Returns a list of nodes to validate - node node_id, report date, ip address
        """

        if node_id is None:
            node_id = self.id
        if account is None:
            account = self.account
        account = self.skale.web3.toChecksumAddress(account)

        try:
            nodes_in_bytes_array = self.skale.validators_data.get_validated_array(node_id, account)
            print(nodes_in_bytes_array)
        except Exception as err:
            self.logger.error(f"Cannot get a list of nodes for validating: {str(err)}", exc_info=True)
            raise

        nodes = []
        for node_in_bytes in nodes_in_bytes_array:
            node_id = int.from_bytes(node_in_bytes[:14], byteorder='big')
            report_date = int.from_bytes(node_in_bytes[14:28], byteorder='big')
            node_ip = socket.inet_ntoa(node_in_bytes[28:])

            nodes.append({'id': node_id, 'ip': node_ip, 'rep_date': report_date})
        self.nodes = nodes
        return self.nodes

    def show_validated_nodes(self):
        self.logger.info(f"Number of nodes to validate: {len(self.nodes)}")
        for node in self.nodes:
            self.logger.debug(f"id: {node['id']}, ip: {node['ip']}")

    def validate_nodes(self):

        self.logger.info("Validating nodes:")
        if len(self.nodes) == 0:
            self.logger.info(f"- No nodes to validate")
        else:
            self.logger.info(f"Number of nodes for validating: {len(self.nodes)}")
            self.logger.info(f"Nodes for validating: {self.nodes}")

        self.nodes_for_report = []
        for node in self.nodes:
            # metrics = ping.get_node_metrics(node['ip'])  # TODO: uncomment when we have real nodes
            # metrics = sim.generate_node_metrics()  # use to simulate metrics
            metrics = ping.get_node_metrics(
                '8.8.8.8')  # ping Google while we have no real nodes # TODO: remove when we have real nodes
            db.save_to_db(self.id, node['id'], metrics['is_alive'], metrics['latency'])

            rep_date = datetime.utcfromtimestamp(node['rep_date'])
            now = datetime.utcnow()
            self.logger.debug(f"now date: {now}")
            self.logger.debug(f"report date: {rep_date}")
            if rep_date < now:
                self.nodes_for_report.append({'id': node['id'], 'rep_date': node['rep_date']})

    def send_verdicts(self):
        self.logger.info("Sending Verdicts:")
        if len(self.nodes_for_report) == 0:
            self.logger.info(f"- No nodes for sending verdicts about")
        else:
            self.logger.info(f"Number of nodes for report: {len(self.nodes_for_report)}")
            self.logger.info(f"Nodes for report: {self.nodes_for_report}")
        for node in self.nodes_for_report:
            metrics = db.get_month_metrics_for_node(self.id, node['id'], node['rep_date'])

            self.logger.info(f"Sending verdict for node #{node['id']}")
            self.logger.info(f'wallet = {self.local_wallet["address"]}    {self.local_wallet["private_key"]}')
            try:
                self.skale.web3.eth.enable_unaudited_features()
                res = self.skale.manager.send_verdict(self.id, node['id'], metrics['downtime'],
                                                      int(metrics['latency']), self.local_wallet)
                receipt = helper.await_receipt(self.skale.web3, res['tx'])
                self.logger.debug('--- receipt ---')
                self.logger.debug(receipt)
                if receipt['status'] == 1:
                    self.logger.info("The verdict was successfully sent")
                if receipt['status'] == 0:
                    self.logger.info("The verdict wasn't sent - transaction failed")
            except Exception as err:
                self.logger.error(f"Failed send verdict for the node #{node['id']}. Error: {str(err)}", exc_info=True)
                # raise
                break

    def job(self) -> None:
        """
        Periodic job
        """
        self.logger.debug("___________________________")
        self.logger.debug("New periodic job started...")

        try:
            self.get_validated_nodes()
        except Exception as err:
            self.logger.error(f"Failed to get list of validated nodes {str(err)}")
            self.nodes = []

        self.validate_nodes()

        self.send_verdicts()
        self.logger.debug("Periodic job finished...")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        is_debug_mode = True
        _node_id = int(sys.argv[1])
    else:
        _node_id = None

    _skale = init_skale()
    print(_skale.nodes_data.get_active_node_ids())
    validator = Validator(_skale, _node_id)
    validator.run()
