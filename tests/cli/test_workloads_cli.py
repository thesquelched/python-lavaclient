import pytest
from mock import patch

from lavaclient.cli import main
from lavaclient.api.workloads import Workload


@patch('sys.argv', ['lava', 'workloads', 'list'])
def test_list(print_table, mock_client, workloads_response):
    pytest.skip('Workloads is disabled for now')

    mock_client._request.return_value = workloads_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['id', 'name', 'caption', 'description']]
    assert header == Workload.table_header
    assert kwargs['title'] is None


@pytest.mark.parametrize('persistence', ['all', 'data', 'none'])
def test_recommendations(persistence, print_table, mock_client,
                         recommendations_response):
    pytest.skip('Workloads is disabled for now')

    mock_client._request.return_value = recommendations_response

    with patch('sys.argv', ['lava', 'workloads', 'recommendations', 'id',
                            '128', persistence]):
        main()

    params = mock_client._request.call_args[1]['params']
    assert params['storagesize'] == 128
    assert params['persistent'] == persistence

    (data, header), kwargs = print_table.call_args
    assert len(list(data)) == 1
    assert header == ('Name', 'Requires', 'Description', 'Flavor', 'Minutes',
                      'Nodes', 'Recommended')
    assert 'title' not in kwargs
