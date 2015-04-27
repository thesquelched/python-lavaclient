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
def stack_fixture(service_fixture, link_response):
    return {
        'id': 'stack_id',
        'name': 'stack_name',
        'distro': 'distro',
        'services': [service_fixture],
        'links': [link_response],
    }


@pytest.fixture
def stack_node_group():
    return {
        'id': 'id',
        'flavor_id': 'hadoop1-7',
        'count': 10,
        'components': [{'name': 'component'}],
        'resource_limits': {
            'min_count': 1,
            'max_count': 10,
            'min_ram': 1024,
        }
    }


@pytest.fixture
def create_node_group():
    return {
        'id': 'id',
        'flavor_id': 'hadoop1-7',
        'count': 10,
        'component': [{'name': 'component'}],
    }


@pytest.fixture
def stack_detail_fixture(stack_fixture, stack_node_group):
    data = stack_fixture.copy()
    data.update(
        created='2015-01-01',
        node_groups=[stack_node_group],
    )
    return data


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


def test_get(lavaclient, stack_detail_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stack': stack_detail_fixture}
        resp = lavaclient.stacks.get('stack_id')
        assert isinstance(resp, response.Stack)


def test_create(lavaclient, service_create, stack_detail_fixture,
                create_node_group):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stack': stack_detail_fixture}
        resp = lavaclient.stacks.create(
            'stack_name', 'distro', [service_create])
        assert isinstance(resp, response.Stack)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'stack': stack_detail_fixture}
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


def test_delete(lavaclient, stack_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = None
        resp = lavaclient.stacks.delete('stack_id')
        assert resp is None
