import pytest
from mock import patch

from lavaclient2.api import response
from lavaclient2 import error


def test_list(lavaclient, flavor_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'flavors': [flavor_response]}
        resp = lavaclient.flavors.list()

        assert isinstance(resp, list)
        assert len(resp) == 1
        assert isinstance(resp[0], response.Flavor)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.flavors.list)


def test_get(lavaclient, flavor_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = {'flavor': flavor_response}
        resp = lavaclient.flavors.get('hadoop1-15')

        assert isinstance(resp, response.Flavor)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.flavors.get, 'hadoop1-15')
