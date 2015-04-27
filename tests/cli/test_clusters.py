import pytest
from mock import patch
from datetime import datetime

from lavaclient2.cli import main
from lavaclient2.api.response import Cluster, ClusterDetail, NodeGroup


@patch('sys.argv', ['lava2', 'clusters', 'list'])
def test_list(print_table, mock_client, clusters_response):
    mock_client._request.return_value = clusters_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['cluster_id', 'cluster_name', 'PENDING',
                           'stack_id', datetime(2014, 1, 1)]]
    assert header == Cluster.table_header
    assert kwargs['title'] is None


@patch('sys.argv', ['lava2', 'clusters', 'get', 'cluster_id'])
def test_get(print_table, print_single_table, mock_client, cluster_response):
    mock_client._request.return_value = cluster_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['cluster_id', 'cluster_name', 'PENDING', 'stack_id',
                    datetime(2014, 1, 1), 1, 'username', 1.0]
    assert header == ClusterDetail.table_header
    assert kwargs['title'] == 'Cluster'

    assert print_table.call_count == 2

    (data, header), kwargs = print_table.call_args_list[0]
    assert list(data) == [['id', 'hadoop1-60', 1, '[{name=component}]']]
    assert header == NodeGroup.table_header
    assert kwargs['title'] == 'Node Groups'

    (data, header), kwargs = print_table.call_args_list[1]
    assert list(data) == [['script_id', 'name', 'status']]
    assert header == ['ID', 'Name', 'Status']
    assert kwargs['title'] == 'Scripts'


@pytest.mark.parametrize('args,node_groups', [
    ([], None),
    (['--node-group', 'id'], [{'id': 'id'}]),
    (['--node-group', 'id(count=10)'], [{'id': 'id', 'count': 10}]),
    (['--node-group', 'id(flavor_id=flavor)'],
     [{'id': 'id', 'flavor_id': 'flavor'}]),
    (['--node-group', 'id(count=10, flavor_id=flavor)'],
     [{'id': 'id', 'flavor_id': 'flavor', 'count': 10}]),
])
def test_create(args, node_groups, print_table, print_single_table,
                mock_client, cluster_response):
    mock_client._request.return_value = cluster_response

    base_args = ['lava2', 'clusters', 'create', 'name', 'username',
                 'keypair_name', 'stack_id']
    with patch('sys.argv', base_args + args):
        main()

        kwargs = mock_client._request.call_args[1]
        assert kwargs['json']['cluster'].get('node_groups') == node_groups


@patch('sys.argv', ['lava2', 'clusters', 'delete', 'cluster_id'])
def test_delete(mock_client):
    main()
    args = mock_client._request.call_args[0]

    assert args == ('DELETE', 'clusters/cluster_id')
