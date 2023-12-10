from enum import Enum
from functools import update_wrapper


# the '__call__' function will not be called when using dict to keep an instance of function
# use "locate" to find the command and execute properly
command_list = {}
# exclude buildin keys when validating parameters


class ResponseType(Enum):
    single = 'CommandSingleResult'
    lists = 'CommandMultipleResults'


def cmd_enroller(module, scopes=[], alias=None,
                 response_type=ResponseType.single, singleton=False):
    """
    register the commands which are hooked up with this decorator,
    commandline tool can directly execute the command for getting something fun

    Arguments:
        module {string} -- represent the module name of command

    Keyword Arguments:
        scope {int} -- represent the scope for access controlling
                       (default: {0} means it can be accessed by all users)
        alias {string} -- represent another short name for the key of command dict
                          (default: {None})
        debug {bool} -- represent the flag for debugging commands

        response_type {ResponseType} -- Represent the response result types.

        singleton {bool} -- Represent the task queue mode, singleton: only allow a 
        single job at the same time when having multi-threads mode
    """

    class Decorator(object):
        """
        Decorator for registering commands
        """

        def __init__(self, fn):
            self.fn = fn
            cmd_str = fn.__qualname__
            if cmd_str not in command_list:
                command_name = alias if alias else cmd_str
                if command_name in command_list:
                    raise ValueError(
                        f"Found duplicated command name: {command_name}")
                command_list[alias if alias else cmd_str] = {
                    'scopes': scopes,
                    'singleton': singleton,
                    'full_name': f"{module}.{fn.__qualname__}"}
            update_wrapper(self, fn)

        def __call__(self, *args, **kwargs):
            # detect the calling mode， CMD_PULS was passed from the command_helper
            # if the value is true, it would wrap the result with commandResult instead of directly
            # return the values from function
            # is_cmd_puls = kwargs.pop('CMD_PULS', None)

            # execute cmd with the specify parameters
            return self.fn(*list(args), **kwargs)

    return Decorator
