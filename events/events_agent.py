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

import sys
from datetime import datetime

from skale import EventListener

from tools import base_agent

EVENTS_POLL_INTERVAL = 5
skale = base_agent.skale


class EventCollector(base_agent.BaseAgent):

    def __init__(self, node_id=None):
        super().__init__(node_id)
        try:
            new_node_event = skale.nodes.contract.events.NodeCreated
            new_node_listener = EventListener(new_node_event, self.new_node_created_handler, EVENTS_POLL_INTERVAL)
            new_node_listener.run()

            # new_validators_event = skale.validators.contract.events.ValidatorsArray
            # new_validators_listener = EventListener(new_validators_event, self.new_validators_array_handler,
            #                                         EVENTS_POLL_INTERVAL)
            # new_validators_listener.run()

            send_verdict_event = skale.validators.contract.events.VerdictWasSent
            send_verdict_listener = EventListener(send_verdict_event, self.send_verdict_handler, EVENTS_POLL_INTERVAL)
            send_verdict_listener.run()

            get_bounty_event = skale.manager.contract.events.BountyGot
            get_bounty_listener = EventListener(get_bounty_event, self.get_bounty_handler, EVENTS_POLL_INTERVAL)
            get_bounty_listener.run()

        except Exception as err:
            self.logger.error(f'Cannot start Event Listener: {err}')

    def new_node_created_handler(self, event):
        self.logger.info('-----')
        self.logger.info(f'New Node Created event: {event}')

    def new_validators_array_handler(self, event):
        self.logger.info('-----')
        self.logger.debug(f'New Validators event: {event}')

    def send_verdict_handler(self, event):
        if event['args']['fromValidatorIndex'] == self.id:
            self.logger.info('-----')
            self.logger.info(f'sendVerdict event for a node {event["args"]["fromValidatorIndex"]}: {event}')
            self.logger.info(f'sendVerdict - time: {event["args"]["time"]}, '
                             f'gas used: {event["args"]["gasSpend"]}, '
                             f'is verdict received: {event["args"]["status"]}')

    def get_bounty_handler(self, event):
        if event['args']['nodeIndex'] == self.id:
            self.logger.info('-----')
            self.logger.info(f'event: {event}')
            self.logger.debug(f'getBounty event for a node {event["args"]["nodeIndex"]}: {event}')
            self.logger.info(f'getBounty - time: {event["args"]["time"]}, '
                             f'gas used: {event["args"]["gasSpend"]}, '
                             f'bounty: {event["args"]["bounty"]}, '
                             f'averageLatency: {event["args"]["averageLatency"]}, '
                             f'averageDowntime: {event["args"]["averageDowntime"]}')

            self.logger.info(f'getBounty transaction hash: {event["transactionHash"]}')
            tx_dt = datetime.utcfromtimestamp(event["args"]["time"])

            # db.save_events(tx_dt, event['transactionHash'].hex(),
            #                event['args']['nodeIndex'], float(event['args']['bounty']),
            #                event['args']['averageLatency'], event['args']['averageDowntime'],
            #                event['args']['gasSpend'], self.logger)

    def run(self) -> None:
        """
        Starts running event collector
        """
        while True:
            pass


if __name__ == '__main__':

    if len(sys.argv) > 1:
        is_debug_mode = True
        _node_id = int(sys.argv[1])
    else:
        _node_id = None

    event_collector = EventCollector(_node_id)
    event_collector.run()
