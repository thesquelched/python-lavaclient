from mock import patch

from lavaclient.cli import main


@patch('sys.argv', ['lava', 'limits', 'get'])
@patch('lavaclient.api.response.print_table')
def test_get(print_table, mock_client, limits_response):
    mock_client._request.return_value = limits_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [
        ('Nodes', 10, 0),
        ('RAM', 10, 0),
        ('Disk', 10, 0),
        ('VCPUs', 10, 0),
    ]
    assert header == ('Property', 'Limit', 'Remaining')
    assert kwargs['title'] is 'Quotas'
