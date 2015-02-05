import pytest
from mock import patch

from lavaclient2.api import response
from lavaclient2 import error


def test_list(lavaclient, distro_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'distros': [distro_fixture]}
        resp = lavaclient.distros.list()

        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Distro)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.distros.list)


def test_get(lavaclient, distro_fixture):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'distro': distro_fixture}
        resp = lavaclient.distros.get('hadoop1-15')

        assert isinstance(resp, response.Distro)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.distros.get, 'hadoop1-15')
