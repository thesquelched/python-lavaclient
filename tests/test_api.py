import pytest
import figgis


from lavaclient2.api import method
from lavaclient2 import error


@pytest.fixture
def apimethod():
    return method.ApiMethod()


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


def test_bad_wrapper(apimethod):
    class TestObject(object):
        field = None

    pytest.raises(AttributeError, apimethod.parse_response, {}, TestObject,
                  wrapper='nonexistent')


def test_parse_response(apimethod, response_class):
    resp1 = apimethod.parse_response({'field': 'value'}, response_class)
    assert resp1.field == 'value'

    resp2 = apimethod.parse_response({'field': 'value'}, response_class,
                                     wrapper='field')
    assert resp2 == 'value'


def test_bad_response(apimethod, response_class):
    pytest.raises(error.ApiError, apimethod.parse_response, {}, response_class)
    pytest.raises(error.ApiError, apimethod.parse_response,
                  {'field': 'badvalue'}, response_class)
