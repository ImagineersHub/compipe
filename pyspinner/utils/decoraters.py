import asyncio
import hashlib
import hmac
import os.path
import time
from pathlib import Path
from sys import platform
from types import MethodType

import wrapt

from ..exception.general_error import ExceptionError
from ..exception.io_error import (GErrorInvalidDirectoryPath,
                                  GErrorInvalidFilePath)
from ..exception.validate_error import (GErrorAuthentication,
                                        GErrorInvalidEnvironment,
                                        GErrorInvalidParam,
                                        GErrorMissingArguments,
                                        GErrorNullObject)
from ..runtime_env import Environment as env
from .access import X_HUB_SIGNATURE, AccessHub
from .logging import logger
from .parameters import ARG_PAYLOAD


class ClassProperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


@wrapt.decorator
def validate_kwargs(wrapped, instance, args, kwargs):
    """ Validate the parameter value, the specific parameters can't be none
    """
    for key, value in kwargs.items():
        if value is None:
            raise GErrorInvalidParam(
                'parameter [{}] has invalid value'.format(key))
    return wrapped(*args, **kwargs)


@wrapt.decorator
def timeit(wrapped, instance, args, kwargs):
    start = time()
    results = wrapped(*args, **kwargs)
    end = time()
    logger.debug(f'{wrapped.__name__} Elapsed time: {end-start}')
    return results


@wrapt.decorator
def event_loop_checker(wrapped, instance, args, kwargs):
    loop = asyncio.get_event_loop()
    while(loop.is_running()):
        logger.debug('asyncio: event loop - checking')
        time.sleep(0.5)
    return wrapped(*args, **kwargs)


@wrapt.decorator
def validate_file_path(wrapped, instance, args, kwargs):
    for _, value in kwargs.items():
        if isinstance(value, str):
            file_name, file_extension = os.path.splitext(value)
            if file_extension and not os.path.isfile(value):
                value = Path(value)
                raise GErrorInvalidFilePath('file not found: {}'.format(value))
    return wrapped(**kwargs)


@wrapt.decorator
def validate_dir_path(wrapped, instance, args, kwargs):
    for _, value in kwargs.items():
        if type(value) is str and os.path.isabs(value) and not os.path.exists(value):
            # force to convert to the current os path standard
            value = Path(value)
            raise GErrorInvalidDirectoryPath('directory not found: {}'.format(value))
    return wrapped(**kwargs)


def validate_collection_parameter(key, collections=[], allow_none=False):
    """
    Validate the keyword parameters.

    Description:
        get the value from kwargs with the given key, and use it to
        check if it's in the given collections

    Arguments:
        key {string} -- represent the key from the kwargs dict

    Keyword Arguments:
        collections {list} -- represent the collections for validating value (default: {[]})
    """
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        if not kwargs:
            logger.warning(
                f'keyword dict is empty, the validate decorator only supports keyword parameters. func {wrapped.__name__}')
        value = kwargs.get(key, None)
        if not value and not allow_none:
            raise GErrorInvalidParam(f'func {wrapped.__name__} | The parameter [{key}] can\'t be None')

        elif value is not None and value not in collections:
            print(key)
            print(value)
            print(collections)
            raise GErrorInvalidParam(
                f'The parameter [{str(key)}] was specified to an invalid value [{str(value)}]! Please choose a value from below lists: {",".join(sorted(collections))}')
        return wrapped(*args, **kwargs)
    return wrapper


def unnullable_params(*keys):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        invalid_keys = [key for key in keys if kwargs.get(key) == None]
        if invalid_keys:
            raise GErrorNullObject(f'Un-nullable parameter doesn\'t has valid value [Key: {invalid_keys}]')

        invalid_params = keys - kwargs.keys() if not set(keys).issubset(set(kwargs.keys())) else []
        # raise exception when seeing invalid parameters
        if invalid_params:
            print(invalid_params)
            raise GErrorMissingArguments(
                f'The required keys (parameters) were missing: {list(invalid_params)}')
        return wrapped(*args, **kwargs)
    return wrapper


def required_params(*keys):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        invalid_params = keys - kwargs.keys() if not set(keys).issubset(set(kwargs.keys())) else []
        # raise exception when seeing invalid parameters
        if invalid_params:
            raise GErrorMissingArguments(
                f'The required keys (parameters) were missing: {list(invalid_params)}')
        return wrapped(*args, **kwargs)
    return wrapper


def accepted_params(*keys):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        invalid_params = kwargs.keys() - keys if not set(kwargs.keys()).issubset(keys) else []
        # raise exception when seeing invalid parameters
        if invalid_params:
            raise GErrorMissingArguments(
                f'Can\'t recognize the specified parameters: {list(invalid_params)}')
        return wrapped(*args, **kwargs)
    return wrapper


def associated_params(*keys):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        source = set(keys)
        all_keys = kwargs.keys()

        if source & all_keys and not source.issubset(all_keys):
            raise GErrorMissingArguments(
                f'The associated keys (parameters) were missing: {list(keys)}')
        return wrapped(*args, **kwargs)
    return wrapper


def deprecate(replacement: MethodType):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        logger.warning(f'{wrapped.__name__} is deprecated, use {replacement.__name__} instead')
        return wrapped(*args, **kwargs)
    return wrapper


@wrapt.decorator
def win32_only(wrapped, instance, args, kwargs):
    if platform != 'win32':
        raise ExceptionError('Invalid platform error, it\'s a win32 only command!')
    return wrapped(*args, **kwargs)


def required_platform(*keys):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        if platform not in keys:
            raise ExceptionError(f"The command/function is only allowed on specific platforms: {keys}")
        return wrapped(*args, **kwargs)
    return wrapper


@wrapt.decorator
def console_only(wrapped, instance, args, kwargs):
    if not env.console_mode:
        raise GErrorInvalidEnvironment(f'Command is console-only: [{wrapped.__name__}]')
    return wrapped(*args, **kwargs)


@wrapt.decorator
def server_only(wrapped, instance, args, kwargs):
    if env.console_mode:
        raise GErrorInvalidEnvironment(f'Command is server_only: [{wrapped.__name__}]')
    return wrapped(*args, **kwargs)


def verify_webhook_secret_sha1(header):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        request = kwargs.get(ARG_PAYLOAD)
        secret = AccessHub().get_credential(X_HUB_SIGNATURE).encode()
        signature = hmac.new(secret, request.data, hashlib.sha1).hexdigest()
        # the hub signature string startswith 'sha1='
        # we would ignore the prefix when comparing the signature
        print(f'{header}{signature}')
        print(request.headers.get(X_HUB_SIGNATURE))
        if f'{header}{signature}' != request.headers.get(X_HUB_SIGNATURE):
            raise GErrorAuthentication(f'Webhook signature is invalid!')

        return wrapped(*args, **kwargs)
    return wrapper
