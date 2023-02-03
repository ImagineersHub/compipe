from threading import get_ident

from ..response.command_result import FilePayload

from .singleton import Singleton
from .task_queue import TaskQueue
from ..exception.validate_error import GErrorNullObject
from .logging import logger
from ..response.response import ConsoleChannel


class TQHelper(metaclass=Singleton):
    def __init__(self):
        self.tasks = TaskQueue()

    @property
    def current_thread_task(self):
        return self.tasks.current_task.get(get_ident())

    @current_thread_task.setter
    def current_thread_task(self, value):
        self.tasks.current_task.update({
            get_ident(): value
        })

    @classmethod
    def post(cls, **kwargs):
        """Accept parameters:
            [name]=[default]
            > payload=None,
            > message=None,
            > channel=None,
            > msg_status=MSGStatusCodes.default
            > thread_ts=None
        """
        if task := TQHelper().current_thread_task:
            kwargs.update({
                'thread_ts': task.thread_ts
            })
            TQHelper().current_thread_task.response.post(**kwargs)

        else:
            logger.warning('Not found task queue! Use console to response by default.')
            ConsoleChannel().post(**kwargs)

    @classmethod
    def upload(cls, file_payload: FilePayload):
        TQHelper().current_thread_task.response.upload(
            data=file_payload,
            thread_ts=TQHelper().current_thread_task.thread_ts)
