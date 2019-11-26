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

"""
Bounty agent runs on every node of SKALE network and sends transactions
to CS with request to get reward for validation work when it's time to get it
"""
import sys
import time
from datetime import datetime, timedelta

from filelock import FileLock, Timeout
from skale.utils.web3_utils import wait_receipt

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from tools import base_agent, db
from tools.configs import BLOCK_STEP_SIZE, LOCK_FILEPATH, LONG_DOUBLE_LINE, LONG_LINE, REWARD_DELAY
from tools.exceptions import GetBountyTxFailedException, IsNotTimeException
from tools.helper import find_block_for_tx_stamp, init_skale


class BountyCollector(base_agent.BaseAgent):

    def __init__(self, skale, node_id=None):
        super().__init__(skale, node_id)
        self.logger.info('Start checking logs on blockchain')
        start = time.time()
        try:
            self.collect_last_bounty_logs()
        except Exception as err:
            self.logger.error(f'Error occurred while checking logs from blockchain: {err} ')
        end = time.time()
        self.logger.info(f'Check completed. Execution time = {end - start}')
        self.scheduler = BackgroundScheduler(timezone='UTC')

    def get_reward_date(self):
        reward_period = self.skale.validators_data.get_reward_period()
        reward_date = self.skale.nodes_data.get(
            self.id)['last_reward_date'] + reward_period
        return datetime.utcfromtimestamp(reward_date) + timedelta(seconds=REWARD_DELAY)

    def collect_last_bounty_logs(self):
        start_date = datetime.utcfromtimestamp(self.skale.nodes_data.get(self.id)['start_date'])
        last_block_number_in_db = db.get_bounty_max_block_number()
        if last_block_number_in_db is None:
            start_block_number = find_block_for_tx_stamp(self.skale, start_date)
        else:
            start_block_number = last_block_number_in_db + 1
        count = 0
        while True:

            last_block_number = self.skale.web3.eth.blockNumber
            self.logger.debug(f'last block = {last_block_number}')
            end_chunk_block_number = start_block_number + BLOCK_STEP_SIZE - 1

            if end_chunk_block_number > last_block_number:
                end_chunk_block_number = last_block_number + 1
            event_filter = self.skale.manager.contract.events.BountyGot().createFilter(
                argument_filters={'nodeIndex': self.id},
                fromBlock=hex(start_block_number),
                toBlock=hex(end_chunk_block_number))
            logs = event_filter.get_all_entries()

            for log in logs:
                args = log['args']
                tx_block_number = log['blockNumber']
                block_data = self.skale.web3.eth.getBlock(tx_block_number)
                block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
                self.logger.debug(log)
                tx_hash = log['transactionHash'].hex()
                gas_used = self.skale.web3.eth.getTransactionReceipt(tx_hash)['gasUsed']
                db.save_bounty_event(block_timestamp, tx_hash,
                                     log['blockNumber'], args['nodeIndex'], args['bounty'],
                                     args['averageDowntime'], args['averageLatency'],
                                     gas_used)
                count += 1
            self.logger.debug(f'count = {count}')
            start_block_number = start_block_number + BLOCK_STEP_SIZE
            if end_chunk_block_number >= last_block_number:
                break

    def get_bounty(self):
        address = self.skale.wallet.address
        eth_bal_before = self.skale.web3.eth.getBalance(address)
        skl_bal_before = self.skale.token.get_balance(address)
        self.logger.info(f'ETH balance: {eth_bal_before}')
        self.logger.info(f'SKL balance: {skl_bal_before}')
        self.logger.info('--- Getting Bounty ---')
        lock = FileLock(LOCK_FILEPATH, timeout=1)
        self.logger.debug('Acquiring lock')
        try:
            with lock.acquire():
                res = self.skale.manager.get_bounty(self.id)
                receipt = wait_receipt(self.skale.web3, res['tx'], retries=30, timeout=6)
        except Timeout:
            self.logger.info('Another agent currently holds the lock')
            return 2
        self.logger.debug('Waiting for receipt of tx...')

        tx_hash = receipt['transactionHash'].hex()
        self.logger.info(f'tx hash: {tx_hash}')
        self.logger.info(f'Receipt: {receipt}')

        eth_bal = self.skale.web3.eth.getBalance(address)
        skl_bal = self.skale.token.get_balance(address)
        self.logger.info(f'ETH balance: {eth_bal}')
        self.logger.info(f'SKL balance: {skl_bal}')
        self.logger.debug(f'ETH difference: {eth_bal - eth_bal_before}')
        try:
            db.save_bounty_stats(tx_hash, eth_bal_before, skl_bal_before, eth_bal, skl_bal)
        except Exception as err:
            self.logger.error(f'Cannot save getBounty stats. Error: {err}')

        self.logger.info(LONG_DOUBLE_LINE)

        if receipt['status'] == 1:
            self.logger.info('The bounty was successfully received')
            h_receipt = self.skale.manager.contract.events.BountyGot().processReceipt(receipt)
            self.logger.info(LONG_LINE)
            self.logger.info(h_receipt)
            # self.logger.info(LONG_LINE)
            args = h_receipt[0]['args']
            try:
                db.save_bounty_event(datetime.utcfromtimestamp(args['time']), str(tx_hash),
                                     receipt['blockNumber'], args['nodeIndex'], args['bounty'],
                                     args['averageDowntime'], args['averageLatency'],
                                     receipt['gasUsed'])
            except Exception as err:
                self.logger.error(f'Cannot save getBounty event. Error: {err}')
        else:
            self.logger.info('The bounty was not received - transaction failed')
            # TODO: notify Skale Admin
            raise GetBountyTxFailedException

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
            raise

        last_block_number = self.skale.web3.eth.blockNumber
        block_data = self.skale.web3.eth.getBlock(last_block_number)
        block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
        self.logger.info(f'Reward date: {reward_date}')
        self.logger.info(f'Timestamp: {block_timestamp}')
        if reward_date > block_timestamp:
            raise IsNotTimeException(Exception)

        if utc_now >= reward_date:
            self.get_bounty()

    def job_listener(self, event):
        if event.exception:
            self.logger.info('The job failed')
            if type(event.exception) == IsNotTimeException:
                self.logger.debug('It\'s not time yet for reward - wait for current block is mined')
            utc_now = datetime.utcnow()
            self.scheduler.add_job(self.job, 'date', run_date=utc_now + timedelta(seconds=60))
            self.logger.debug(self.scheduler.get_jobs())
        else:
            self.logger.debug('The job finished successfully)')
            reward_date = self.get_reward_date()
            self.logger.debug(f'Reward date after job: {reward_date}')
            utc_now = datetime.utcnow()
            if utc_now > reward_date:
                self.logger.debug('Changing reward date for now')
                reward_date = utc_now
            self.scheduler.add_job(self.job, 'date', run_date=reward_date)
            self.scheduler.print_jobs()

    def run(self) -> None:
        """Starts agent"""
        self.logger.debug(f'{self.agent_name} started')
        reward_date = self.get_reward_date()
        self.logger.debug(f'Reward date on agent\'s start: {reward_date}')
        utc_now = datetime.utcnow()
        if utc_now > reward_date:
            reward_date = utc_now
        self.scheduler.add_job(self.job, 'date', run_date=reward_date)
        self.scheduler.print_jobs()
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.scheduler.start()
        while True:
            pass


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1].isdecimal():
        node_id = int(sys.argv[1])
    else:
        node_id = None

    skale = init_skale(node_id)
    bounty_collector = BountyCollector(skale, node_id)
    bounty_collector.run()
