from pedantic import Parameter


def test_parameter_str():
    assert str(Parameter(name='a')) == 'Parameter name=a'
