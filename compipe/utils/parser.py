import argparse
import itertools
import os
from argparse import ArgumentParser

from .parameters import (ARG_ARGUMENT, ARG_CALLBACK, ARG_COMMAND,
                         ARG_DEBUG, ARG_DEV_CHANNEL, ARG_OUT_OF_SERVICE,
                         ARG_QUEUE_WORKER_NUMBER, ARG_RESOURCE, ARG_SPACE)
from .singleton import Singleton


def resolve_keyword_arguments(arguments):
    kwargs = {}
    param = []
    # seperate keyword and non-keyword parameters into two different groups:
    grouped_args = itertools.groupby(
        arguments, lambda value: '=' in value)
    # parse parameters: param-> non-keyword, kwargs-> keyword
    for is_keyword_param, values in grouped_args:
        if not is_keyword_param:
            param = list(values)
        else:
            for key in list(values):
                pairs = key.split('=', 1)
                kwargs[pairs[0]] = _parse_parameters(pairs[1])

    return param, kwargs


def is_int(x):
    try:
        a = float(x)
        b = int(a)
    except (TypeError, ValueError):
        return False
    else:
        return a == b


def is_float(x):
    try:
        a = float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True


def _parse_parameters(value):
    lowerStr = value.lower()
    if is_int(value) or is_float(value):
        return int(value) if is_int(value) else float(value)
    elif ',' in lowerStr:
        array_values = [element for element in lowerStr.split(',') if element]
        if is_int(array_values[0]):
            return list(map(lambda x: int(x), lowerStr.split(',')))
        elif is_float(array_values[0]):
            return list(map(lambda x: float(x), lowerStr.split(',')))
        else:
            return array_values

    elif os.path.isabs(value):
        # normalized the absolute file path with current system separator
        return os.path.normpath(value)

    if lowerStr in ("yes", "true", "t"):
        return True
    elif lowerStr in ("no", "false", "f"):
        return False
    else:
        return value


def str2bool(v):
    # susendberg's function
    return v.lower() in ("yes", "true", "t", "1")


class EnvParser(metaclass=Singleton):

    @classmethod
    def parse(cls, params={}) -> ArgumentParser:
        par = EnvParser().load()
        return par.parse_args(params) or par.parse_args()  # sys.arugs

    def load(self, parser=None):
        if not parser:
            parser = argparse.ArgumentParser()

        parser.add_argument('-v', '--version',
                            help='output the version number')

        parser.add_argument(ARG_COMMAND,
                            type=str,
                            help='the command name for executing',
                            nargs='?',
                            default='mayday')

        parser.add_argument(
            '-a',
            '--{}'.format(ARG_ARGUMENT),
            nargs='*',
            default=[],
            help='represent the command parameters for execting')

        parser.add_argument(
            '-cb',
            '--{}'.format(ARG_CALLBACK),
            help='represent the callback function, it will be sent back'
            'with payload data to the caller.'
        )

        parser.add_argument(
            '-sp',
            '--{}'.format(ARG_SPACE),
            type=str,
            default='default',
            help='represent the space name for current service: e.g. hkg, lax')

        parser.add_argument(
            '-res',
            '--{}'.format(ARG_RESOURCE),
            type=str,
            default='',
            help='represent the share drive letter.')

        parser.add_argument(
            '-d',
            '--{}'.format(ARG_DEBUG),
            type=str2bool,
            default=False,
            help='represent the debug flag. It would help make functional test '
            'in local. e.g. resource_app -> load local resource when "debug" flag '
            'is on.')

        parser.add_argument(
            '-o',
            '--{}'.format(ARG_OUT_OF_SERVICE),
            type=str2bool,
            default=False,
            help='represent the state of service.')

        parser.add_argument(
            '-dc',
            '--{}'.format(ARG_DEV_CHANNEL),
            type=str,
            default='G011D6MFK43',
            help='represent the dev slack channel ID, it would used to post some error logs.')

        parser.add_argument(
            '-wn',
            '--{}'.format(ARG_QUEUE_WORKER_NUMBER),
            type=int,
            default=1,
            help='represent the the total thread numbers of the parallel task workers')

        return parser
