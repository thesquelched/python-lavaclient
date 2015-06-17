import pytest
import figgis


from lavaclient.api import resource
from lavaclient import error


@pytest.fixture
def apiresource():
    return resource.Resource(None)


@pytest.fixture
def field_validator():
    def validator(value):
        return value == 'value'
    return validator


@pytest.fixture
def response_class(field_validator):
    class Response(figgis.Config):
        field = figgis.Field(required=True, validator=field_validator)

    return Response


def test_bad_wrapper(apiresource):
    class TestObject(object):
        field = None

    pytest.raises(AttributeError, apiresource._parse_response, {}, TestObject,
                  wrapper='nonexistent')


def test_parse_response(apiresource, response_class):
    resp1 = apiresource._parse_response({'field': 'value'}, response_class)
    assert resp1.field == 'value'

    resp2 = apiresource._parse_response(
        {'field': 'value'}, response_class, wrapper='field')
    assert resp2 == 'value'


def test_bad_response(apiresource, response_class):
    pytest.raises(error.ApiError, apiresource._parse_response, {},
                  response_class)
    pytest.raises(error.ApiError, apiresource._parse_response,
                  {'field': 'badvalue'}, response_class)


def test_bad_request(apiresource, response_class):
    pytest.raises(error.InvalidError, apiresource._marshal_request, {},
                  response_class)
    pytest.raises(error.InvalidError, apiresource._marshal_request,
                  {'field': 'badvalue'}, response_class)


def test_marshal_request(apiresource, response_class):
    request1 = apiresource._marshal_request({'field': 'value'}, response_class)
    assert isinstance(request1, dict)
    assert request1 == {'field': 'value'}

    request2 = apiresource._marshal_request({'field': 'value'},
                                            response_class, wrapper='wrapper')
    assert isinstance(request2, dict)
    assert request2 == {'wrapper': {'field': 'value'}}
