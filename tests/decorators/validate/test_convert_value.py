import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ConversionError
from pedantic.decorators.fn_deco_validate.convert_value import convert_value


def test_convert_to_bool():
    for value in [True, 1, '1', '  1 ', '  tRuE  ', 'TRUE']:
        assert convert_value(value=value, target_type=bool) is True

    for value in [False, 0, '0', '  0 ', '  fAlSe  ', 'FALSE']:
        assert convert_value(value=value, target_type=bool) is False

    for value in ['alse', 0.1, '0.2', '  0000 ', 'Talse', 'Frue', 42]:
        with pytest.raises(expected_exception=ConversionError):
            convert_value(value=value, target_type=bool)


def test_convert_to_int():
    for value in range(-4, 4):
        assert convert_value(value=value, target_type=int) == value

    assert convert_value(value='42', target_type=int) == 42
    assert convert_value(value='  0000 ', target_type=int) == 0

    for value in ['alse', 'Talse', 'Frue', 0.2, '0.2']:
        with pytest.raises(expected_exception=ConversionError):
            convert_value(value=value, target_type=int)


def test_convert_to_float():
    for value in range(-4, 4):
        assert convert_value(value=value, target_type=float) == value

    assert convert_value(value=0.2, target_type=float) == 0.2
    assert convert_value(value='0.2', target_type=float) == 0.2
    assert convert_value(value='42', target_type=float) == 42
    assert convert_value(value='  0000 ', target_type=float) == 0

    for value in ['alse', 'Talse', 'Frue']:
        with pytest.raises(expected_exception=ConversionError):
            convert_value(value=value, target_type=float)


def test_convert_to_list():
    for value in [[], [1], ['1', '  1 '], ['  tRuE  ', 'TRUE']]:
        assert convert_value(value=value, target_type=list) == value

    assert convert_value(value='1,2,3', target_type=list) == ['1', '2', '3']


def test_convert_to_dict():
    for value in [{}, {1: 2}, {'1': '  1 '}, {1: '  tRuE  ', 2: 'TRUE'}]:
        assert convert_value(value=value, target_type=dict) == value

    assert convert_value(value='1:1,2:4,3:7', target_type=dict) == {'1': '1', '2': '4', '3': '7'}
