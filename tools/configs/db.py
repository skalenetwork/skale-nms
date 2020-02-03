import os

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_NAME = 'db_skale'
DB_HOST = '127.0.0.1'
