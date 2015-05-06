from mock import patch

from lavaclient2.cli import main
from lavaclient2.api.response import Node


@patch('sys.argv', ['lava2', 'nodes', 'list', 'cluster_id'])
def test_list(print_table, mock_client, nodes_response):
    mock_client._request.return_value = nodes_response
    main()

    (data, header), kwargs = print_table.call_args
    alldata = [entry for entry in list(data)[0]]
    assert alldata[:6] == ['node_id', 'NODENAME', '[]', 'ACTIVE', '1.2.3.4',
                           '5.6.7.8']
    assert header == Node.table_header
    assert kwargs['title'] is None
