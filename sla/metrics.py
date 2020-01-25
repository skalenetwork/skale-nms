import requests
from skale.dataclasses.skaled_ports import SkaledPorts
from skale.schain_config.ports_allocation import calc_schain_base_port

from sla import ping
from tools.configs import GOOD_IP
from tools.helper import HEALTH_REQ_URL, PORT, init_skale, logger


def get_metrics_for_node(skale, node, is_test_mode):
    host = GOOD_IP if is_test_mode else node['ip']
    metrics = ping.get_node_metrics(host)
    # metrics = sim.generate_node_metrics()  # use to simulate metrics for some tests
    if not is_test_mode:
        healthcheck = get_containers_healthcheck(host, is_test_mode)
        schains_check = check_schains_for_node(skale, node['id'])
        metrics['is_offline'] = metrics['is_offline'] | healthcheck | schains_check

    logger.info(f'Received metrics from node ID = {node["id"]}: {metrics}')
    return metrics


def check_schain(skale, schain, node_ip):
    name = schain['name']
    addr = "http://" + node_ip + ":" + str(schain['http_rpc_port'])
    print(f'\nChecking {name}, {addr}')

    try:
        block_number = skale.web3.eth.blockNumber
        print(f"Current block number = {block_number}")
        return 0
    except Exception as err:
        print(f'Error occurred while getting block number : {err}')
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
    print(f'schains = {schains}')
    for schain in schains:
        if check_schain(skale, schain, node_ip) == 1:
            return 1

    return 0


def get_containers_healthcheck(host, test_mode):
    """Return 0 if OK or 1 if failed"""
    if test_mode:
        return 0
    url = 'http://' + host + ':' + PORT + HEALTH_REQ_URL
    logger.info(f'Checking: {url}')
    try:
        response = requests.get(url, timeout=15)
    except requests.exceptions.ConnectionError as err:
        logger.error(err)
        print(f'Could not connect to {url}')
        return 1
    except Exception as err:
        logger.error(err)
        print(f'Could not get data from {url}')
        return 1

    if response.status_code != requests.codes.ok:
        print('Request failed, status code:', response.status_code)
        return 1

    json = response.json()
    if json['res'] != 1:
        for error in response.json()['errors']:
            print(error)
        return 1
    else:
        data = json['data']
    for container in data:
        if 'skale_schain_' not in container['name'] and 'skale_ima_' not in container['name'] and \
                (not container['state']['Running'] or container['state']['Paused']):
            return 1
    return 0


if __name__ == '__main__':
    import socket
    skale = init_skale()
    node_id = 2
    node = {'id': node_id, 'ip': socket.inet_ntoa(b'\xb2\x80\xfc\xf1')}
    # check = check_schains_for_node(skale, node_id)
    metrics = get_metrics_for_node(skale, node, False)
    print(f'Check = {metrics}')
