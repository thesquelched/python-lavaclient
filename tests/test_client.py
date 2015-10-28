from mock import patch, MagicMock
import pytest
import requests

from lavaclient import constants
from lavaclient import error
from lavaclient import __version__


@patch('uuid.uuid4')
def test_requests(uuid4, lavaclient):
    uuid4.return_value = 'uuid'

    with patch('requests.sessions.Session.request') as request:
        lavaclient._get('path')
        request.assert_called_with(
            'GET', 'v2/tenant_id/path',
            verify=False,
            timeout=constants.DEFAULT_TIMEOUT,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})

    with patch('requests.sessions.Session.request') as request:
        lavaclient._post('path')
        request.assert_called_with(
            'POST', 'v2/tenant_id/path',
            verify=False,
            timeout=constants.DEFAULT_TIMEOUT,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})

    with patch('requests.sessions.Session.request') as request:
        lavaclient._put('path')
        request.assert_called_with(
            'PUT', 'v2/tenant_id/path',
            verify=False,
            timeout=constants.DEFAULT_TIMEOUT,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})

    with patch('requests.sessions.Session.request') as request:
        lavaclient._delete('path')
        request.assert_called_with(
            'DELETE', 'v2/tenant_id/path',
            verify=False,
            timeout=constants.DEFAULT_TIMEOUT,
            headers={'X-Auth-Token': 'auth_token',
                     'Client-Request-ID': 'uuid',
                     'User-Agent': 'python-lavaclient {0}'.format(
                         __version__)})


@patch('uuid.uuid4')
def test_headers(uuid4, lavaclient):
    uuid4.return_value = 'uuid'

    with patch('requests.sessions.Session.request') as request:
        lavaclient._get('path', headers={'foo': 'bar'})
        request.assert_called_with(
            'GET', 'v2/tenant_id/path',
            verify=False,
            timeout=constants.DEFAULT_TIMEOUT,
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

    with patch('requests.sessions.Session.request') as request:
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

    with patch('requests.sessions.Session.request') as request:
        request.return_value = MagicMock(raise_for_status=MagicMock(
            side_effect=requests.exceptions.HTTPError(
                response=MagicMock(status_code=requests.codes.unauthorized)
            )
        ))

        pytest.raises(error.AuthorizationError, lavaclient._get, 'path')
        assert request.call_count == 2


@patch('requests.sessions.Session.request')
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

    try:
        lavaclient._get('path')
    except error.RequestError as exc:
        exception = exc
    else:
        pytest.fail('Did not catch RequestError')

    assert exception.code == requests.codes.internal_server_error


@patch('requests.sessions.Session.request')
def test_request_exception(request, lavaclient):
    request.return_value = MagicMock(
        raise_for_status=MagicMock(
            side_effect=requests.exceptions.RequestException
        )
    )

    pytest.raises(error.RequestError, lavaclient._get, 'path')
