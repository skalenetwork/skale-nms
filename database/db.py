#   -*- coding: utf-8 -*-
#
#   This file is part of SLA
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

#########################################
# Context manager for a database (MySQL)
#########################################

import mysql.connector


db_config = {'host': '127.0.0.1',
             'user': 'user',
             'password': 'pass',
             'database': 'test'}


class ConnectError(Exception):
    """Raised if the backend-database cannot be connected to."""
    pass


class CredentialsError(Exception):
    """Raised if the database is up, but there's a login issue."""
    pass


class SQLError(Exception):
    """Raised if the query caused problems."""
    pass


class UseDatabase:

    def __init__(self, config: dict):
        """Add the database configuration parameters:
            host - the IP address of the host running MySQL
            user - the MySQL username to use
            password - the user's password
            database - the name of the database to use
        """
        self.configuration = config

    def __enter__(self) -> 'cursor':
        """Connect to database and create (returns) a DB cursor
        """
        try:
            self.conn = mysql.connector.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except mysql.connector.errors.InterfaceError as err:
            raise ConnectError(err) from err
        except mysql.connector.errors.ProgrammingError as err:
            raise CredentialsError(err) from err

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Commits and destroy the cursor and the connection
        """
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exc_type:
            raise exc_type(exc_value)


def save_to_db(my_id, node_id, is_alive, latency):

    try:
        with UseDatabase(db_config) as cursor:
            _SQL = f"""
                   INSERT INTO report (my_id, node_id, is_alive, latency) 
                   VALUES ({my_id},{node_id},{is_alive},{latency})"""

            cursor.execute(_SQL)
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
    except CredentialsError as err:
        print('User-id/Password issues. Error:', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print("Error:", str(err))


def save_events(tx_dt, tx_hash, my_id, bounty, latency, downtime, gas, logger):

    try:
        with UseDatabase(db_config) as cursor:
            _SQL = f"""
                   INSERT INTO bounty (tx_dt, tx_hash, my_id, bounty, latency, downtime, gas) 
                   VALUES ('{tx_dt}',{tx_hash},{my_id},{bounty},{latency},{downtime},{gas})"""

            cursor.execute(_SQL)
    except ConnectionError as err:
        logger.error('Is your database switched on? Error:', str(err))
        return
    except CredentialsError as err:
        logger.error('User-id/Password issues. Error:', str(err))
    except SQLError as err:
        logger.error('Is your query correct? Error:', str(err))
    except Exception as err:
        logger.error('Error:', str(err))


def get_month_metrics_for_node(my_id, node_id, max_date) -> dict:
    """ Returns a dict with month metrics
    """

    try:
        with UseDatabase(db_config) as cursor:
            _SQL = f"""
                   SELECT COUNT(*) AS downtime FROM report  
                   WHERE my_id = {my_id} AND node_id = {node_id} AND is_alive = 1 AND stamp > '{max_date}'
                """
            cursor.execute(_SQL)
            downtime = cursor.fetchone()[0]
            _SQL = f"""
                   SELECT AVG(latency) AS latency FROM report 
                WHERE my_id = {my_id} AND node_id = {node_id} AND stamp > '{max_date}'
                """
            print(_SQL)
            cursor.execute(_SQL)
            latency = cursor.fetchone()[0]
            return {'downtime': downtime, 'latency': latency}
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
    except CredentialsError as err:
        print('User-id/Password issues. Error:', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print("Error:", str(err))


def get_downtime_for_node(my_id, node_id, max_date):

    with UseDatabase(db_config) as cursor:
        _SQL = f"""
            SELECT COUNT(*) AS downtime FROM report 
            WHERE my_id = {my_id} AND node_id = {node_id} AND is_alive = 1 AND stamp > '{max_date}'
            """
        cursor.execute(_SQL)
        data = cursor.fetchone()[0]
        return data


def get_latency_for_node(my_id, node_id, max_date):

    with UseDatabase(db_config) as cursor:
        _SQL = f"""
            SELECT AVG(latency) AS latency FROM report 
            WHERE my_id = {my_id} AND node_id = {node_id} AND stamp > '{max_date}'
            """
        cursor.execute(_SQL)
        data = cursor.fetchone()[0]
        return data


def clear_db():

    with UseDatabase(db_config) as cursor:
        _SQL = 'DELETE FROM report'
        cursor.execute(_SQL)


def get_recs(my_id, node_id, max_date):
    """ Test function - returns all records for defined parameters
    """
    with UseDatabase(db_config) as cursor:
        _SQL = f"""SELECT * FROM report WHERE my_id = {my_id} AND node_id = {node_id} AND stamp > '{max_date}'"""
        cursor.execute(_SQL)
        data = cursor.fetchall()
        return data


if __name__ == '__main__':
    clear_db()
