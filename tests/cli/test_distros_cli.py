from mock import patch

from lavaclient.cli import main
from lavaclient.api.response import DistroDetail, DistroService


@patch('sys.argv', ['lava2', 'distros', 'list'])
def test_list(print_table, mock_client, distros_response):
    mock_client._request.return_value = distros_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['HDP2.2', 'HortonWorks Data Platform', '2.2']]
    assert header == ['ID', 'Name', 'Version']
    assert kwargs['title'] is None


@patch('sys.argv', ['lava2', 'distros', 'get', 'distro_id'])
def test_get(print_table, print_single_table, mock_client, distro_response):
    mock_client._request.return_value = distro_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['HDP2.2', 'HortonWorks Data Platform', '2.2']
    assert header == DistroDetail.table_header
    assert kwargs['title'] is 'Distro'

    assert print_table.call_count == 1

    (data, header), kwargs = print_table.call_args_list[0]
    assert list(data) == [['name', 'version', '[{name=component}]',
                           'description']]
    assert header == DistroService.table_header
    assert kwargs['title'] == 'Services'
