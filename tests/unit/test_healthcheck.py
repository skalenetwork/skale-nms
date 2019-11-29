import unittest
from unittest import mock
from tools.helper import get_containers_healthcheck  # MyGreatClass


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    data1 = [{'state': {'Running': True}}]
    data2 = [{'state': {'Running': False}}]
    if args[0] == 'http://url_ok:3007/healthchecks/containers':
        return MockResponse({'res': 1, 'data': data1}, 200)
    if args[0] == 'http://url_bad1:3007/healthchecks/containers':
        return MockResponse({'res': 1, 'data': data2}, 200)
    elif args[0] == 'http://url_bad2:3007/healthchecks/containers':
        return MockResponse({'res': 0, 'data': data1, 'errors': ["Error1"]}, 200)

    return MockResponse(None, 404)


@mock.patch('tools.helper.requests.get', side_effect=mocked_requests_get)
def test_healthcheck(mock_get):
    res = get_containers_healthcheck('url_ok', False)
    assert res == 0
    res = get_containers_healthcheck('url_bad1', False)
    assert res == 1
    res = get_containers_healthcheck('url_bad2', False)
    assert res == 1


if __name__ == '__main__':
    unittest.main()
