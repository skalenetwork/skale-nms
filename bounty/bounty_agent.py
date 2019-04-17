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
Bounty agent runs on every node of Skale network and sends transactions
to CS with request to get reward for validation work when it's time to get it
"""
import sys
from datetime import datetime

import skale.utils.helper as Helper

from tools import base_agent
from tools.helper import init_skale


class BountyCollector(base_agent.BaseAgent):

    def get_reward_date(self):
        reward_period = skale.validators_data.get_reward_period()
        reward_date = self.skale.nodes_data.get(self.id)['last_reward_date'] + reward_period
        return datetime.utcfromtimestamp(reward_date)

    def get_bounty(self):
        address = self.local_wallet['address']
        self.logger.debug(f'ETH balance: {self.skale.web3.eth.getBalance(address)}')
        self.logger.debug(f'SKL balance: {self.skale.token.contract.functions.balanceOf(address).call()}')
        self.logger.info('--- Getting Bounty ---')
        try:
            res = self.skale.manager.get_bounty(self.id, self.local_wallet)
        except Exception as err:
            self.logger.error(f'Failed getting bounty tx: {err}')
            # TODO: notify Skale Admin
            raise
        self.logger.debug('Waiting for receipt of tx...')
        receipt = Helper.await_receipt(self.skale.web3, res['tx'])
        if receipt['status'] == 1:
            self.logger.info('The bounty was successfully received')
        if receipt['status'] == 0:
            self.logger.info('The bounty was not received - transaction failed')
            # TODO: notify Skale Admin
        self.logger.info(f'Receipt: {receipt}')
        self.logger.debug(f'ETH balance: {self.skale.web3.eth.getBalance(address)}')
        self.logger.debug(f'SKL balance: {self.skale.token.contract.functions.balanceOf(address).call()}')
        self.logger.debug('Waiting for the next periodic check')

    def job(self) -> None:
        """ Periodic job"""
        utc_now = datetime.utcnow()
        self.logger.debug('Checking my reward date...')
        self.logger.debug(f'Now (UTC): {utc_now}')

        try:
            reward_date = self.get_reward_date()
        except Exception as err:
            self.logger.error(f'Cannot get reward date: {err}')
            # TODO: notify Skale Admin
            return

        self.logger.debug(f'Next reward date: {reward_date}')

        if utc_now >= reward_date:
            self.get_bounty()


if __name__ == '__main__':

    if len(sys.argv) > 1:
        is_debug_mode = True
        _node_id = int(sys.argv[1])
    else:
        _node_id = None
    skale = init_skale()
    bounty_collector = BountyCollector(skale, _node_id)
    bounty_collector.run()
