import os
from tools.configs import CONTRACTS_INFO_FOLDER, MANAGER_CONTRACTS_INFO_NAME

ENDPOINT = os.environ['ENDPOINT']
ABI_FILEPATH = os.path.join(CONTRACTS_INFO_FOLDER, MANAGER_CONTRACTS_INFO_NAME)
