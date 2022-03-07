import json
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum

from ..utils.mime_types import GMimeTypes

MSGStatus = namedtuple('MSGStatus', ['value', 'color'])


class MSGStatusCodes(Enum):
    @property
    def color(self):
        return self.value.color  # pylint: disable=no-member

    default = MSGStatus(1, '#5ec120')
    warning = MSGStatus(2, '#f4b642')
    success = MSGStatus(5, '#81D8D0')
    error = MSGStatus(3, '#dd0f0f')


@dataclass
class FilePayload():
    title: str = None
    file_name: str = None
    file_type: GMimeTypes = GMimeTypes.PNG
    file_path: str = None
    file_bytes: bytes = None
    file_data: object = None


@dataclass
class _CommandResultBase():
    message: str = None
    payload: object = None
    error: object = None
    msg_status: MSGStatusCodes = MSGStatusCodes.default
    channel: str = None
    response: str = None
    # The ts value of the parent message.
    thread_ts: str = None


@dataclass
class CommandResult(_CommandResultBase):

    def is_large_payload(self, max_length=3000):
        return isinstance(self.payload, str) and len(self.payload) > max_length

    @property
    def is_error(self):
        return self.error is not None

    def slack_output(self):
        pass

    def terminal_output(self):
        pass

    def __str__(self):
        return '{}:{}'.format(self.payload or '<payload:None>',
                              self.message or '<message:None>')


@dataclass
class CommandMultipleResults(CommandResult, _CommandResultBase):

    def slack_output(self):
        pass

    def __str__(self):
        response = '\n'.join([str(item) for item in self.payload]) \
            if isinstance(self.payload, list) else self.payload

        return '{}\nResults:\n{}'.format(self.message, response)


@dataclass
class CommandSingleResult(CommandResult, _CommandResultBase):

    def __str__(self):
        results = self.payload or self.message
        if results and isinstance(results, dict):
            return f'\n{json.dumps(self.payload, indent=4)}'
        else:
            return str(results)


class HttpResponse:

    @staticmethod
    def success(payload):
        return HttpResponse.response(1, payload)

    @staticmethod
    def error(payload):
        return HttpResponse.response(0, payload)

    @staticmethod
    def response(mode, payload):
        return {
            "result": mode,
            "payload": payload
        }
