import re
import shlex
import uuid
from typing import Callable
from dataclasses import dataclass
from pydoc import locate
from timeit import default_timer as timer

# register commands
from .cmd_enroller import command_list
from .exception.user_access_error import GErrorUserNoPermission
from .exception.validate_error import (GErrorCommandNotFound,
                                       GErrorMissingArguments)
from .response.command_result import CommandSingleResult, MSGStatusCodes
# from utils.parser import *
from .response.response import RespChannel
from .runtime_env import Environment as env
from .utils.decorators_exception_handler import exception_handler
from .utils.logging import LOG_COLOR, logger
from .utils.parameters import *
from .utils.parser import EnvParser, resolve_keyword_arguments
from .utils.singleton import Singleton
from .utils.task_queue import Task
from .utils.task_queue_helper import TQHelper

# customize the mapping lists to assign access to the specific users
scope_mappings = {}


@dataclass
class Command():
    args: dict

    @property
    def callback(self):
        return self.args.get(ARG_CALLBACK, None)

    @property
    def command(self):
        return self.args[ARG_COMMAND]

    @property
    def command_id(self):
        return self.args[ARG_COMMAND_ID]

    @property
    def message(self):
        return ' '.join(self.arguments)

    @property
    def arguments(self):
        return self.args.get(ARG_ARGUMENT, [])

    @property
    def user(self):
        return self.args.get(ARG_USER, None)


class CommandWrapper():

    @staticmethod
    def resolve_task(*args, **kwargs):

        cmd = Command(kwargs)
        logger.debug(f'================ Start [{cmd.command}]', color=LOG_COLOR.OKBLUE)
        # calculate time elapsed
        start_time = timer()
        CommandWrapper().run_command(cmd)
        logger.debug(f'elapsed time: {timer() - start_time}', color=LOG_COLOR.WARNING)

        logger.debug(f'================== End [{cmd.command}]', color=LOG_COLOR.OKBLUE)

    def _verify_build_status(self):
        """TODO: Implement build status checking
        """
        logger.warning('TODO: implement the function to check build '
                       'status before committing new changes')
        pass

    @exception_handler
    def run_command(self, command_inst: Command):
        """TODO: implement the command scope protection. Users will not 
        be able to access some specific command without granted access 

        Args:
            command_inst (Command): represent the activated command instance

        Raises:
            GErrorCommandNotFound: throw not found error when command name is invalid.
        """

        if command_inst.command not in command_list:
            raise GErrorCommandNotFound(
                f'Not Found[{command_inst.command}], use `compe list` to dump the full lists.')

        cmd = locate(command_list[command_inst.command]['full_name'])

        # parse keywords argus
        param, kwargs = resolve_keyword_arguments(command_inst.arguments)

        cmd_results = cmd(*param, **kwargs)

        TQHelper.post(payload=cmd_results or f'[{cmd.__name__}] No returned value')


def push_command_in_queue(kwargs: dict, on_success: Callable[[str, Command], None]):

    # Resolve arguments
    data = resolve_arguments(**kwargs)
    data[ARG_COMMAND_ID] = uuid.uuid4().hex
    # Append new task
    TQHelper().tasks.add_task(Task(CommandWrapper.resolve_task, [], data))

    if on_success:
        on_success(Command(data))


def get_user_scope(user):
    """
    Return default "0" scope for testing features

    Arguments:
        usr {string} -- represent the user account name

    ToDo:
        load user scope from database for validating the acccess in real
    """
    return scope_mappings.get(user, [1])


def resolve_arguments(**kwargs):

    if ARG_COMMAND not in kwargs or ARG_RESPONSE not in kwargs:
        raise GErrorMissingArguments(
            'Key error : [command] or [response] was not found!')

    data = kwargs

    if kwargs[ARG_RESPONSE] == RespChannel.slack.value:
        # Remove slack bot name
        if re.match(r'<@\w+>', kwargs[ARG_COMMAND][0]):
            kwargs[ARG_COMMAND].pop(0)

    # add '-a' to the command str if user did not specify
    if len(kwargs[ARG_COMMAND]) > 1 and '-a' not in kwargs[ARG_COMMAND]:
        kwargs[ARG_COMMAND].insert(1, '-a')

    # add default '-a' flag and null value
    elif len(kwargs[ARG_COMMAND]) == 1:
        kwargs[ARG_COMMAND] += ['-a']

    command_param = vars(EnvParser.parse(kwargs[ARG_COMMAND]))

    channel = kwargs.get(ARG_CHANNEL, None)

    data.update({
        ARG_COMMAND: command_param[ARG_COMMAND],
        ARG_ARGUMENT: command_param[ARG_ARGUMENT],
        ARG_RESPONSE: kwargs[ARG_RESPONSE],
        ARG_USER: kwargs.get(ARG_USER),
        ARG_CHANNEL: channel
    })

    return data


def create_command_payload(args):
    # the dev_channel would be involved when running debug mode without specifying channel info.
    # ps: use flag 'Environment.debug_mode' to check the running mode
    if ARG_CHANNEL not in args:
        args[ARG_CHANNEL] = env.dev_channel
    if env.out_of_service:
        TQHelper.post(
            channel=args.get(ARG_CHANNEL, env.dev_channel),
            payload='Compipe is temporary out of service for maintaining!',
            msg_status=MSGStatusCodes.warning)
    else:
        args[ARG_COMMAND] = args[ARG_COMMAND].replace(u'\xa0', u' ')
        args[ARG_COMMAND] = list(map(str.strip, shlex.split(args[ARG_COMMAND])))

        push_command_in_queue(args)
