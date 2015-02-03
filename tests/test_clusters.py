import pytest
from datetime import datetime
import figgis
from mock import patch

from lavaclient2.api import clusters
from lavaclient2.api import response


@pytest.fixture
def node_group():
    return {
        'id': 'node_id',
        'count': 1,
        'flavor_id': 'hadoop1-60',
        'components': {},
    }


@pytest.fixture
def cluster_fixture(node_group):
    return {
        'id': 'cluster_id',
        'name': 'cluster_name',
        'created': '2014-01-01',
        'updated': None,
        'status': 'PENDING',
        'stack_id': 'stack_id',
        'node_groups': [node_group]
    }


def test_cluster_response(cluster_fixture):
    cluster = clusters.ClusterResponse(cluster=cluster_fixture)

    assert cluster.cluster.id == 'cluster_id'
    assert cluster.cluster.name == 'cluster_name'
    assert cluster.cluster.created == datetime(2014, 1, 1)
    assert cluster.cluster.updated is None
    assert cluster.cluster.status == 'PENDING'
    assert cluster.cluster.stack_id == 'stack_id'

    assert len(cluster.cluster.node_groups) == 1

    group = cluster.cluster.node_groups[0]
    assert group.id == 'node_id'
    assert group.count == 1
    assert group.flavor_id == 'hadoop1-60'
    assert group.components == {}


def test_clusters_response(cluster_fixture):
    resp = clusters.ClustersResponse(clusters=[cluster_fixture])
    assert len(resp.clusters) == 1

    resp = clusters.ClustersResponse(clusters=[])
    assert len(resp.clusters) == 0

    pytest.raises(figgis.PropertyError, clusters.ClustersResponse)


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


def test_api_get(lavaclient, cluster_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'cluster': cluster_fixture}
        resp = lavaclient.clusters.get('cluster_id')
        assert isinstance(resp, response.Cluster)
