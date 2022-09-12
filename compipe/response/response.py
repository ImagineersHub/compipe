import io
import json
import logging
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from enum import Enum

import requests
from compipe.runtime_env import Environment as env

from ..utils.access import SLACK_APP_KEY, AccessHub
from ..utils.logging import logger
from ..utils.mime_types import GMimeTypes
from ..utils.parameters import *  # pylint: disable=unused-wildcard-import
from ..utils.parameters import ARG_CHANNEL, ARG_USER
from .command_result import (CommandResult, CommandSingleResult, FilePayload, CommandMultipleResults,
                             MSGStatusCodes)

ChannelType = namedtuple('ChannelType', ['key', 'name'])

SLACK_POST_MESSAGE_API = 'https://slack.com/api/chat.postMessage'
SLACK_UPLOAD_API = 'https://slack.com/api/files.upload'
HEADERS = {'content-type': 'application/json'}
SLACK_MAX_MESSAGE_LENGTH = 3000


class ClassProperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class RespChannel(Enum):
    console = 'ConsoleChannel'
    slack = 'SlackChannel'


class AbstractResponseChannel(metaclass=ABCMeta):
    """Represent the base class of channel."""

    def __init__(self, channel, user):
        pass

    @abstractmethod
    def post(self, payload=None, message=None, channel=None, msg_status=MSGStatusCodes.default):
        pass

    @abstractmethod
    def send(self, data: CommandResult):
        """Represent the abstractMethod for "send"."""
        pass

    @abstractmethod
    def upload(self, data: FilePayload, thread_ts=None):
        """Represent the abstractMethod for "upload file payload"."""
        pass


class ResponseChannel(AbstractResponseChannel):
    def __init__(self, channel, user):
        pass

    def post(self, payload=None, message=None, channel=None, msg_status=MSGStatusCodes.default, thread_ts=None):
        """Resolve the commandResult with the specific parameters.

        Arguments:
            payload {object} -- It would be any type value. type [list] 
            value would be wrapped with CommandMultipleResults

            message {str} -- Represent the message title

        Keyword Arguments:
            msg_status {MSGStatusCodes} -- Represent the message status (color) 
            (default: {MSGStatusCodes.default})
        """
        message_inst_type = CommandMultipleResults if isinstance(payload, list) else CommandSingleResult
        message_inst = message_inst_type(message=message,
                                         payload=payload,
                                         channel=None,
                                         thread_ts=thread_ts,
                                         msg_status=msg_status)
        return self.send(message_inst)

    def send(self, data: CommandResult):
        """Represent the abstractMethod for "send"."""
        pass

    def upload(self, data: FilePayload, thread_ts=None):
        """Represent the abstractMethod for "upload file payload"."""
        pass


class ConsoleChannel(ResponseChannel):
    """Represent the console channel for running service in local (debug)."""

    def __init__(self, channel='', user=''):
        pass

    def send(self, data: CommandResult):
        """Send response to local console.

        Arguments:
            data {dict} -- Represent the payload data
        """
        sys_logger = logging.getLogger()  # pylint: disable=no-member
        sys_logger.setLevel(logging.DEBUG)

        reporter = logger.debug

        if data.msg_status.value == MSGStatusCodes.error.value:
            reporter = logger.error
        elif data.msg_status.value == MSGStatusCodes.warning.value:
            reporter = logger.warning

        reporter(f'\n{str(data)}')

    def upload(self, data: FilePayload, thread_ts=None):
        logger.warning(f'Unable to upload file payload through ConsoleChannel')


class SlackChannel(ResponseChannel):
    def __init__(self, channel, user):
        # load tokens from load creds json
        self.channel = channel
        self.user = user

    def send(self, data: CommandResult):
        # slack message ts
        slack_ts = ''
        self.channel = data.channel if data.channel else self.channel
        print('==========channel')
        print(self.channel)
        print(data.channel)
        print('==========channel')
        payload = SlackChannel.resolve_payload(data)
        if data.is_error and self.user != 'com':
            # post to dev channel
            self.upload_large_text_with_snippet(title='Exception: traceback',
                                                content=data.payload,
                                                thread_ts=data.thread_ts,
                                                channel=env.dev_channel.upper())
            # post to user channel
            payload = SlackChannel.resolve_payload(
                CommandSingleResult(
                    message=data.message,
                    payload='A team of highly trained martian has been'
                    ' dispatched to stop the launching.\nTask queue\'s been terminated immediately',
                    msg_status=MSGStatusCodes.error))
            slack_ts = self.post_message(payload)
        else:
            if data.is_large_payload(SLACK_MAX_MESSAGE_LENGTH):
                self.post_message(
                    SlackChannel.resolve_payload(CommandSingleResult(payload=data.message)))

                slack_ts = self.upload_large_text_with_snippet(content=data.payload,
                                                               thread_ts=data.thread_ts)
            else:
                slack_ts = self.post_message(payload=payload)

        logger.debug('Response sent to slack!')
        return slack_ts

    @classmethod
    def resolve_payload(cls, data):
        attachments = []

        if isinstance(data, CommandSingleResult):
            message_data = str(data)
            attachments.append({
                'color': data.msg_status.color,
                'text': message_data
            })
            # dump a copy of the message to the logs when posting through slack
            if data.msg_status.value == MSGStatusCodes.warning.value:
                logger.warning(message_data)
            else:
                logger.debug(message_data)
        else:
            if not data.payload:
                # handling the empty results
                attachments.append({
                    'color': MSGStatusCodes.warning.value,
                    'text': 'Oops! Found nothing at the moment...'
                })
            else:
                # reformat payload to list type
                if not isinstance(data.payload, list):
                    data.payload = [data.payload]

                for item in data.payload:
                    attachments.append({
                        'text': json.dumps(item) if isinstance(item, dict) else str(item)
                    })
        msg_payload = {
            'text': data.message or None,
            'attachments': json.dumps(attachments).encode()
        }
        # attach thread ts info
        # the message will be replied in message thread
        if data.thread_ts:
            msg_payload.update({
                'thread_ts': data.thread_ts
            })

        return msg_payload

    def post_message(self, payload, channel=None):
        team, channel = (channel or self.channel).split('#')
        upload_meta = {
            "token": AccessHub().get_credential(SLACK_APP_KEY).get(team),
            "channel": channel}

        upload_meta.update(payload)
        result = requests.post(SLACK_POST_MESSAGE_API,
                               headers=HEADERS,
                               params=upload_meta
                               )

        logger.debug(f'Post message to slack!{result.json()}')
        return result.json().get('ts')

    def upload_large_text_with_snippet(self, title=None, content='', channel=None, thread_ts=None):
        team, channel = (channel or self.channel).split('#')
        upload_meta = {
            "title": title or 'Text Snippets',
            "token": AccessHub().get_credential(SLACK_APP_KEY).get(team),
            "channels": channel,
            'content': content
        }
        # attach thread ts info
        # the message will be replied in message thread
        if thread_ts:
            upload_meta.update({
                'thread_ts': thread_ts
            })

        result = requests.post(SLACK_UPLOAD_API,
                               params=upload_meta)

        logger.debug(f'Post text snippets to slack! {title}')
        return result.json().get('ts')

    def upload(self, data: FilePayload, thread_ts=None):
        team, channel = self.channel.split('#')
        result = {}
        if data.file_path:
            with open(data.file_path, 'rb') as f:
                upload_meta = {
                    "title": data.title,
                    "filename": data.file_name,
                    "token": AccessHub().get_credential(SLACK_APP_KEY).get(team),
                    "channels": channel,
                    "filetype": data.file_type.name
                }

                # attach thread ts info
                # the message will be replied in message thread
                if thread_ts:
                    upload_meta.update({
                        'thread_ts': thread_ts
                    })

                result = requests.post(SLACK_UPLOAD_API,
                                       params=upload_meta,
                                       files={
                                           'file': f
                                       })

        else:
            if data.file_type is GMimeTypes.PNG and data.file_data:
                preview_map = io.BytesIO()
                # force to resize to 1k image, the high qaulity image could be found on google drive
                data.file_data.resize((1024, 1024))
                data.file_data.save(preview_map, data.file_type.name)
                data.file_bytes = preview_map

            upload_meta = {
                "title": data.title,
                "token": AccessHub().get_credential(SLACK_APP_KEY).get(team),
                "channels": channel,
                "filename": data.file_name,
                "filetype": data.file_type.name
            }

            # attach thread ts info
            # the message will be replied in message thread
            if thread_ts:
                upload_meta.update({
                    'thread_ts': thread_ts
                })

            result = requests.post("https://slack.com/api/files.upload",
                                   params=upload_meta,
                                   files={
                                       'file': data.file_bytes.getvalue() if data.file_bytes else data.file_data  # io.BytesIO()
                                   })

        logger.debug(f'upload file to slack! {data.title}')
        return result.json().get('ts')


# The other modules could directly parse the channel class
# from the name via 'eval' function
response_channel_handlers = {
    'ConsoleChannel': ConsoleChannel,
    'SlackChannel': SlackChannel
}
