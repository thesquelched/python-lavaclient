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


def test_cluster_repr(cluster_response):
    cluster = response.Cluster(cluster_response)
    assert repr(cluster) == "Cluster(id='cluster_id')"


def test_link(link_response):
    link = response.Link(link_response)

    assert link.rel == 'rel'
    assert link.href == 'href'

    assert repr(link) == "Link(rel='rel', href='href')"


def test_flavors(flavor_response):
    flavor = response.Flavor(flavor_response)

    assert flavor.id == 'hadoop1-15'
    assert flavor.name == 'Medium Hadoop Instance'
    assert flavor.vcpus == 4
    assert flavor.ram == 15360
    assert flavor.disk == 2500

    assert isinstance(flavor.links, list)
    assert len(flavor.links) == 1
    assert isinstance(flavor.links[0], response.Link)
