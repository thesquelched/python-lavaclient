from mock import patch

from lavaclient.api import response


def test_list(lavaclient, nodes_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'nodes': []}
        resp = lavaclient.nodes.list('cluster_id')
        assert isinstance(resp, list)
        assert len(resp) == 0

    with patch.object(lavaclient, '_request') as request:
        request.return_value = nodes_response
        resp = lavaclient.nodes.list('cluster_id')
        assert isinstance(resp, list)
        assert len(resp) == 1
        assert all(isinstance(item, response.Node) for item in resp)


def test_delete(lavaclient, node_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = node_response
        resp = lavaclient.nodes.delete('cluster_id', 'node_id')
        assert resp is None
