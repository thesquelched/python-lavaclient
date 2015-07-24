import socks
import subprocess
import pytest
from mock import patch, call, MagicMock
from datetime import datetime
from copy import deepcopy
from six.moves import StringIO
from contextlib import contextmanager

from lavaclient.cli import main
from lavaclient.api.response import Cluster, ClusterDetail, NodeGroup, Node
from lavaclient.api.clusters import DEFAULT_SSH_KEY
from lavaclient.error import RequestError


@patch('sys.argv', ['lava', 'clusters', 'list'])
def test_list(print_table, mock_client, clusters_response):
    mock_client._request.return_value = clusters_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['cluster_id', 'cluster_name', 'ACTIVE',
                           'stack_id', datetime(2014, 1, 1)]]
    assert header == Cluster.table_header
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'clusters', 'get', 'cluster_id'])
def test_get(print_table, print_single_table, mock_client, cluster_response):
    mock_client._request.return_value = cluster_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['cluster_id', 'cluster_name', 'ACTIVE', 'stack_id',
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
def test_create_node_groups(args, node_groups, print_table,
                            print_single_table, mock_client,
                            cluster_response):
    mock_client._request.return_value = cluster_response

    base_args = ['lava', 'clusters', 'create', 'name', 'stack_id']
    with patch('sys.argv', base_args + args):
        main()

        kwargs = mock_client._request.call_args[1]
        assert kwargs['json']['cluster'].get('node_groups') == node_groups


@pytest.mark.parametrize('args,keys', [
    ([], [DEFAULT_SSH_KEY]),
    (['--ssh-key', 'key1'], ['key1']),
    (['--ssh-key', 'key1', '--ssh-key', 'key2'], ['key1', 'key2']),
])
def test_create_ssh_keys(args, keys, mock_client, print_table,
                         print_single_table, cluster_response):
    mock_client._request.return_value = cluster_response

    base_args = ['lava', 'clusters', 'create', 'name', 'stack_id']
    with patch('sys.argv', base_args + args):
        main()

        kwargs = mock_client._request.call_args[1]
        assert kwargs['json']['cluster'].get('ssh_keys') == keys


@contextmanager
def mock_keyfile(*args, **kwargs):
    yield StringIO('a' * 50)


@pytest.mark.usefixtures('print_table', 'print_single_table')
@patch('sys.argv', ['lava', 'clusters', 'create', 'name', 'stack_id'])
@patch('lavaclient.api.clusters.open', mock_keyfile, create=True)
@patch('lavaclient.api.clusters.confirm')
def test_create_no_ssh_key(confirm, mock_client, cluster_response,
                           ssh_key_response):
    mock_client._request.side_effect = [
        RequestError('Cannot find requested ssh_keys: {0}'.format(
            [DEFAULT_SSH_KEY])),
        ssh_key_response,
        cluster_response,
    ]
    confirm.return_value = True

    with patch.object(mock_client.clusters._args, 'headless', False):
        main()

    assert confirm.called
    assert mock_client._request.call_count == 3


@pytest.mark.usefixtures('print_table', 'print_single_table')
@patch('sys.argv', ['lava', 'clusters', 'create', 'name', 'stack_id'])
@patch('lavaclient.api.clusters.open', mock_keyfile, create=True)
def test_create_no_ssh_key_headless(mock_client, cluster_response,
                                    ssh_key_response):
    mock_client._request.side_effect = [
        RequestError('Cannot find requested ssh_keys: {0}'.format(
            [DEFAULT_SSH_KEY])),
    ]

    pytest.raises(Exception, main)

    assert mock_client._request.call_count == 1


@pytest.mark.usefixtures('print_table', 'print_single_table')
@patch('sys.argv', ['lava', 'clusters', 'create', 'name', 'stack_id',
                    '--ssh-key', 'mykey'])
def test_create_missing_ssh_key(mock_client, cluster_response):
    mock_client._request.side_effect = RequestError(
        'Cannot find requested ssh_keys: mykey')

    pytest.raises(Exception, main)
    assert mock_client._request.call_count == 1


def test_create_with_scripts(print_table, print_single_table, mock_client,
                             cluster_response):
    mock_client._request.return_value = cluster_response

    with patch('sys.argv', ['lava', 'clusters', 'create', 'name', 'stack_id',
                            '--user-script', 'id1', '--user-script', 'id2']):
        main()
        kwargs = mock_client._request.call_args[1]
        assert kwargs['json']['cluster'].get('scripts') == [{'id': 'id1'},
                                                            {'id': 'id2'}]


@pytest.mark.parametrize('args,node_groups', [
    (['--node-group', 'id(count=10)'], [{'id': 'id', 'count': 10}]),
    (['--node-group', 'id1(count=10)', '--node-group', 'id2(count=3)'],
     [{'id': 'id1', 'count': 10}, {'id': 'id2', 'count': 3}]),
])
def test_resize(args, node_groups, print_table, print_single_table,
                mock_client, cluster_response):
    mock_client._request.return_value = cluster_response

    base_args = ['lava', 'clusters', 'resize', 'cluster_id']

    with patch('sys.argv', base_args + args):
        main()

        kwargs = mock_client._request.call_args[1]
        assert kwargs['json']['cluster'].get('node_groups') == node_groups


@patch('sys.argv', ['lava', 'clusters', 'delete', 'cluster_id'])
@patch('lavaclient.api.clusters.confirm', MagicMock(return_value=True))
def test_delete(mock_client, cluster_response, print_single_table):
    mock_client._request.return_value = cluster_response

    main()
    assert mock_client._request.call_count == 2

    call1, call2 = mock_client._request.call_args_list

    assert call1[0] == ('GET', 'clusters/cluster_id')
    assert call2[0] == ('DELETE', 'clusters/cluster_id')


@patch('sys.argv', ['lava', 'clusters', 'wait', 'cluster_id'])
@patch('lavaclient.api.clusters.elapsed_minutes',
       MagicMock(side_effect=[0.0, 1.0, 2.0]))
@patch('time.sleep', MagicMock)
@patch('sys.stdout')
def test_wait(stdout, print_table, print_single_table, mock_client,
              cluster_response):
    building = deepcopy(cluster_response)
    building['cluster']['status'] = 'BUILDING'
    configuring = deepcopy(cluster_response)
    configuring['cluster']['status'] = 'CONFIGURING'
    active = deepcopy(cluster_response)
    active['cluster']['status'] = 'ACTIVE'

    mock_client._request.side_effect = [building, configuring, active]

    with patch.object(mock_client.clusters, '_command_line', True):
        main()
        stdout.write.assert_has_calls([
            call('Waiting for cluster cluster_id'),
            call('\n'),
            call('Status: BUILDING (Elapsed time: 0.0 minutes)'),
            call('{0}Status: CONFIGURING (Elapsed time: 1.0 minutes)'.format(
                '\b' * 44)),
            call('{0}Status: ACTIVE (Elapsed time: 2.0 minutes)'.format(
                '\b' * 47)),
        ])

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['cluster_id', 'cluster_name', 'ACTIVE', 'stack_id',
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


@patch('sys.argv', ['lava', 'clusters', 'nodes', 'cluster_id'])
@patch('lavaclient.api.response.print_table')
def test_nodes(resp_print_table, print_table, mock_client, nodes_response):
    mock_client._request.return_value = nodes_response
    main()

    (data, header), kwargs = print_table.call_args
    alldata = [entry for entry in list(data)[0]]
    assert alldata[:6] == ['node_id', 'NODENAME', '[]', 'ACTIVE', '1.2.3.4',
                           '5.6.7.8']
    assert header == Node.table_header
    assert kwargs['title'] == 'Nodes'

    (data, header), kwargs = resp_print_table.call_args
    alldata = [entry for entry in list(data)[0]]
    assert alldata[:6] == ['NODENAME', 'component_name', 'Component name',
                           'http://host']
    assert header == ('Node', 'ID', 'Name', 'URI')
    assert kwargs['title'] == 'Components'


@patch('subprocess.Popen')
def test_ssh_proxy(popen, mock_client, cluster_response, nodes_response):
    del nodes_response['nodes'][0]['components'][0]['uri']

    popen.return_value = MagicMock(
        poll=MagicMock(return_value=None),
        communicate=MagicMock(return_value=('stdout', 'stderr'))
    )
    mock_client._request.side_effect = [cluster_response, nodes_response]

    with patch('sys.argv', ['lava', 'clusters', 'ssh_proxy', 'cluster_id',
                            '--node-name', 'NODENAME', '--port', '54321']):
        main()

    popen.assert_called_with(
        ['ssh', '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes',
         '-N', '-D', '54321', 'username@1.2.3.4'],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE)


@pytest.mark.parametrize('failure', [None,
                                     socks.ProxyConnectionError,
                                     socks.GeneralProxyError])
@patch('subprocess.Popen')
@patch('lavaclient.util.test_socks_connection')
def test_ssh_proxy_errors(test_connection, popen, failure, mock_client,
                          cluster_response, nodes_response):
    del nodes_response['nodes'][0]['components'][0]['uri']

    popen.return_value = MagicMock(
        poll=MagicMock(return_value=None),
        communicate=MagicMock(return_value=('stdout', 'stderr'))
    )
    if failure:
        test_connection.side_effect = [failure, 200]
    else:
        test_connection.return_value = 200

    mock_client._request.side_effect = [cluster_response, nodes_response]

    with patch('sys.argv', ['lava', 'clusters', 'ssh_proxy', 'cluster_id',
                            '--node-name', 'NODENAME', '--port',
                            '54321']):
        main()

    popen.assert_called_with(
        ['ssh', '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes',
         '-N', '-D', '54321', 'username@1.2.3.4'],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE)


@patch('subprocess.Popen')
def test_ssh_proxy_cmd_fail(popen, mock_client, cluster_response,
                            nodes_response):
    popen.return_value = MagicMock(
        poll=MagicMock(return_value=1),
        communicate=MagicMock(return_value=('stdout', 'stderr'))
    )
    mock_client._request.side_effect = [cluster_response, nodes_response]

    with patch('sys.argv', ['lava', 'clusters', 'ssh_proxy', 'cluster_id',
                            '--node-name', 'NODENAME', '--port',
                            '54321']):
        pytest.raises(Exception, main)


@pytest.mark.parametrize('error_code', [400, 500])
@patch('subprocess.Popen')
@patch('lavaclient.util.test_socks_connection')
def test_ssh_proxy_http_fail(test_connection, popen, error_code, mock_client,
                             cluster_response, nodes_response):
    popen.return_value = MagicMock(
        poll=MagicMock(return_value=None),
        communicate=MagicMock(return_value=('stdout', 'stderr'))
    )
    test_connection.return_value = error_code
    mock_client._request.side_effect = [cluster_response, nodes_response]

    with patch('sys.argv', ['lava', 'clusters', 'ssh_proxy', 'cluster_id',
                            '--node-name', 'NODENAME', '--port',
                            '54321']):
        pytest.raises(Exception, main)


@patch('subprocess.Popen')
def test_ssh_tunnel_nodename(popen, mock_client, cluster_response,
                             nodes_response):
    popen.return_value = MagicMock(
        poll=MagicMock(return_value=None),
        communicate=MagicMock(return_value=('stdout', 'stderr'))
    )
    mock_client._request.side_effect = [cluster_response, nodes_response]

    with patch('sys.argv', ['lava', 'clusters', 'ssh_tunnel', 'cluster_id',
                            '123', '456', '--node-name', 'NODENAME']):
        main()

    popen.assert_called_with(
        ['ssh', '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes',
         '-N', '-L', '123:NODENAME:456', 'username@1.2.3.4'],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE)


@patch('subprocess.Popen')
def test_ssh_tunnel_component(popen, mock_client, cluster_response,
                              nodes_response):
    popen.return_value = MagicMock(
        poll=MagicMock(return_value=None),
        communicate=MagicMock(return_value=('stdout', 'stderr'))
    )
    mock_client._request.side_effect = [cluster_response, nodes_response]

    with patch('sys.argv', ['lava', 'clusters', 'ssh_tunnel', 'cluster_id',
                            '123', '456', '--component', 'component_name']):
        main()

    popen.assert_called_with(
        ['ssh', '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes',
         '-N', '-L', '123:NODENAME:456', 'username@1.2.3.4'],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE)


def test_ssh_tunnel_arg_failure(mock_client):
    with patch('sys.argv', ['lava', 'clusters', 'ssh_tunnel', 'cluster_id',
                            '123', '456', '--component', 'component_name',
                            '--node-name', 'NODENAME']):
        pytest.raises(Exception, main)
