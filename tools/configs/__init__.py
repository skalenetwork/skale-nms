import os

LONG_LINE = '-' * 100
LONG_DOUBLE_LINE = '=' * 100

SKALE_VOLUME_PATH = '/skale_vol'
NODE_DATA_PATH = '/skale_node_data'

CONFIG_FOLDER_NAME = 'config'
CONTRACTS_INFO_FOLDER_NAME = 'contracts_info'

MANAGER_CONTRACTS_INFO_NAME = 'manager.json'
IMA_CONTRACTS_INFO_NAME = 'ima.json'
DKG_CONTRACTS_INFO_NAME = 'dkg.json'

CONTRACTS_INFO_FOLDER = os.path.join(SKALE_VOLUME_PATH, CONTRACTS_INFO_FOLDER_NAME)
CONFIG_FOLDER = os.path.join(SKALE_VOLUME_PATH, CONFIG_FOLDER_NAME)

LOCAL_WALLET_FILENAME = 'local_wallet.json'
LOCAL_WALLET_FILEPATH = os.path.join(NODE_DATA_PATH, LOCAL_WALLET_FILENAME)

NODE_CONFIG_FILENAME = 'node_config.json'
NODE_CONFIG_FILEPATH = os.path.join(NODE_DATA_PATH, NODE_CONFIG_FILENAME)


LOCK_FILE = "tx.lock"
LOCK_FILEPATH = os.path.join(NODE_DATA_PATH, LOCK_FILE)

GOOD_IP = '8.8.8.8'
MONITOR_PERIOD = 1  # in min (2)
REPORT_PERIOD = 2  # in min (5)
BLOCK_STEP_SIZE = 5000
REWARD_DELAY = 60  # in seconds
