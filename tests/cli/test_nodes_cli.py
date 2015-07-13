from mock import patch

from lavaclient.cli import main
from lavaclient.api.response import Node


@patch('sys.argv', ['lava', 'nodes', 'list', 'cluster_id'])
@patch('lavaclient.api.response.print_table')
def test_list(resp_print_table, print_table, mock_client, nodes_response):
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
