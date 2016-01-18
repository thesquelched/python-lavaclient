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

from lavaclient.client import Lava
from lavaclient import error


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
                            "region": "REGION",
                            "versionId": "2",
                            "versionInfo": "versionInfo",
                            "versionList": "versionList"
                        },
                    ],
                    "endpoints_links": []
                },
            ]
        }
    }


@patch('requests.Session.post')
def test_auth_client(post, auth_response):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response)
    )
    client = Lava('username', 'region', api_key='apikey', tenant_id='tenantId')

    assert post.call_count == 1
    assert client.token == 'ab48a9efdfedb23ty3494'
    assert client.endpoint == 'publicURL/v2/tenantId'


@patch.object(Lava, '_get_endpoint')
@patch('requests.Session.post')
def test_auth_endpoint(post, get_endpoint, auth_response):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response)
    )

    client1 = Lava('username', 'region', api_key='apikey',
                   endpoint='v2/tenant')

    assert get_endpoint.call_count == 0
    assert post.call_count == 1
    assert client1.token == 'ab48a9efdfedb23ty3494'
    assert client1.endpoint == 'v2/tenant'


@patch.object(Lava, '_get_endpoint')
@patch('requests.Session.post')
def test_auth_endpoint_validation(post, get_endpoint, auth_response):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response)
    )

    assert Lava('username',
                'region',
                api_key='apikey',
                endpoint='v2/tenant').endpoint == 'v2/tenant'
    assert Lava('username',
                'region',
                api_key='apikey',
                endpoint='v2',
                tenant_id='tenant').endpoint == 'v2/tenant'
    assert Lava('username',
                'region',
                api_key='apikey',
                endpoint='v2/tenant',
                tenant_id='tenant').endpoint == 'v2/tenant'

    pytest.raises(error.InvalidError, Lava, 'username',
                  'region', api_key='apikey', endpoint='foo')
    pytest.raises(error.InvalidError, Lava, 'username',
                  'region', api_key='apikey', endpoint='foo',
                  tenant_id='tenant')


@pytest.mark.parametrize('exc,username,call_kwargs', [
    (error.InvalidError, None, dict(token='token')),
    (error.InvalidError, 'username', dict()),
    (error.InvalidError, 'username', dict(token='token', region=None,
                                          endpoint=None)),
])
def test_client_auth_errors(exc, username, call_kwargs, auth_response):
    pytest.raises(exc, Lava, username, **call_kwargs)


def test_auth_error_service_catalog(auth_response):
    with patch('requests.Session.post') as post:
        post.return_value = MagicMock(
            json=MagicMock(return_value=auth_response)
        )
        pytest.raises(error.AuthenticationError, Lava, 'username',
                      region='badregion', api_key='apikey')
