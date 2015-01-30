import pytest
from datetime import datetime

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
def cluster_response(node_group):
    return {
        'id': 'cluster_id',
        'name': 'cluster_name',
        'created': '2014-01-01',
        'updated': None,
        'status': 'PENDING',
        'stack_id': 'stack_id',
        'node_groups': [node_group]
    }


def test_cluster(cluster_response):
    cluster = response.Cluster(cluster_response)

    assert cluster.id == 'cluster_id'
    assert cluster.name == 'cluster_name'
    assert cluster.created == datetime(2014, 1, 1)
    assert cluster.updated is None
    assert cluster.status == 'PENDING'
    assert cluster.stack_id == 'stack_id'

    assert len(cluster.node_groups) == 1

    group = cluster.node_groups[0]
    assert group.id == 'node_id'
    assert group.count == 1
    assert group.flavor_id == 'hadoop1-60'
    assert group.components == {}


def test_clusters_response(cluster_response):
    resp = response.ClustersResponse(clusters=[cluster_response])
    assert len(resp.clusters) == 1

    resp = response.ClustersResponse()
    assert len(resp.clusters) == 0
