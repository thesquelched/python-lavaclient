from keystoneclient.exceptions import VersionNotAvailable
from mock import patch, MagicMock
import pytest

from lavaclient import Lava, error

auth_response = {
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
        }
    }
}


@pytest.fixture
def auth_response_w_versions():
    service_catalog_list = [
        {
            "name": "cloudBigData",
                    "type": "rax:bigdata",
                    "endpoints": [
                        {
                            "tenantId": "tenantId",
                            "publicURL": "publicURL/v2/tenantId",
                            "internalURL": "internalURL",
                            "region": "DFW",
                            "versionId": "2",
                            "versionInfo": "versionInfo",
                            "versionList": "versionList"
                        },
                        {
                            "tenantId": "tenantId",
                            "publicURL": "publicURL/v1/tenantId",
                            "internalURL": "internalURL",
                            "region": "DFW",
                            "versionId": "1",
                            "versionInfo": "versionInfo",
                            "versionList": "versionList"
                        },
                    ],
            "endpoints_links": []
        },
    ]

    auth_response['access']['serviceCatalog'] = service_catalog_list
    return auth_response


@pytest.fixture
def auth_response_w_incorrect_version():
    service_catalog_list = [
        {
            "name": "cloudBigData",
                    "type": "rax:bigdata",
                    "endpoints": [
                        {
                            "tenantId": "tenantId",
                            "publicURL": "publicURL/v3/tenantId",
                            "internalURL": "internalURL",
                            "region": "DFW",
                            "versionId": "3",
                            "versionInfo": "versionInfo",
                            "versionList": "versionList"
                        }
                    ],
            "endpoints_links": []
        },
    ]
    auth_response['access']['serviceCatalog'] = service_catalog_list
    return auth_response


@pytest.fixture
def auth_response_default():
    service_catalog_list = [
        {
            "name": "cloudBigData",
                    "type": "rax:bigdata",
                    "endpoints": [
                        {
                            "tenantId": "tenantId",
                            "publicURL": "publicURL/v1/tenantId",
                            "internalURL": "internalURL",
                            "region": "DFW"
                        }
                    ],
            "endpoints_links": []
        },
    ]
    auth_response['access']['serviceCatalog'] = service_catalog_list
    return auth_response


@patch('keystoneclient.session.Session.post')
def test_v2_endpoint(post, auth_response_w_versions):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response_w_versions)
    )
    client = Lava('username', 'DFW', api_key='apikey', tenant_id='tenantId')

    assert post.call_count == 1
    assert client.endpoint == 'publicURL/v2/tenantId'


@patch('keystoneclient.session.Session.post')
def test_default_endpoint(post, auth_response_default):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response_default)
    )
    with pytest.raises(error.InvalidError):
        Lava('username', 'DFW', api_key='apikey', tenant_id='tenantId')


@patch('keystoneclient.session.Session.post')
def test_incorrect_endpoint(post, auth_response_w_incorrect_version):
    post.return_value = MagicMock(
        json=MagicMock(return_value=auth_response_w_incorrect_version)
    )

    with pytest.raises(VersionNotAvailable):
        Lava('username', 'DFW', api_key='apikey')
