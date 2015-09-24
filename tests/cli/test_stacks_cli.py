import pytest
import json
from mock import patch, MagicMock
from datetime import datetime

from lavaclient.cli import main
from lavaclient.api.response import StackDetail, StackNodeGroup


@pytest.fixture
def print_table_(request):
    patcher = patch('lavaclient.api.stacks.print_table')
    request.addfinalizer(patcher.stop)
    return patcher.start()


@patch('sys.argv', ['lava', 'stacks', 'list'])
def test_list(print_table_, mock_client, stacks_response):
    mock_client._request.return_value = stacks_response
    main()

    assert print_table_.call_count == 2
    (data, header), kwargs = print_table_.call_args_list[0]
    alldata = list(data)
    assert len(alldata) == 1
    assert list(item[:5] for item in alldata) == [[1,
                                                   'stack_id',
                                                   'stack_name',
                                                   'distro',
                                                   'description']]
    assert header == ['', 'ID', 'Name', 'Distro', 'Description']
    assert kwargs['title'] is 'Stacks'


@patch('sys.argv', ['lava', 'stacks', 'get', 'stack_id'])
def test_get(print_table, print_single_table, mock_client, stack_response):
    mock_client._request.return_value = stack_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data[:5] == ['stack_id', 'stack_name', 'distro',
                        datetime(2015, 1, 1), 'description']
    assert data[6] == 'id'
    pieces = list(sorted(data[5]
                         .strip('[]')
                         .strip('}{')
                         .replace('\n', '')
                         .split(',')))
    assert pieces == ['modes=[mode1]', 'name=service_name']
    assert header == StackDetail.table_header
    assert kwargs['title'] == 'Stack'

    assert print_table.call_count == 1

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['id', 'hadoop1-7', 10, 1024, 1, 10]]
    assert header == StackNodeGroup.table_header
    assert kwargs['title'] == 'Node Groups'


@pytest.mark.parametrize('services,node_groups', [
    ([], None),
    ([{'name': 'service1'}], None),
    ([{'name': 'service1', 'modes': []}], None),
    ([{'name': 'service1', 'modes': ['mode1']}], None),
    ([], [{'id': 'nodegroup'}]),
    ([], [{'id': 'nodegroup', 'flavor_id': 'hadoop1-7', 'count': 10}]),
    ([], [{'id': 'nodegroup', 'components': []}]),
    ([], [{'id': 'nodegroup', 'components': [{'name': 'component'}]}]),
    ([{'name': 'service1', 'modes': ['mode1']}],
     [{'id': 'nodegroup', 'components': [{'name': 'component'}]}]),
])
def test_create(services, node_groups, print_table, print_single_table,
                mock_client, stack_response):
    mock_client._request.return_value = stack_response

    args = ['lava', 'stacks', 'create', 'name', 'distro',
            json.dumps(services)]
    if node_groups:
        args.extend(['--node-groups', json.dumps(node_groups)])

    with patch('sys.argv', args):
        main()

    jsondata = mock_client._request.call_args[1]['json']['stack']
    assert jsondata['services'] == services
    if 'node_groups' in jsondata:
        assert jsondata['node_groups'] == node_groups

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data[:5] == ['stack_id', 'stack_name', 'distro',
                        datetime(2015, 1, 1), 'description']
    assert data[6] == 'id'
    pieces = list(sorted(data[5]
                         .strip('[]')
                         .strip('}{')
                         .replace('\n', '')
                         .split(',')))
    assert pieces == ['modes=[mode1]', 'name=service_name']
    assert header == StackDetail.table_header
    assert kwargs['title'] == 'Stack'

    assert print_table.call_count == 1

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['id', 'hadoop1-7', 10, 1024, 1, 10]]
    assert header == StackNodeGroup.table_header
    assert kwargs['title'] == 'Node Groups'


@patch('lavaclient.api.stacks.confirm', MagicMock(return_value=True))
@patch('sys.argv', ['lava', 'stacks', 'delete', 'stack_id'])
def test_delete(print_table, print_single_table, mock_client, stack_response):
    mock_client._request.return_value = stack_response
    main()
    args = mock_client._request.call_args[0]

    assert args == ('DELETE', 'stacks/stack_id')
