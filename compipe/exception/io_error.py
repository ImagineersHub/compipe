from .general_error import ExceptionError
from ..response.command_result import CommandSingleResult, MSGStatusCodes


class GErrorFileNotFound(ExceptionError):
    """
    Represent the exception for not found 404
    """

    def __init__(self, payload=None):
        super().__init__("Failed to load file:", payload)

    def to_command_result(self):
        return CommandSingleResult(
            message=self.message,
            payload=self.__str__(),
            msg_status=MSGStatusCodes.error)


class GErrorUnsupportedMIMEType(ExceptionError):
    """
    Represent the exception for uploading an unsupported MIME type file
    """
    pass


class GErrorInvalidFilePath(ExceptionError):
    """
    Represent the exception for invalid file path error.
    """
    pass


class GErrorInvalidDirectoryPath(ExceptionError):
    """
    Represent the exception for invalid file path error.
    """
    pass
