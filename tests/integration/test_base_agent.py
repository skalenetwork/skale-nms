import pytest

from tools.base_agent import BaseAgent
from tools.config_storage import ConfigStorage
from tools.configs import NODE_CONFIG_FILEPATH
from tools.exceptions import NodeNotFoundException
from tools.helper import init_skale


@pytest.fixture(scope="module")
def skale(request):
    print("\nskale setup")
    _skale = init_skale()
    return _skale


def test_init_base_agent(skale):
    print("Test agent init with given node id")
    agent0 = BaseAgent(skale, 0)
    assert agent0.id == 0

    print("Test agent init without given node id - read id from file")
    config_node = ConfigStorage(NODE_CONFIG_FILEPATH)
    config_node.update({'node_id': 1})
    agent1 = BaseAgent(skale)
    assert agent1.id == 1

    print("Test agent init with non-existing node id")
    with pytest.raises(NodeNotFoundException):
        BaseAgent(skale, 100)

    print("Test agent init with non-integer node id")
    config_node.update({'node_id': 'one'})

    with pytest.raises(Exception):
        BaseAgent(skale)
