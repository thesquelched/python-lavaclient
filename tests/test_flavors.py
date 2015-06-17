import pytest
from mock import patch

from lavaclient.api import response
from lavaclient import error


def test_list(lavaclient, flavors_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = flavors_response
        resp = lavaclient.flavors.list()

        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Flavor)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.flavors.list)
