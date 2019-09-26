#   -*- coding: utf-8 -*-
#
#   This file is part of SLA
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

"""
Bounty agent runs on every node of Skale network and sends transactions
to CS with request to get reward for validation work when it's time to get it
"""
import sys
from datetime import datetime

import skale.utils.helper as Helper
from filelock import FileLock, Timeout

from tools import base_agent, db
from tools.config import LONG_LINE
from tools.helper import get_lock_filepath, init_skale


class BountyCollector(base_agent.BaseAgent):

    def get_reward_date(self):
        reward_period = self.skale.validators_data.get_reward_period()
        reward_date = self.skale.nodes_data.get(self.id)['last_reward_date'] + reward_period
        return datetime.utcfromtimestamp(reward_date)

    def get_bounty(self):
        address = self.local_wallet['address']
        eth_bal_before = self.skale.web3.eth.getBalance(address)
        skl_bal_before = self.skale.token.get_balance(address)
        self.logger.debug(f'ETH balance: {eth_bal_before}')
        self.logger.debug(f'SKL balance: {skl_bal_before}')
        self.logger.info('--- Getting Bounty ---')
        lock = FileLock(get_lock_filepath(), timeout=1)
        self.logger.debug('Acquiring lock')
        try:
            with lock.acquire():
                res = self.skale.manager.get_bounty(self.id, self.local_wallet)
                receipt = Helper.await_receipt(self.skale.web3, res['tx'], retries=30, timeout=6)
        except Timeout:
            self.logger.info('Another agent currently holds the lock')
            return 2
        except Exception as err:
            self.logger.error(f'Failed getting bounty tx: {err}')
            # TODO: notify Skale Admin
            raise
        self.logger.debug('Waiting for receipt of tx...')

        tx_hash = receipt["transactionHash"].hex()

        if receipt['status'] == 1:
            self.logger.info('The bounty was successfully received')
            h_receipt = self.skale.manager.contract.events.BountyGot().processReceipt(receipt)
            self.logger.info(LONG_LINE)
            self.logger.info(h_receipt)
            self.logger.info(LONG_LINE)
            args = h_receipt[0]['args']
            db.save_bounty_event(datetime.utcfromtimestamp(args['time']), str(tx_hash),
                                 args['nodeIndex'], args['bounty'],
                                 args['averageLatency'], args['averageDowntime'],
                                 receipt["gasUsed"])
        if receipt['status'] == 0:
            self.logger.info('The bounty was not received - transaction failed')
            # TODO: notify Skale Admin
        self.logger.debug(f'Receipt: {receipt}')

        eth_bal = self.skale.web3.eth.getBalance(address)
        skl_bal = self.skale.token.get_balance(address)
        self.logger.debug(f'transactionHash: {tx_hash}')
        self.logger.info(f'ETH balance: {eth_bal}')
        self.logger.info(f'SKL balance: {skl_bal}')
        self.logger.debug(f'ETH difference: {eth_bal - eth_bal_before}')

        db.save_bounty_stats(tx_hash, eth_bal_before, skl_bal_before, eth_bal, skl_bal)
        self.logger.debug('Waiting for the next periodic check')
        return receipt['status']

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
            try:
                self.get_bounty()
            except Exception as err:
                self.logger.error(f'Cannot get bounty: {err}')
                raise


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1].isdecimal():
        node_id = int(sys.argv[1])
    else:
        node_id = None

    skale = init_skale()
    bounty_collector = BountyCollector(skale, node_id)
    bounty_collector.run()
