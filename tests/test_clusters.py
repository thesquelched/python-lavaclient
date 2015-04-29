import pytest
from mock import patch

from lavaclient2.api import response
from lavaclient2 import error


@pytest.fixture
def cluster_fixture(link_response):
    return {
        'id': 'cluster_id',
        'created': '2014-01-01',
        'updated': None,
        'name': 'cluster_name',
        'status': 'ACTIVE',
        'stack_id': 'stack_id',
        'cbd_version': 1,
        'links': [link_response],
    }


@pytest.fixture
def cluster_detail_fixture(cluster_fixture, node_group, cluster_script):
    data = cluster_fixture.copy()
    data.update(
        node_groups=[node_group],
        username='username',
        scripts=[cluster_script],
        progress=1.0
    )
    return data


@pytest.fixture
def nodes_fixture():
    return {}


def test_api_list(lavaclient, cluster_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'clusters': []}
        resp = lavaclient.clusters.list()
        assert isinstance(resp, list)
        assert len(resp) == 0

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'clusters': [cluster_fixture]}
        resp = lavaclient.clusters.list()
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Cluster)


def test_api_get(lavaclient, cluster_detail_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'cluster': cluster_detail_fixture}
        resp = lavaclient.clusters.get('cluster_id')
        assert isinstance(resp, response.ClusterDetail)


def test_api_create(lavaclient, cluster_detail_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'cluster': cluster_detail_fixture}
        resp = lavaclient.clusters.create(
            'cluster_name', 'username', 'keypair_name', 'stack_id')
        assert isinstance(resp, response.ClusterDetail)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'cluster': cluster_detail_fixture}
        resp = lavaclient.clusters.create(
            'cluster_name', 'username', 'keypair_name', 'stack_id',
            node_groups=[])
        assert isinstance(resp, response.ClusterDetail)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'cluster': cluster_detail_fixture}
        resp = lavaclient.clusters.create(
            'cluster_name', 'username', 'keypair_name', 'stack_id',
            node_groups=[{
                'id': 'node_id',
                'count': 10,
                'flavor_id': 'hadoop1-60',
            }])
        assert isinstance(resp, response.ClusterDetail)

    pytest.raises(error.InvalidError, lavaclient.clusters.create, 'x' * 256,
                  'username', 'keypair_name', 'stack_id')
    pytest.raises(error.InvalidError, lavaclient.clusters.create, 'name',
                  'username', 'x' * 256, 'stack_id')
    pytest.raises(error.InvalidError, lavaclient.clusters.create, 'name',
                  'username', 'keypair_name', 'stack_id',
                  node_groups=[{'id': 'x' * 256}])


def test_api_delete(lavaclient, cluster_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'cluster': cluster_fixture}
        resp = lavaclient.clusters.delete('cluster_id')
        assert resp is None
