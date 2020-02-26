import json
import os

from skale import Skale
from skale.transactions.tools import post_transaction
from skale.utils.web3_utils import check_receipt, init_web3
from skale.wallets import Web3Wallet

from tests.constants import (
    D_DELEGATION_INFO, D_DELEGATION_PERIOD, D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_ID,
    D_VALIDATOR_MIN_DEL, D_VALIDATOR_NAME, ENDPOINT, ETH_PRIVATE_KEY, TEST_ABI_FILEPATH,
    TEST_DELTA, TEST_EPOCH
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
    delegation_id = len(skale.delegation_service.get_all_delegations_by_validator(
        skale.wallet.address))
    set_test_msr(skale)
    delegate_to_validator(skale)
    accept_pending_delegation(skale, delegation_id)
    skip_delegation_delay(skale, delegation_id)
    accelerate_skale_manager(skale)


def accelerate_skale_manager(skale):

    reward_period = skale.constants_holder.get_reward_period()
    delta_period = skale.constants_holder.get_delta_period()
    print(f'Existing times for SM: {reward_period}, {delta_period}')

    tx_res = skale.constants_holder.set_periods(TEST_EPOCH, TEST_DELTA, wait_for=True)
    assert tx_res.receipt['status'] == 1
    print(tx_res.receipt)
    reward_period = skale.constants_holder.get_reward_period()
    delta_period = skale.constants_holder.get_delta_period()
    print(f'New times for SM: {reward_period}, {delta_period}')


def link_address_to_validator(skale):
    print('Linking address to validator')
    tx_res = skale.delegation_service.link_node_address(
        node_address=skale.wallet.address,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def skip_delegation_delay(skale, delegation_id):
    print(f'Activating delegation with ID {delegation_id}')
    tx_res = skale.token_state._skip_transition_delay(
        delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def accept_pending_delegation(skale, delegation_id):
    print(f'Accepting delegation with ID: {delegation_id}')
    tx_res = skale.delegation_service.accept_pending_delegation(
        delegation_id=delegation_id,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def get_test_delegation_amount(skale):
    msr = skale.constants_holder.msr()
    return msr * 10


def set_test_msr(skale):
    skale.constants_holder._set_msr(
        new_msr=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )


def delegate_to_validator(skale):
    print(f'Delegating tokens to validator ID: {D_VALIDATOR_ID}')
    tx_res = skale.delegation_service.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=get_test_delegation_amount(skale),
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


def enable_validator(skale):
    print(f'Enabling validator ID: {D_VALIDATOR_ID}')
    tx_res = skale.validator_service._enable_validator(D_VALIDATOR_ID, wait_for=True)
    check_receipt(tx_res.receipt)


def create_validator(skale):
    print('Creating default validator')
    tx_res = skale.delegation_service.register_validator(
        name=D_VALIDATOR_NAME,
        description=D_VALIDATOR_DESC,
        fee_rate=D_VALIDATOR_FEE,
        min_delegation_amount=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )
    check_receipt(tx_res.receipt)


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


def get_abi(abi_filepath=TEST_ABI_FILEPATH):
    with open(abi_filepath) as data_file:
        return json.load(data_file)


def delegation_patch(skale):  # temporary patch for sending SKL for SKALE manager
    skl_amount = 5000000000000000000000000
    gas = 600000
    data = "0x000000000000000000000000"

    abi = get_abi()
    skale_balances_address = abi['skale_balances_address']
    skale_manager_address = abi['skale_manager_address']
    data += skale_manager_address[2:]
    print(skale.web3.eth.getBalance(skale_balances_address))
    print(skale.web3.eth.getBalance(skale_manager_address))

    op = skale.token.contract.functions.send(skale_balances_address, skl_amount, data)
    res = post_transaction(skale.wallet, op, gas)
    print(res.receipt)


if __name__ == "__main__":
    skale = init_skale()
    setup_validator(skale)
    delegation_patch(skale)
