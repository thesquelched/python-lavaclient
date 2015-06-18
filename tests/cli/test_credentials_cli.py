from mock import patch

from lavaclient.cli import main


@patch('sys.argv', ['lava', 'credentials', 'list'])
@patch('lavaclient.api.credentials.print_table')
def test_list(print_table_, mock_client, credentials_response):
    mock_client._request.return_value = credentials_response
    main()

    assert print_table_.call_count == 1
    (data, header), kwargs = print_table_.call_args
    assert list(data) == [('SSH Key', 'mykey'), ('Cloud Files', 'username')]
    assert header == ('Type', 'Name')
    assert 'title' not in kwargs


@patch('sys.argv', ['lava', 'credentials', 'list_ssh_keys'])
def test_list_ssh_keys(print_table, mock_client, ssh_keys_response):
    mock_client._request.return_value = ssh_keys_response
    main()

    assert print_table.call_count == 1
    (data, header), kwargs = print_table.call_args
    assert list(data) == [['SSH Key', 'mykey']]
    assert header == ('Type', 'Name')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'list_cloud_files'])
def test_list_cloud_files(print_table, mock_client,
                          cloud_files_creds_response):
    mock_client._request.return_value = cloud_files_creds_response
    main()

    assert print_table.call_count == 1
    (data, header), kwargs = print_table.call_args
    assert list(data) == [['Cloud Files', 'username']]
    assert header == ('Type', 'Username')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'create_ssh_key', 'name',
                    'x' * 50])
def test_create_ssh_key(print_single_table, mock_client, ssh_key_response):
    mock_client._request.return_value = ssh_key_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['SSH Key', 'mykey']
    assert header == ('Type', 'Name')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'create_cloud_files', 'username',
                    'x' * 25])
def test_create_cloud_files(print_single_table, mock_client,
                            cloud_files_cred_response):
    mock_client._request.return_value = cloud_files_cred_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['Cloud Files', 'username']
    assert header == ('Type', 'Username')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'update_ssh_key', 'name',
                    'x' * 50])
def test_update_ssh_key(print_single_table, mock_client, ssh_key_response):
    mock_client._request.return_value = ssh_key_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['SSH Key', 'mykey']
    assert header == ('Type', 'Name')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'update_cloud_files', 'username',
                    'x' * 25])
def test_update_cloud_files(print_single_table, mock_client,
                            cloud_files_cred_response):
    mock_client._request.return_value = cloud_files_cred_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['Cloud Files', 'username']
    assert header == ('Type', 'Username')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'delete_ssh_key', 'name'])
def test_delete_ssh_key(mock_client):
    mock_client._request.return_value = None
    main()


@patch('sys.argv', ['lava', 'credentials', 'delete_cloud_files',
                    'username'])
def test_delete_cloud_files(mock_client):
    mock_client._request.return_value = None
    main()
