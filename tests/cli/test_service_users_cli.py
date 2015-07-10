from mock import patch

from lavaclient.cli import main


@patch('sys.argv', ['lava', 'service_users', 'list', 'cluster_id'])
def test_list(print_table, mock_client, service_users_response):
    mock_client._request.return_value = service_users_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['AMBARI', 'username']]
    assert header == ['Service', 'Username']
    assert kwargs['title'] is None


@patch('sys.argv', ['lava', 'service_users', 'reset_ambari_password',
                    'cluster_id'])
def test_create(print_single_table, mock_client, service_user_response):
    mock_client._request.return_value = service_user_response
    main()

    (data, header), kwargs = print_single_table.call_args
    assert data == ['AMBARI', 'username', 'password']
    assert header == ['Service', 'Username', 'Password']
    assert kwargs['title'] is None
