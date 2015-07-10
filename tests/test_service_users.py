from mock import patch

from lavaclient.api.response import ServiceUser, ServiceUserDetail


def test_api_list(lavaclient, service_users_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = service_users_response

        resp = lavaclient.service_users.list('cluster_id')
        request.assert_called_with('GET', 'clusters/cluster_id/service_users')

        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], ServiceUser)


def test_api_reset_ambari_password(lavaclient, service_user_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = service_user_response

        resp = lavaclient.service_users.reset_ambari_password('cluster_id')
        request.assert_called_with(
            'PUT', 'clusters/cluster_id/service_users',
            json={'service_user': {'service': 'AMBARI',
                                   'username': 'username'}})

        assert isinstance(resp, ServiceUserDetail)
