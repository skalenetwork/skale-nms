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

from agent import base_agent
from agent.helper import init_skale


class BountyCollector(base_agent.BaseAgent):

    def __init__(self, skale, node_id=None):
        super().__init__(skale, node_id)
        self.reward_date = 0
        self.is_reward_time = False

    def update_reward_date(self):
        reward_period = skale.validators_data.get_reward_period()
        try:
            self.reward_date = self.skale.nodes_data.get(
                self.id)['last_reward_date'] + reward_period
        except Exception as err:
            self.logger.exception('Error: ', err)
            raise

    def job(self) -> None:
        """ Periodic job"""
        self.logger.debug("Checking my reward date...")
        utcnow = datetime.utcnow()
        self.logger.debug(f"Now (UTC): {utcnow}")
        try:
            self.update_reward_date()
        except Exception as err:
            self.logger.error(f"Cannot get reward date {err}")
            return 1

        reward_date = datetime.utcfromtimestamp(self.reward_date)
        self.logger.debug(f"Next reward date: {reward_date}")

        if utcnow >= reward_date:

            address = self.local_wallet['address']
            self.logger.debug(
                f"ETH balance before getting bounty: {self.skale.web3.eth.getBalance(address)}"
            )
            self.logger.debug(
                f"SKL balance before getting bounty: {self.skale.token.contract.functions.balanceOf(address).call()}"
            )
            self.logger.info("--- Getting Bounty ---")
            self.skale.web3.eth.enable_unaudited_features()
            res = self.skale.manager.get_bounty(self.id, self.local_wallet)
            self.logger.debug("Waiting for receipt of tx...")
            receipt = Helper.await_receipt(self.skale.web3, res['tx'])
            self.logger.debug(f"Receipt: {receipt}")
            if receipt['status'] == 1:
                self.logger.info("The bounty was successfully received")
            print(receipt)
            print('+++++++++++')
            print(len(receipt['transactionHash']))

            if receipt['status'] == 0:
                self.logger.info(
                    "The bounty wasn't received - transaction failed")
            self.logger.debug(
                f"ETH balance after getting bounty: {self.skale.web3.eth.getBalance(address)}"
            )
            self.logger.debug(
                f"SKL balance after getting bounty: {self.skale.token.contract.functions.balanceOf(address).call()}"
            )
            self.logger.debug("-----------------------------------")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        is_debug_mode = True
        _node_id = int(sys.argv[1])
    else:
        _node_id = None
    skale = init_skale()
    bounty_collector = BountyCollector(skale, _node_id)
    bounty_collector.run()
