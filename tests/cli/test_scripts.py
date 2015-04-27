import pytest
from mock import patch
from datetime import datetime

from lavaclient2.cli import main
from lavaclient2.api.response import Script


@patch('sys.argv', ['lava2', 'scripts', 'list'])
def test_list(print_table, mock_client, scripts_response):
    mock_client._request.return_value = scripts_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['id', 'name', 'POST_INIT', True,
                           datetime(2015, 1, 1), 'url']]
    assert header == Script.table_header
    assert kwargs['title'] is None


@patch('sys.argv', ['lava2', 'scripts', 'create', 'name', 'url', 'post_init'])
def test_create(print_single_table, mock_client, script_response):
    mock_client._request.return_value = script_response
    main()

    (data, header), kwargs = print_single_table.call_args
    assert data == ['id', 'name', 'POST_INIT', True, datetime(2015, 1, 1),
                    'url']
    assert header == Script.table_header
    assert kwargs['title'] is None


@pytest.mark.parametrize('name,url,script_type', [
    (None, None, None),
    (None, None, 'post_init'),
    (None, 'url', None),
    (None, 'url', 'post_init'),
    ('name', None, None),
    ('name', None, 'post_init'),
    ('name', 'url', None),
    ('name', 'url', 'post_init'),
])
def test_update(name, url, script_type, print_single_table,
                mock_client, script_response):
    mock_client._request.return_value = script_response
    args = ['lava2', 'scripts', 'update', 'script_id']
    if name:
        args.extend(['--name', name])
    if url:
        args.extend(['--url', url])
    if script_type:
        args.extend(['--type', script_type])

    with patch('sys.argv', args):
        main()

    kwargs = mock_client._request.call_args[1]
    assert kwargs['json']['script'].get('name') == name
    assert kwargs['json']['script'].get('url') == url

    stype = script_type.upper() if script_type else None
    assert kwargs['json']['script'].get('type') == stype

    (data, header), kwargs = print_single_table.call_args
    assert data == ['id', 'name', 'POST_INIT', True, datetime(2015, 1, 1),
                    'url']
    assert header == Script.table_header
    assert kwargs['title'] is None


@patch('sys.argv', ['lava2', 'scripts', 'delete', 'script_id'])
def test_delete(mock_client):
    main()
    args = mock_client._request.call_args[0]

    assert args == ('DELETE', 'scripts/script_id')
