
import traceback

from googleapiclient.errors import HttpError

from ..exception.general_error import ExceptionError
from ..exception.general_warning import ExceptionWarning
from ..response.command_result import MSGStatusCodes
from .task_queue_helper import TQHelper


def exception_handler(func):
    def decorator(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:

            if issubclass(type(e), ExceptionWarning):
                TQHelper.post(
                    payload=e.to_command_result(),
                    msg_status=MSGStatusCodes.warning)

            elif issubclass(type(e), ExceptionError):
                TQHelper.post(payload=e.to_command_result())

            elif isinstance(e, HttpError):
                TQHelper.post(
                    message='Google Drive Connection Timeout',
                    payload='Service Unavailable',
                    msg_status=MSGStatusCodes.error)
            else:
                # post to the triggering channel
                TQHelper.post(
                    payload='Got an internal error, self-destruction is activated!',
                    msg_status=MSGStatusCodes.error)

                # post to debug channel
                TQHelper.post(
                    payload=f'{str(TQHelper().current_thread_task)}\n{str(traceback.format_exc())}',
                )
    return decorator
