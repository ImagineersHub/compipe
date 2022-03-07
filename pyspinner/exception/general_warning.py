import json
from ..response.command_result import CommandSingleResult, MSGStatusCodes
from .general_error import ExceptionError


class ExceptionWarning(ExceptionError):

    def to_command_result(self):
        return CommandSingleResult(
            message=self.message,
            payload=self.payload or None,
            msg_status=MSGStatusCodes.warning)


class WarningGotEmptyValue(ExceptionWarning):
    pass
