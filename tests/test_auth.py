# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import pytest
from mock import patch, MagicMock
from keystoneclient import exceptions

from lavaclient2.client import Lava
from lavaclient2 import error
from lavaclient2 import keystone


@pytest.fixture
def auth_response():
    return {
        "access": {
            "token": {
                "id": "ab48a9efdfedb23ty3494",
                "expires": "2010-11-01T03:32:15-05:00",
                "tenant": {
                    "id": "tenantId",
                    "name": "tenantName"
                }
            },
            "user": {
                "id": "username",
                "name": "username",
                "roles": [
                    {
                        "id": "roleId",
                        "name": "tenantName",
                        "tenantId": "tenantId"
                    }
                ],
                "roles_links": []
            },
            "serviceCatalog": [
                {
                    "name": "cloudBigData",
                    "type": "rax:bigdata",
                    "endpoints": [
                        {
                            "tenantId": "tenantId",
                            "publicURL": "publicURL/v2/tenantId",
                            "internalURL": "internalURL",
                            "region": "region",
                            "versionId": "versionId",
                            "versionInfo": "versionInfo",
                            "versionList": "versionList"
                        },
                    ],
                    "endpoints_links": []
                },
            ]
        }
    }


@patch('keystoneclient.session.Session.post')
def test_auth_client(post, auth_response):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response)
    )
    client = Lava('apikey', 'username', 'region', tenant_id='tenantId')

    assert post.call_count == 1
    assert client.token == 'ab48a9efdfedb23ty3494'
    assert client.endpoint == 'publicURL/v2/tenantId'


@patch.object(Lava, '_get_endpoint')
@patch('keystoneclient.session.Session.post')
def test_auth_endpoint(post, get_endpoint, auth_response):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response)
    )

    client1 = Lava('apikey', 'username', 'region', endpoint='v2/tenant')

    assert get_endpoint.call_count == 0
    assert post.call_count == 1
    assert client1.token == 'ab48a9efdfedb23ty3494'
    assert client1.endpoint == 'v2/tenant'


@patch.object(Lava, '_get_endpoint')
@patch('keystoneclient.session.Session.post')
def test_auth_endpoint_validation(post, get_endpoint, auth_response):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response)
    )

    assert Lava('apikey',
                'username',
                'region',
                endpoint='v2/tenant').endpoint == 'v2/tenant'
    assert Lava('apikey',
                'username',
                'region',
                endpoint='v2',
                tenant_id='tenant').endpoint == 'v2/tenant'
    assert Lava('apikey',
                'username',
                'region',
                endpoint='v2/tenant',
                tenant_id='tenant').endpoint == 'v2/tenant'

    pytest.raises(error.InvalidError, Lava, 'apikey', 'username', 'region',
                  endpoint='foo')
    pytest.raises(error.InvalidError, Lava, 'apikey', 'username', 'region',
                  endpoint='v2/something', tenant_id='tenant')
    pytest.raises(error.InvalidError, Lava, 'apikey', 'username', 'region',
                  endpoint='foo', tenant_id='tenant')


def test_auth_errors(auth_response):
    pytest.raises(error.InvalidError, Lava, None, 'username', 'region')
    pytest.raises(error.InvalidError, Lava, 'apikey', None, 'region')
    pytest.raises(error.InvalidError, Lava, 'apikey', 'username', None)

    with patch('keystoneclient.session.Session.post') as post:
        post.return_value = MagicMock(status_code=400)
        pytest.raises(error.AuthenticationError, Lava, 'apikey', 'username',
                      'region')

    with patch('keystoneclient.session.Session.post') as post:
        post.side_effect = exceptions.Unauthorized
        pytest.raises(error.AuthorizationError, Lava, 'apikey', 'username',
                      'region')

    with patch('keystoneclient.session.Session.post') as post:
        post.side_effect = exceptions.EndpointNotFound
        pytest.raises(error.AuthenticationError, Lava, 'apikey', 'username',
                      'region')

    with patch('keystoneclient.session.Session.post') as post:
        post.return_value = MagicMock(
            json=MagicMock(return_value=auth_response)
        )
        pytest.raises(error.InvalidError, Lava, 'apikey', 'username',
                      'badregion')


def test_apikey_client_errors():
    pytest.raises(ValueError, keystone.ApiKeyClient,
                  api_key=None, username='username', region='region')
    pytest.raises(ValueError, keystone.ApiKeyClient,
                  api_key='api_key', username=None, region='region')
    pytest.raises(ValueError, keystone.ApiKeyClient,
                  api_key='api_key', username='username', region=None)
    pytest.raises(exceptions.AuthorizationFailure, keystone.ApiKeyClient,
                  api_key='api_key', username='username', region='region',
                  auth_url=None)
