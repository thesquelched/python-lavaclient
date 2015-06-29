import pytest
from mock import patch

from lavaclient.api import response
from lavaclient import error


@pytest.fixture
def service_create():
    return {
        'name': 'service_name',
        'modes': ['mode1'],
    }


@pytest.fixture
def create_node_group():
    return {
        'id': 'id',
        'flavor_id': 'hadoop1-7',
        'count': 10,
        'component': [{'name': 'component'}],
    }


def test_list(lavaclient, stacks_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stacks': []}
        resp = lavaclient.stacks.list()
        assert isinstance(resp, list)
        assert len(resp) == 0

    with patch.object(lavaclient, '_request') as request:
        request.return_value = stacks_response
        resp = lavaclient.stacks.list()
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Stack)


def test_get(lavaclient, stack_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = stack_response
        resp = lavaclient.stacks.get('stack_id')
        assert isinstance(resp, response.Stack)


def test_create(lavaclient, service_create, stack_response,
                create_node_group):
    pytest.skip('create is not yet supported')

    with patch.object(lavaclient, '_request') as request:
        request.return_value = stack_response
        resp = lavaclient.stacks.create(
            'stack_name', 'distro', [service_create])
        assert isinstance(resp, response.Stack)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = stack_response
        resp = lavaclient.stacks.create(
            'stack_name', 'distro', [service_create],
            node_groups=[create_node_group])
        assert isinstance(resp, response.Stack)

    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'x' * 256,
                  'distro', [service_create])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'x' * 256, [service_create])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', [{'name': 'x' * 256}])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', [{'name': 'name', 'modes': ['x' * 256]}])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', [{'name': 'name', 'modes': ['mode', 'x' * 256]}])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', [service_create],
                  node_groups=[{'id': 'x' * 256}])


def test_delete(lavaclient):
    pytest.skip('Delete is not yet supported')

    with patch.object(lavaclient, '_request') as request:
        request.return_value = None
        resp = lavaclient.stacks.delete('stack_id')
        assert resp is None
