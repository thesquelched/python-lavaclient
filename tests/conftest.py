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
