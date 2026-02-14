import os
from dataclasses import dataclass

from pedantic import validate, ExternalParameter, overrides, Validator, Parameter, Min, ReturnAs


@dataclass(frozen=True)
class Configuration:
    iterations: int
    max_error: float


class ConfigurationValidator(Validator):
    @overrides(Validator)
    def validate(self, value: Configuration) -> Configuration:
        if value.iterations < 1 or value.max_error < 0:
            self.raise_exception(msg=f'Invalid configuration: {value}', value=value)

        return value


class ConfigFromEnvVar(ExternalParameter):
    """ Reads the configuration from environment variables. """

    @overrides(ExternalParameter)
    def has_value(self) -> bool:
        return 'iterations' in os.environ and 'max_error' in os.environ

    @overrides(ExternalParameter)
    def load_value(self) -> Configuration:
        return Configuration(
            iterations=int(os.environ['iterations']),
            max_error=float(os.environ['max_error']),
        )


class ConfigFromFile(ExternalParameter):
    """ Reads the configuration from a config file. """

    @overrides(ExternalParameter)
    def has_value(self) -> bool:
        return os.path.isfile('config.csv')

    @overrides(ExternalParameter)
    def load_value(self) -> Configuration:
        with open(file='config.csv', mode='r') as file:
            content = file.readlines()
            return Configuration(
                iterations=int(content[0].strip('\n')),
                max_error=float(content[1]),
            )


# choose your configuration source here:
@validate(ConfigFromEnvVar(name='config', validators=[ConfigurationValidator()]), strict=False, return_as=ReturnAs.KWARGS_WITH_NONE)
# @validate(ConfigFromFile(name='config', validators=[ConfigurationValidator()]), strict=False)

# with strict_mode = True (which is the default)
# you need to pass a Parameter for each parameter of the decorated function
# @validate(
#     Parameter(name='value', validators=[Min(5, include_boundary=False)]),
#     ConfigFromFile(name='config', validators=[ConfigurationValidator()]),
# )
def my_algorithm(value: float, config: Configuration) -> float:
    """
        This method calculates something that depends on the given value with considering the configuration.
        Note how well this small piece of code is designed:
            - Fhe function my_algorithm() need a Configuration but has no knowledge where this come from.
            - Furthermore, it need does not care about parameter validation.
            - The ConfigurationValidator doesn't now anything about the creation of the data.
            - The @validate decorator is the only you need to change, if you want a different configuration source.
    """
    print(value)
    print(config)
    return value


if __name__ == '__main__':
    # we can call the function with a config like there is no decorator.
    # This makes testing extremely easy: no config files, no environment variables or stuff like that
    print(my_algorithm(value=2, config=Configuration(iterations=3, max_error=4.4)))

    os.environ['iterations'] = '12'
    os.environ['max_error'] = '3.1415'

    # but we also can omit the config and load it implicitly by our custom Parameters
    print(my_algorithm(value=42.0))
