import pytest
from mock import patch

from lavaclient.api import limits
from lavaclient import error


def test_get(lavaclient, limits_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = limits_response
        resp = lavaclient.limits.get()

        assert isinstance(resp, limits.Limit)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.limits.get)


def test_limit_repr(absolute_limit):
    alimit = limits.AbsoluteLimit(absolute_limit)
    assert repr(alimit) == 'AbsoluteLimit(limit=10, remaining=0)'
