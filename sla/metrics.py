import pingparsing
import requests
from skale.dataclasses.skaled_ports import SkaledPorts
from skale.schain_config.ports_allocation import calc_schain_base_port

from tools.configs import GOOD_IP
from tools.helper import HEALTH_REQ_URL, PORT, logger


def get_metrics_for_node(skale, node, is_test_mode):
    host = GOOD_IP if is_test_mode else node['ip']
    metrics = get_ping_node_results(host)
    if not is_test_mode:
        healthcheck = get_containers_healthcheck(host)
        schains_check = check_schains_for_node(skale, node['id'])
        metrics['is_offline'] = metrics['is_offline'] | healthcheck | schains_check

    logger.info(f'Received metrics from node ID = {node["id"]}: {metrics}')
    return metrics


def check_schain(skale, schain, node_ip):
    name = schain['name']
    addr = "http://" + node_ip + ":" + str(schain['http_rpc_port'])
    logger.info(f'\nChecking {name}, {addr}')

    try:
        block_number = skale.web3.eth.blockNumber
        logger.debug(f"Current block number = {block_number}")
        return 0
    except Exception as err:
        logger.exception(f'Error occurred while getting block number : {err}')
        return 1


def check_schains_for_node(skale, node_id):
    raw_schains = skale.schains_data.get_schains_for_node(node_id)

    node_info = skale.nodes_data.get(node_id)
    node_base_port = node_info['port']
    node_ip = str(node_info['ip'])

    schains = [{'name': schain['name'],
                'index': schain['index'],
                'http_rpc_port': calc_schain_base_port(
                    node_base_port, schain['index']) + SkaledPorts.HTTP_JSON.value}
               for schain in raw_schains]
    logger.debug(f'schains = {schains}')
    for schain in schains:
        if check_schain(skale, schain, node_ip) == 1:
            return 1

    return 0


def get_containers_healthcheck(host):
    """Return 0 if OK or 1 if failed"""
    url = 'http://' + host + ':' + PORT + HEALTH_REQ_URL
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
        logger.info('Request failed, status code:', response.status_code)
        return 1

    json = response.json()
    if json['res'] != 1:
        for error in response.json()['errors']:
            logger.info(error)
        return 1
    else:
        data = json['data']
    for container in data:
        if 'skale_schain_' not in container['name'] and 'skale_ima_' not in container['name'] and \
                (not container['state']['Running'] or container['state']['Paused']):
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
        # print('Ping ok!')

    return {'is_offline': is_offline, 'latency': latency}
