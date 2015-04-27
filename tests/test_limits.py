import pytest
from mock import patch

from lavaclient2.api import limits
from lavaclient2 import error


@pytest.fixture
def absolute_limit():
    return {
        'limit': 10,
        'remaining': 0,
    }


@pytest.fixture
def absolute_limits(absolute_limit):
    return {
        'node_count': absolute_limit,
        'ram': absolute_limit,
        'disk': absolute_limit,
        'vcpus': absolute_limit,
    }


@pytest.fixture
def limit(absolute_limits, link_response):
    return {
        'absolute': absolute_limits,
        'links': [link_response]
    }


@pytest.fixture
def limit_response(limit):
    return {'limits': limit}


def test_get(lavaclient, limit_response):
    with patch.object(lavaclient, '_request') as request:
        request.return_value = limit_response
        resp = lavaclient.limits.get()

        assert isinstance(resp, limits.Limit)

    with patch.object(lavaclient, '_request') as request:
        request.return_value = {}
        pytest.raises(error.ApiError, lavaclient.limits.get)


def test_limit_repr(absolute_limit):
    alimit = limits.AbsoluteLimit(absolute_limit)
    assert repr(alimit) == 'AbsoluteLimit(limit=10, remaining=0)'
