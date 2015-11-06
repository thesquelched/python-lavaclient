from mock import patch, call

from lavaclient.cli import main
from lavaclient.api.response import Node


@patch('sys.argv', ['lava', 'nodes', 'list', 'cluster_id'])
def test_list(print_table, mock_client, nodes_response):
    mock_client._request.return_value = nodes_response
    main()

    assert print_table.call_count == 2

    (data, header), kwargs = print_table.call_args_list[0]
    alldata = [entry for entry in list(data)[0]]
    assert alldata[:6] == ['node_id', 'NODENAME', 'node_group', 'ACTIVE',
                           '1.2.3.4', '5.6.7.8']
    assert header == Node.table_header
    assert kwargs['title'] == 'Nodes'

    (data, header), kwargs = print_table.call_args_list[1]
    alldata = [entry for entry in list(data)[0]]
    assert alldata[:6] == ['NODENAME', 'component_name', 'Component name',
                           'http://host']
    assert header == ('Node', 'ID', 'Name', 'URI')
    assert kwargs['title'] == 'Components'


@patch('sys.argv', ['lava', 'nodes', 'list', 'cluster_id', '--no-format'])
@patch('lavaclient.cli.six.print_')
def test_list_noformat(sixprint, mock_client, nodes_response):
    mock_client._request.return_value = nodes_response
    main()

    sixprint.assert_has_calls([
        call('node_id,NODENAME,node_group,ACTIVE,1.2.3.4,5.6.7.8')
    ])
