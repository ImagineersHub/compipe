import copy
import json
import queue
import random
import traceback
from threading import Thread, get_ident

from compipe.runtime_env import Environment as env
from ..response.response import response_channel_handlers, RespChannel
from ..cmd_enroller import command_list
from ..exception.task_queue_error import GErrorDuplicateSingletonCMD
from ..response.command_result import CommandSingleResult, MSGStatusCodes
from ..response.response import RespChannel
from .hash_code_helper import encrypt_str
from .logging import logger
from .parameters import (ARG_ARGUMENT, ARG_CHANNEL, ARG_COMMAND, ARG_RESPONSE,
                         ARG_USER)

current_thread = None
# only support single task to avoid content conflict on a single vm
NUM_WORKERS = 1

GREETING_HEADER = 'Apollo 11, this is Houston!'
# AIR_TO_GROUND_VOICE
ATDV_TRANSCRIPTION = ['You are confirmed GO for orbit.',
                      'Through Canary. Over.',
                      'The booster has been configured for orbital coast.',
                      'Through Tananarive. Over.',
                      'We are receiving your FM downlink now.',
                      'We are seeing the pitch hot firing and it looks good.',
                      'Go ahead and we\'ll watch you on TM.',
                      'We\'ve completed the uplink.',
                      'You are GO for TLI. Over.',
                      'We\'re reading you readability about 3,'
                      'strength 5. Sounds pretty good. Over.']


class Task():

    def __init__(self, interpreter=None, arguments=None, kwargs=None):
        self.interpreter = interpreter
        self.arguments = arguments
        self.kwargs = kwargs
        self._response = None
        self.thread_ts = None

    @property
    def hash(self):
        key_str = json.dumps(self.kwargs)
        return encrypt_str(key_str)

    @property
    def command(self):
        return self.kwargs[ARG_COMMAND]

    @property
    def args(self):
        return self.kwargs[ARG_ARGUMENT] or []

    @property
    def user(self):
        return self.kwargs.get(ARG_USER, 'com')

    @property
    def channel(self):
        return self.kwargs.get(ARG_CHANNEL, env.dev_channel)

    @property
    def response_channel(self):
        return self.kwargs.get(ARG_RESPONSE, RespChannel.console.value)

    @property
    def response(self):
        if not self._response:
            # parse the response channel class from the name
            resp_inst = response_channel_handlers.get(self.response_channel,
                                                      RespChannel.console.value)
            # trigger the corresponding channel to response messages
            self._response = resp_inst(channel=self.channel,
                                       user=self.user)
        return self._response

    @property
    def is_singleton(self):
        """ Singleton mode task, it means the command would not be triggered in
        multi-threads at the same time

        Returns:
            {bool} -- Represent the flag identifying singleton mode.
        """
        return self.command in command_list and command_list[self.command]['singleton']

    def pop(self):
        return self.interpreter, self.arguments or [], self.kwargs or {}

    def run(self):
        self.interpreter(*self.arguments, **self.kwargs)
        return True

    def __str__(self):
        # filtered build-in kwargs
        # e.g. 'ARG_TASK_WORKER' flag would be added to the param
        # when trigging through task queue
        params = " ".join(self.args)
        return f'{self.command} -a {params}'


class TaskQueue(queue.Queue):
    current_task_count = 0

    #
    def __init__(self):
        queue.Queue.__init__(self)
        # get worker number (multi-thread support)
        # default value would be single thread.
        self.num_workers = int(env.worker_num)
        logger.debug(f'Start task queue service: thread number [{self.num_workers}]')
        self.start_workers()
        self.current_task = {}

    def get_thread_task_hash(self):
        return list(task.hash for task in self.current_task.values())

    def get(self):

        task = super().get()

        if task.is_singleton and task.hash in self.get_thread_task_hash():
            # add back to the end of the task queue
            self.add_task(task)
            raise GErrorDuplicateSingletonCMD(f'Found duplicate singleton command.[{task.command}]')

        # record current task
        self.current_task.update({
            get_ident(): task
        })

        cmd_res = CommandSingleResult(
            message=f"{GREETING_HEADER} {random.choice(ATDV_TRANSCRIPTION)}",
            payload=f'[Command] `{str(task)}` \n[User] `{task.user}`')

        # retrieve the thread context, which is used to reply message in the
        # same threads (discord or slack channel)
        task.thread_ts = task.response.send(cmd_res)

        # blow codes were deprecated, leave the code snippet for further investigation
        # TODO: Clean up
        # if task.thread_ts:  # update message when grabbing task from queue
        #     team, channel = task.channel.split('#')
        #     payload = SlackChannel.resolve_payload(cmd_res)
        #     payload.update({
        #         'ts': task.thread_ts,
        #         'channel': channel,
        #         'team': team
        #     })
        #     chat_update(**payload)
        # else:
        #     task.thread_ts = task.response.send(cmd_res)

        return task

    def task_done(self):
        super().task_done()

        # remove finished task instance
        task_inst = self.current_task.get(get_ident())
        del task_inst
        TaskQueue.current_task_count -= 1

    def add_task(self, task):
        # Response greetings, ignore the cmd header when receving from compe
        if TaskQueue.current_task_count != 0:
            task.thread_ts = task.response.post(
                payload=f"Joined in task queue [{TaskQueue.current_task_count}] `{str(task)}`",
                msg_status=MSGStatusCodes.default)
        TaskQueue.current_task_count += 1
        self.put(task)

    def start_workers(self):
        for _ in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = not env.console_mode
            t.start()

    def worker(self):
        while True:
            task = self.get()
            try:
                task.run()
            except:
                logger.error(str(traceback.format_exc()))
            finally:
                logger.debug(f'Task\'s been Done! [{str(task)}]')
                self.task_done()
                # stop listenning task queue when trigging from consoles
                if env.console_mode:
                    logger.debug('Exit Task Queue : Current process '
                                 '[Environment.console_mode]')
                    break

    def get_queue_list(self):
        queue_tasks = [{ARG_COMMAND: cmd[ARG_COMMAND],
                        ARG_ARGUMENT: cmd[ARG_ARGUMENT]} for _, _, cmd, in self.queue]
        if self.current_task:
            queue_tasks.append(copy.deepcopy(self.current_task))

        # reformat command context
        for item in queue_tasks:
            args = (arg for arg in item[ARG_ARGUMENT] if '=' in arg)
            for arg in args:
                pairs = arg.split('=')
                item.update({pairs[0]: pairs[1]})
        return queue_tasks
