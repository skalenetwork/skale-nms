#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE-NMS
#
#   Copyright (C) 2020 SKALE Labs
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

import pingparsing
import requests
from skale.dataclasses.skaled_ports import SkaledPorts
from skale.schain_config.ports_allocation import calc_schain_base_port
from web3 import HTTPProvider, Web3

from tools.configs import GOOD_IP, WATCHDOG_PORT, WATCHDOG_URL
from tools.helper import logger


def get_metrics_for_node(skale, node, is_test_mode):
    host = GOOD_IP if is_test_mode else node['ip']
    metrics = get_ping_node_results(host)
    if not is_test_mode:
        healthcheck = get_containers_healthcheck(host)
        schains_check = check_schains_for_node(skale, node['id'], host)
        metrics['is_offline'] = metrics['is_offline'] | healthcheck | schains_check

    logger.info(f'Received metrics from node ID = {node["id"]}: {metrics}')
    return metrics


def get_schain_endpoint(node_ip, rpc_port):
    return 'http://' + node_ip + ':' + str(rpc_port)


def check_schain(schain, node_ip):
    schain_name = schain['name']
    schain_endpoint = get_schain_endpoint(node_ip, schain['http_rpc_port'])
    logger.info(f'\nChecking {schain_name}: {schain_endpoint}')

    try:
        web3 = Web3(HTTPProvider(schain_endpoint))
        block_number = web3.eth.blockNumber
        logger.info(f"Current block number for {schain_name} = {block_number}")
        return 0
    except Exception as err:
        logger.error(f'Error occurred while getting block number : {err}')
        return 1


def check_schains_for_node(skale, node_id, node_ip):
    raw_schains = skale.schains_data.get_schains_for_node(node_id)

    node_info = skale.nodes_data.get(node_id)
    node_base_port = node_info['port']

    schains = [{'name': schain['name'],
                'index': schain['index'],
                'http_rpc_port': calc_schain_base_port(
                    node_base_port, schain['index']) + SkaledPorts.HTTP_JSON.value}
               for schain in raw_schains]
    logger.debug(f'schains = {schains}')
    for schain in schains:
        if check_schain(schain, node_ip) == 1:
            return 1

    return 0


def get_containers_healthcheck_url(host):
    return f'http://{host}:{WATCHDOG_PORT}/{WATCHDOG_URL}'


def get_containers_healthcheck(host):
    """Return 0 if OK or 1 if failed"""
    url = get_containers_healthcheck_url(host)
    logger.info(f'Checking: {url}')
    try:
        response = requests.get(url, timeout=15)
    except requests.exceptions.ConnectionError as err:
        logger.info(f'Could not connect to {url}')
        logger.error(err)
        return 1
    except Exception as err:
        logger.info(f'Could not get data from {url}')
        logger.error(err)
        return 1

    if response.status_code != requests.codes.ok:
        logger.info(f'Request failed, status code: {response.status_code}')
        return 1

    res = response.json()
    if res.get('error') is not None:
        logger.info(res['error'])
        return 1
    data = res.get('data')
    if data is None:
        logger.info(f'No data found checking {url}')
        return 1

    for container in data:
        if not container['state']['Running'] or container['state']['Paused']:
            logger.info(f'{container["name"]} is not running or paused')
            return 1
    return 0


def get_ping_node_results(host) -> dict:
    """Returns a node host metrics (downtime and latency)"""

    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination_host = host
    transmitter.ping_option = '-w1'
    transmitter.count = 3
    result = transmitter.ping()
    if ping_parser.parse(
            result).as_dict()['rtt_avg'] is None or ping_parser.parse(
                result).as_dict()['packet_loss_count'] > 0:
        is_offline = True
        latency = -1
        logger.info('No connection to host!')
    else:
        is_offline = False
        latency = int((ping_parser.parse(result).as_dict()['rtt_avg']) * 1000)

    return {'is_offline': is_offline, 'latency': latency}
