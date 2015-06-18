import pytest
from mock import patch

from lavaclient.cli import main


@pytest.fixture
def print_table(request):
    # Override from conftest because limits imports the function directly
    patcher = patch('lavaclient.api.limits.print_table')
    request.addfinalizer(patcher.stop)
    return patcher.start()


@patch('sys.argv', ['lava', 'limits', 'get'])
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
