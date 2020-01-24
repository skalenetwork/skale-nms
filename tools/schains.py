from skale.schain_config.ports_allocation import calc_schain_base_port
from tools.helper import init_skale
from skale.dataclasses.skaled_ports import SkaledPorts


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
    print(skale.nodes_data.get(node_id))

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


if __name__ == '__main__':
    skale = init_skale()
    node_id = 2
    check = check_schains_for_node(skale, node_id)
    print(f'Check = {check}')
