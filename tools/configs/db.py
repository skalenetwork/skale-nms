import os
from tools.configs import ENV

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_NAME = 'db_skale'
if ENV == 'DEV':
    DB_HOST = '127.0.0.1'
else:
    DB_HOST = 'mysql'
