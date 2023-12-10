
from compipe.utils.task_queue_helper import TQHelper
from compipe.utils.parser import EnvParser
from compipe.utils.parameters import (ARG_ARGUMENT, ARG_COMMAND, ARG_RESPONSE,
                                      ARG_USER)
from compipe.response.response import RespChannel
from compipe.cmd_wrapper import push_command_in_queue
from time import sleep
import sys
import logging
import getpass
from typing import Any, Dict, List

from compipe.cmd_enroller import cmd_enroller
from compipe.utils.logging import logger


@cmd_enroller(__name__, alias="test1")
def cmd_test(*args: List, **kwds: Dict) -> Any:
    logger.debug(f"==============Hello World==============")
    return "test1"


def main():
    # attach '-a' flag for specify arguments
    if len(sys.argv) < 3:
        sys.argv.append('-a')
    elif '-a' not in sys.argv:
        sys.argv.insert(2, '-a')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    cmd_str = ' '.join(sys.argv)

    args = vars(EnvParser().load().parse_args())

    if ARG_COMMAND in args:
        args[ARG_COMMAND] = [args[ARG_COMMAND], *args[ARG_ARGUMENT]]
        args[ARG_RESPONSE] = RespChannel.console.value
        args[ARG_USER] = getpass.getuser()

        push_command_in_queue(
            args, on_success=lambda x: logger.debug(f'[Command] {x}'))

        while TQHelper().tasks.current_task_count:
            sleep(3)
