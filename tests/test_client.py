from mock import patch, MagicMock
import pytest
import requests

from lavaclient import error
from lavaclient import __version__


@patch('uuid.uuid4')
def test_requests(uuid4, lavaclient):
    uuid4.return_value = 'uuid'

    with patch('requests.request') as request:
        lavaclient._get('path')
        request.assert_called_with(
            'GET', 'endpoint/path',
            verify=False,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})

    with patch('requests.request') as request:
        lavaclient._post('path')
        request.assert_called_with(
            'POST', 'endpoint/path',
            verify=False,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})

    with patch('requests.request') as request:
        lavaclient._put('path')
        request.assert_called_with(
            'PUT', 'endpoint/path',
            verify=False,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})

    with patch('requests.request') as request:
        lavaclient._delete('path')
        request.assert_called_with(
            'DELETE', 'endpoint/path',
            verify=False,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})


@patch('uuid.uuid4')
def test_headers(uuid4, lavaclient):
    uuid4.return_value = 'uuid'

    with patch('requests.request') as request:
        lavaclient._get('path', headers={'foo': 'bar'})
        request.assert_called_with(
            'GET', 'endpoint/path',
            verify=False,
            headers={'foo': 'bar',
                     'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})


def test_reauthenticate(lavaclient):
    lavaclient._authenticate = MagicMock(
        return_value=MagicMock(
            auth_token='auth_token',
            service_catalog=MagicMock(
                url_for=MagicMock(
                    return_value='endpoint'
                )
            )
        )
    )

    with patch('requests.request') as request:
        # First call mocks 401 error, second call goes through
        request.side_effect = [
            MagicMock(raise_for_status=MagicMock(
                side_effect=requests.exceptions.HTTPError(
                    response=MagicMock(status_code=requests.codes.unauthorized)
                )
            )),
            MagicMock(
                json=MagicMock(return_value={'key': 'value'})
            )
        ]
        result = lavaclient._get('path')
        assert result == {'key': 'value'}
        assert request.call_count == 2


def test_reauthenticate_failure(lavaclient):
    lavaclient._authenticate = MagicMock(
        return_value=MagicMock(
            auth_token='auth_token',
            service_catalog=MagicMock(
                url_for=MagicMock(
                    return_value='endpoint'
                )
            )
        )
    )

    with patch('requests.request') as request:
        request.return_value = MagicMock(raise_for_status=MagicMock(
            side_effect=requests.exceptions.HTTPError(
                response=MagicMock(status_code=requests.codes.unauthorized)
            )
        ))

        pytest.raises(error.AuthorizationError, lavaclient._get, 'path')
        assert request.call_count == 2


@patch('requests.request')
def test_http_error(request, lavaclient):
    request.return_value = MagicMock(
        raise_for_status=MagicMock(
            side_effect=requests.exceptions.HTTPError(
                response=MagicMock(
                    status_code=requests.codes.internal_server_error
                )
            )
        )
    )

    pytest.raises(error.RequestError, lavaclient._get, 'path')


@patch('requests.request')
def test_request_exception(request, lavaclient):
    request.return_value = MagicMock(
        raise_for_status=MagicMock(
            side_effect=requests.exceptions.RequestException
        )
    )

    pytest.raises(error.RequestError, lavaclient._get, 'path')
