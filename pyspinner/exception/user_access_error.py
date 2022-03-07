from .general_error import ExceptionError
from ..response.command_result import CommandSingleResult, MSGStatusCodes


class GErrorUserNoPermission(ExceptionError):
    """
    Represent the exception for user permission error
    """
    pass
