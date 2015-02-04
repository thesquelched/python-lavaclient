import pytest
from mock import patch

from lavaclient2.api import response
from lavaclient2 import error


@pytest.fixture
def service_create():
    return {
        'name': 'service_name',
        'modes': ['mode1'],
    }


@pytest.fixture
def service_fixture():
    return {
        'name': 'service_name',
        'modes': ['mode1'],
        'version': 'version',
        'components': [{'name': 'component'}],
    }


@pytest.fixture
def stack_fixture(service_fixture, node_group):
    return {
        'id': 'stack_id',
        'name': 'stack_name',
        'distro': 'distro',
        'services': [service_fixture],
        'node_groups': [node_group],
    }


def test_list(lavaclient, stack_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stacks': []}
        resp = lavaclient.stacks.list()
        assert isinstance(resp, list)
        assert len(resp) == 0

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stacks': [stack_fixture]}
        resp = lavaclient.stacks.list()
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Stack)


def test_get(lavaclient, stack_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stack': stack_fixture}
        resp = lavaclient.stacks.get('stack_id')
        assert isinstance(resp, response.Stack)


def test_create(lavaclient, service_create, stack_fixture, node_group):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stack': stack_fixture}
        resp = lavaclient.stacks.create(
            'stack_name', 'distro')
        assert isinstance(resp, response.Stack)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stack': stack_fixture}
        resp = lavaclient.stacks.create(
            'stack_name', 'distro', services=[service_create])
        assert isinstance(resp, response.Stack)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stack': stack_fixture}
        resp = lavaclient.stacks.create(
            'stack_name', 'distro', node_groups=[node_group])
        assert isinstance(resp, response.Stack)

    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'x' * 256,
                  'distro')
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'x' * 256)
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', services=[{'name': 'x' * 256}])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', services=[{'name': 'name', 'modes': ['x' * 256]}])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', services=[{'name': 'name', 'modes': ['mode',
                                                                 'x' * 256]}])
    pytest.raises(error.InvalidError, lavaclient.stacks.create, 'name',
                  'distro', node_groups=[{'id': 'x' * 256}])


def test_delete(lavaclient, stack_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = None
        resp = lavaclient.stacks.delete('stack_id')
        assert resp is None
