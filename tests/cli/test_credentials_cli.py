from mock import patch, MagicMock

from lavaclient.cli import main


@patch('sys.argv', ['lava', 'credentials', 'list'])
def test_list(print_table, mock_client, credentials_response):
    mock_client._request.return_value = credentials_response
    main()

    assert print_table.call_count == 1
    (data, header), kwargs = print_table.call_args
    assert list(data) == [('SSH Key', 'mykey'),
                          ('Cloud Files', 'username'),
                          ('Amazon S3', 'access_key_id'),
                          ('Ambari', 'username')]
    assert header == ('Type', 'Name')
    assert kwargs['title'] == 'Credentials'


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


@patch('sys.argv', ['lava', 'credentials', 'list_s3'])
def test_list_s3(print_table, mock_client, s3_creds_response):
    mock_client._request.return_value = s3_creds_response
    main()

    assert print_table.call_count == 1
    (data, header), kwargs = print_table.call_args
    assert list(data) == [['Amazon S3', 'access_key_id']]
    assert header == ('Type', 'Access Key ID')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'list_ambari'])
def test_list_ambari(print_table, mock_client, ambari_creds_response):
    mock_client._request.return_value = ambari_creds_response
    main()

    assert print_table.call_count == 1
    (data, header), kwargs = print_table.call_args
    assert list(data) == [['Ambari', 'username']]
    assert header == ['Type', 'Username']
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


@patch('sys.argv', ['lava', 'credentials', 'create_s3', 'a' * 20,
                    'x' * 40])
def test_create_s3(print_single_table, mock_client,
                   s3_cred_response):
    mock_client._request.return_value = s3_cred_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['Amazon S3', 'access_key_id']
    assert header == ('Type', 'Access Key ID')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'create_ambari', 'username',
                    '--ambari-password', 'password'])
def test_create_ambari(print_single_table, mock_client, ambari_cred_response):
    mock_client._request.return_value = ambari_cred_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['Ambari', 'username']
    assert header == ['Type', 'Username']
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


@patch('sys.argv', ['lava', 'credentials', 'update_s3', 'a' * 20,
                    'x' * 40])
def test_update_s3(print_single_table, mock_client, s3_cred_response):
    mock_client._request.return_value = s3_cred_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['Amazon S3', 'access_key_id']
    assert header == ('Type', 'Access Key ID')
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'update_ambari', 'username',
                    '--ambari-password', 'password'])
def test_update_ambari(print_single_table, mock_client, ambari_cred_response):
    mock_client._request.return_value = ambari_cred_response
    main()

    assert print_single_table.call_count == 1
    (data, header), kwargs = print_single_table.call_args
    assert data == ['Ambari', 'username']
    assert header == ['Type', 'Username']
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'credentials', 'delete_ssh_key', 'name'])
@patch('lavaclient.api.credentials.confirm', MagicMock(return_value=True))
def test_delete_ssh_key(mock_client):
    mock_client._request.return_value = None
    main()


@patch('sys.argv', ['lava', 'credentials', 'delete_cloud_files',
                    'username'])
@patch('lavaclient.api.credentials.confirm', MagicMock(return_value=True))
def test_delete_cloud_files(mock_client):
    mock_client._request.return_value = None
    main()


@patch('sys.argv', ['lava', 'credentials', 'delete_s3', 'access_key_id'])
@patch('lavaclient.api.credentials.confirm', MagicMock(return_value=True))
def test_delete_s3(mock_client):
    mock_client._request.return_value = None
    main()


@patch('sys.argv', ['lava', 'credentials', 'delete_ambari', 'username'])
@patch('lavaclient.api.credentials.confirm', MagicMock(return_value=True))
def test_delete_ambari(mock_client):
    mock_client._request.return_value = None
    main()
