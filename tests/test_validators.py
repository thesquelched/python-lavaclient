import pytest
from figgis import ValidationError
from lavaclient import validators


def test_range():
    validator = validators.Range(min=1, max=1)
    pytest.raises(ValidationError, validator, 0)
    pytest.raises(ValidationError, validator, 2)

    validator(1)


def test_length():
    validator = validators.Length(min=1, max=1)
    pytest.raises(ValidationError, validator, [])
    pytest.raises(ValidationError, validator, [1, 2])

    validator([1])
