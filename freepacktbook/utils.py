from os import environ


class ImproperlyConfiguredError(Exception):
    pass


def check_config(variables):
    for variable in variables:
        if variable not in environ:
            raise ImproperlyConfiguredError(
                '%s environment variable is required' % variable)


def env_variables_required(variables):
    def decorated(func):
        def new_function(*args, **kwargs):
            check_config(variables)
            func(*args, **kwargs)
        return new_function
    return decorated
