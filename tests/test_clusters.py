import pytest
from mock import patch, MagicMock

from lavaclient.api import response
from lavaclient import error


def test_api_list(lavaclient, clusters_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = clusters_response
        resp = lavaclient.clusters.list()
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Cluster)


def test_api_get(lavaclient, cluster_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = cluster_response
        resp = lavaclient.clusters.get('cluster_id')
        assert isinstance(resp, response.ClusterDetail)


def test_api_create(lavaclient, cluster_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = cluster_response
        resp = lavaclient.clusters.create(
            'cluster_name', 'stack_id')
        assert isinstance(resp, response.ClusterDetail)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = cluster_response
        resp = lavaclient.clusters.create(
            'cluster_name', 'stack_id',
            node_groups=[])
        assert isinstance(resp, response.ClusterDetail)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = cluster_response
        resp = lavaclient.clusters.create(
            'cluster_name', 'stack_id',
            node_groups=[{
                'id': 'node_id',
                'count': 10,
                'flavor_id': 'hadoop1-60',
            }])
        assert isinstance(resp, response.ClusterDetail)

    pytest.raises(error.InvalidError, lavaclient.clusters.create, 'x' * 256,
                  'stack_id')
    pytest.raises(error.InvalidError, lavaclient.clusters.create, 'name',
                  'stack_id',
                  node_groups=[{'id': 'x' * 256}])


def test_api_resize(lavaclient, cluster_response):
    with patch.object(lavaclient, '_request') as request:

        request.return_value = cluster_response
        resp = lavaclient.clusters.resize(
            'cluster_id',
            node_groups=[{
                'id': 'node_id',
                'count': 10,
            }])

        assert isinstance(resp, response.ClusterDetail)

    pytest.raises(error.RequestError, lavaclient.clusters.resize,
                  'cluster_id')
    pytest.raises(error.RequestError, lavaclient.clusters.resize,
                  'cluster_id', node_groups=[])
    pytest.raises(error.RequestError, lavaclient.clusters.resize,
                  'cluster_id', node_groups=[{'id': 'node_id'}])


def test_api_update_credentials(lavaclient, cluster_response):
    with patch.object(lavaclient, '_request') as request:

        request.return_value = cluster_response
        resp = lavaclient.clusters._update_credentials(
            'cluster_id',
            credentials=[{'s3': 's3_cred'}]
        )

        assert isinstance(resp, response.ClusterDetail)
        request.assert_called_with('PUT', 'clusters/cluster_id',
                                   json={'cluster':
                                         {'credentials':
                                          [{'name': u's3_cred',
                                            'type': u's3'}]}})


def test_api_delete_ssh_credentials(lavaclient, cluster_response):
    with patch.object(lavaclient, '_request') as request:

        request.return_value = cluster_response
        resp = lavaclient.clusters.delete_ssh_credentials(
            'cluster_id',
            ['ssh_cred'],
            False
        )
        assert isinstance(resp, response.ClusterDetail)
        request.assert_called_with('PUT', 'clusters/cluster_id',
                                   json={'cluster':
                                         {'remove_credentials':
                                          [{'type': u'ssh_keys',
                                            'name': u'ssh_cred'}]}})


def test_api_delete(lavaclient, cluster_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = cluster_response
        resp = lavaclient.clusters.delete('cluster_id')
        assert resp is None


def test_api_cluster_nodes(lavaclient, nodes_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = nodes_response
        resp = lavaclient.clusters.nodes('cluster_id')
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert all(isinstance(item, response.Node) for item in resp)


def test_api_cluster_nodes_property(lavaclient, nodes_response,
                                    cluster_response):
    with patch.object(lavaclient, '_request',
                      MagicMock(return_value=cluster_response)):
        cluster = lavaclient.clusters.get('cluster_id')
        assert isinstance(cluster, response.ClusterDetail)

    with patch.object(lavaclient, '_request',
                      MagicMock(return_value=nodes_response)):
        nodes = cluster.nodes
        assert all(isinstance(node, response.Node) for node in nodes)


def test_api_clusters_nodes_property(lavaclient, nodes_response,
                                     clusters_response):
    with patch.object(lavaclient, '_request',
                      MagicMock(return_value=clusters_response)):
        clusters = lavaclient.clusters.list()
        assert all(isinstance(cluster, response.Cluster)
                   for cluster in clusters)

    with patch.object(lavaclient, '_request',
                      MagicMock(return_value=nodes_response)):
        for cluster in clusters:
            nodes = cluster.nodes
            assert all(isinstance(node, response.Node) for node in nodes)
