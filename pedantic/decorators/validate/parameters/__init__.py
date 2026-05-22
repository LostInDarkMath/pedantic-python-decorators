from .abstract_external_parameter import ExternalParameter
from .abstract_parameter import Parameter
from .deserializable import Deserializable
from .environment_variable_parameter import EnvironmentVariableParameter

__all__ = [
    'Deserializable',
    'EnvironmentVariableParameter',
    'ExternalParameter',
    'Parameter',
]

try:
    from .flask_parameters import (
        FlaskFormParameter,
        FlaskGetParameter,
        FlaskHeaderParameter,
        FlaskJsonParameter,
        FlaskParameter,
        FlaskPathParameter,
        GenericFlaskDeserializer,
    )

    __all__ += [
        'FlaskFormParameter',
        'FlaskGetParameter',
        'FlaskHeaderParameter',
        'FlaskJsonParameter',
        'FlaskParameter',
        'FlaskPathParameter',
        'GenericFlaskDeserializer',
    ]
except ImportError:
    pass  # no Flask installed
