import pytest
from mock import patch

from lavaclient.api.response import AbsoluteLimits
from lavaclient import error


def test_get(lavaclient, limits_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = limits_response
        resp = lavaclient.limits.get()

        assert isinstance(resp, AbsoluteLimits)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.limits.get)
