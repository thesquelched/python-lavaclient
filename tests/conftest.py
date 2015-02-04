from mock import patch, MagicMock
import pytest

from lavaclient2 import client


@pytest.fixture
def lavaclient():
    with patch.object(client.Lava, 'authenticate') as auth:
        auth.return_value = MagicMock(
            auth_token='auth_token',
            service_catalog=MagicMock(
                url_for=MagicMock(
                    return_value='endpoint'
                )
            )
        )
        return client.Lava('api_key',
                           'username',
                           'region',
                           auth_url='auth_url',
                           tenant_id='tenant_id',
                           verify_ssl=False)


@pytest.fixture
def link_response():
    return {
        'rel': 'rel',
        'href': 'href',
    }


@pytest.fixture
def flavor_response(link_response):
    return {
        'id': 'hadoop1-15',
        'name': 'Medium Hadoop Instance',
        'vcpus': 4,
        'ram': 15360,
        'disk': 2500,
        'links': [link_response],
    }
