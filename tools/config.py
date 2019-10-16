import os

HERE = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.join(HERE, os.pardir)
TEST_DATA_DIR = "test_data"
TEST_DATA_DIR_PATH = os.path.join(PROJECT_DIR, TEST_DATA_DIR)
TEST_ABI_FILE = "data.json"
