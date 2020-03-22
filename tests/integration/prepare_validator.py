import os

from skale import Skale
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet

from tests.constants import (
    D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_ID, D_VALIDATOR_MIN_DEL, D_VALIDATOR_NAME,
    ENDPOINT, ETH_PRIVATE_KEY, TEST_ABI_FILEPATH, TEST_DELTA, TEST_EPOCH
)

IP_BASE = '10.1.0.'
TEST_PORT = 123
DIR_LOG = '/skale_node_data/log'
DIR_ABI = '/skale_vol/contracts_info'
TEST_BOUNTY_DELAY = 0  # for using on geth > 0


def create_dirs():
    if not os.path.exists(DIR_LOG):
        os.makedirs(DIR_LOG)
    if not os.path.exists(DIR_ABI):
        os.makedirs(DIR_ABI)


def validator_exist(skale):
    return skale.validator_service.number_of_validators() > 0


def setup_validator(skale):
    """Create and activate a validator"""
    if not validator_exist(skale):
        create_validator(skale)
        enable_validator(skale)
    set_test_msr(skale, msr=0)
    skale.validator_service.link_node_address(
        node_address=skale.wallet.address,
        wait_for=True
    )
    accelerate_skale_manager(skale)


def accelerate_skale_manager(skale):

    reward_period = skale.constants_holder.get_reward_period()
    delta_period = skale.constants_holder.get_delta_period()
    print(f'Existing times for SKALE Manager: {reward_period}, {delta_period}')

    tx_res = skale.constants_holder.set_periods(TEST_EPOCH, TEST_DELTA, wait_for=True)
    assert tx_res.receipt['status'] == 1
    reward_period = skale.constants_holder.get_reward_period()
    delta_period = skale.constants_holder.get_delta_period()
    print(f'New time values for SKALE Manager: {reward_period}, {delta_period}')


def set_test_msr(skale, msr=D_VALIDATOR_MIN_DEL):
    skale.constants_holder._set_msr(
        new_msr=msr,
        wait_for=True
    )


def enable_validator(skale):
    print(f'Enabling validator ID: {D_VALIDATOR_ID}')
    skale.validator_service._enable_validator(D_VALIDATOR_ID, wait_for=True)


def create_validator(skale):
    print('Creating default validator')
    skale.validator_service.register_validator(
        name=D_VALIDATOR_NAME,
        description=D_VALIDATOR_DESC,
        fee_rate=D_VALIDATOR_FEE,
        min_delegation_amount=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )


def create_node(skale, node_id):
    res_tx = skale.manager.create_node(IP_BASE + str(node_id), TEST_PORT,
                                       'node_' + str(node_id), wait_for=True)

    if res_tx.receipt['status'] == 1:
        print(f'Node with ID = {node_id} was successfully created')


def get_active_ids(skale):
    return skale.nodes_data.get_active_node_ids()


def create_set_of_nodes(skale, first_node_id, nodes_number=2):

    active_ids = get_active_ids(skale)
    print(active_ids)

    if first_node_id not in active_ids:

        print(f'Starting creating {nodes_number} nodes from id = {first_node_id}:')
        for node_id in range(first_node_id, first_node_id + nodes_number):
            print(f'Creating node with id = {node_id}')
            create_node(skale, node_id)
    else:
        print(f'Node with id = {first_node_id} is already exists! Try another start id...')


def init_skale():
    web3 = init_web3(ENDPOINT)
    wallet = Web3Wallet(ETH_PRIVATE_KEY, web3)
    return Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet)


if __name__ == "__main__":
    skale = init_skale()
    setup_validator(skale)
