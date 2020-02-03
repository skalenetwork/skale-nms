from unittest import mock

import requests

from sla.metrics import get_containers_healthcheck
from tools.configs import WATCHDOG_PORT, WATCHDOG_URL


def get_test_url(base):
    return f'http://{base}:{WATCHDOG_PORT}/{WATCHDOG_URL}'


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    data_ok1 = [{'name': 'container_name', 'state': {'Running': True, 'Paused': False}},
                {'name': 'skale_schain_name', 'state': {'Running': True, 'Paused': False}}]
    data_ok2 = [{'name': 'container_name', 'state': {'Running': True, 'Paused': False}},
                {'name': 'skale_schain_name', 'state': {'Running': False, 'Paused': False}}]
    data_bad1 = [{'name': 'container_name', 'state': {'Running': False, 'Paused': False}},
                 {'name': 'skale_schain_name', 'state': {'Running': True, 'Paused': False}}]
    data_bad2 = [{'name': 'container_name', 'state': {'Running': False, 'Paused': True}},
                 {'name': 'skale_schain_name', 'state': {'Running': True, 'Paused': False}}]

    if args[0] == get_test_url('url_ok1'):
        return MockResponse({'res': 1, 'data': data_ok1}, 200)
    elif args[0] == get_test_url('url_bad1'):
        return MockResponse({'res': 1, 'data': data_bad1}, 200)
    elif args[0] == get_test_url('url_bad2'):
        return MockResponse({'res': 0, 'data': data_ok1, 'errors': ["Error1"]}, 200)
    elif args[0] == get_test_url('url_bad3'):
        return MockResponse({'res': 1, 'data': data_ok1}, 500)
    elif args[0] == get_test_url('url_bad4'):
        return MockResponse({'res': 1, 'data': data_bad2}, 200)
    elif args[0] == get_test_url('url_ok2'):
        return MockResponse({'res': 1, 'data': data_ok2}, 200)

    return MockResponse(None, 404)


def connection_error(*args, **kwargs):
    raise requests.exceptions.ConnectionError


def unknown_error(*args, **kwargs):
    raise Exception


@mock.patch('sla.metrics.requests.get', side_effect=mocked_requests_get)
def test_healthcheck_pos(mock_get):
    res = get_containers_healthcheck('url_ok1')
    assert res == 0
    res = get_containers_healthcheck('url_ok2')
    assert res == 0


@mock.patch('sla.metrics.requests.get', side_effect=mocked_requests_get)
def test_healthcheck_neg(mock_get):
    res = get_containers_healthcheck('url_bad1')
    assert res == 1
    res = get_containers_healthcheck('url_bad2')
    assert res == 1
    res = get_containers_healthcheck('url_bad3')
    assert res == 1
    res = get_containers_healthcheck('url_bad4')
    assert res == 1
    res = get_containers_healthcheck('url_bad5')
    assert res == 1


@mock.patch('sla.metrics.requests.get', side_effect=connection_error)
def test_healthcheck_connection_error(mock_get):
    res = get_containers_healthcheck('url_ok')
    assert res == 1


@mock.patch('sla.metrics.requests.get', side_effect=unknown_error)
def test_healthcheck_unknown_error(mock_get):
    res = get_containers_healthcheck('url_ok')
    assert res == 1
