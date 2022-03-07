import json
from ..response.command_result import CommandSingleResult, MSGStatusCodes


class ExceptionError(Exception):
    def __init__(self, payload=None, message=None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.payload = payload if not payload or type(payload) is str else json.dumps(payload)
        self.message = message
        self.ProtoError = True

    def __str__(self):
        return '\n'.join([self.message, self.payload or ''])

    def to_command_result(self):
        return CommandSingleResult(
            message=self.message,
            payload=self.payload or None,
            msg_status=MSGStatusCodes.error)
