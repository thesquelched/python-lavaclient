import pytest
from mock import patch

from lavaclient2.api import response
from lavaclient2 import error


def test_list(lavaclient, distros_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = distros_response
        resp = lavaclient.distros.list()

        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Distro)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.distros.list)


def test_get(lavaclient, distro_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = distro_response
        resp = lavaclient.distros.get('HDP2.2')

        assert isinstance(resp, response.DistroDetail)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.distros.get, 'HDP2.2')
