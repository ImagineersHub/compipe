
from .utils.access import AccessHub
from .utils.parameters import (ARG_CONSOLE, ARG_DEBUG, ARG_DEV_CHANNEL,
                               ARG_MARS_DICOM_DATA_ROOT, ARG_OUT_OF_SERVICE,
                               ARG_QUEUE_WORKER_NUM, ARG_RESOURCE,
                               ARG_SUBPROCESS_NUM)
from .utils.singleton import ThreadSafeSingleton

AccessHub().get_server_config()


class ClassProperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class Environment(metaclass=ThreadSafeSingleton):
    def __init__(self, *args, console_mode=False, **kwargs):
        self.param = {key: value.lower() if isinstance(value, str) else value for key, value in kwargs.items()}
        self.param.update({
            ARG_CONSOLE: console_mode
        })
        self.param.update(AccessHub().get_server_config())
        # update server config to Environment
        # local mode: Local_server_config.json
        # cloud: IBM cloud runtime env
        # self.update(AccessHub().server_configs)

    @ClassProperty
    def console_mode(cls):
        # check the running mode
        return Environment().param.get(ARG_CONSOLE, True)

    @ClassProperty
    def debug_mode(cls):
        # check the running mode
        return Environment().param.get(ARG_DEBUG, False)

    @ClassProperty
    def resource(cls):
        return Environment().param.get(ARG_RESOURCE, r'S:\Shared drives\Savoia_Data')

    @ClassProperty
    def dev_channel(cls):
        # set 'bot-tars-debug' to be the default channel for posting error logs
        # deeptars#bot-tars-debug https://deeptars.slack.com/archives/G015P1L6L7J
        return Environment().param.get(ARG_DEV_CHANNEL, 'T015BP2HUU9#G015P1L6L7J')

    @ClassProperty
    def out_of_service(cls):
        # set hkg to be the default space for PROTP
        return Environment().param.get(ARG_OUT_OF_SERVICE, False)

    @ClassProperty
    def worker_num(cls):
        # check the running mode
        return Environment().param.get(ARG_QUEUE_WORKER_NUM, 1)

    @ClassProperty
    def subprocess_num(cls):
        # check the running mode
        return Environment().param.get(ARG_SUBPROCESS_NUM, 5)

    @ClassProperty
    def mars_dicom_data_root(cls):
        # check the running mode
        return Environment().param.get(ARG_MARS_DICOM_DATA_ROOT, None)

    def __str__(self):
        return '{0}\n{1}\n{2}\n{0}'.format('==========ENV==========',
                                           '|'.join(['dev_channel']),
                                           '|'.join([Environment.dev_channel]))
