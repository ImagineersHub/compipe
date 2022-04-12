from .general_error import ExceptionError


class GErrorValue(ExceptionError):
    """
    Represent the exception for value validation
    """

    def __init__(self, payload=None):
        super().__init__(payload=payload, message="Failed to update")


class GErrorInvalidParam(ExceptionError):
    """Represent the exception of invalid parameters."""

    pass


class GErrorCommandNotFound(ExceptionError):
    pass


class GErrorAssetPathNotFound(ExceptionError):
    pass


class GErrorFileNotFound(ExceptionError):
    pass


class GErrorFolderNotFound(ExceptionError):
    pass


class GErrorKeyNotFound(ExceptionError):
    pass


class GErrorSpaceNotFound(ExceptionError):
    pass


class GErrorMissingArguments(ExceptionError):
    pass


class GErrorConfigValidation(ExceptionError):
    pass


class GErrorInvalidEnvironment(ExceptionError):
    pass


class GErrorAuthentication(ExceptionError):
    pass


class GErrorInvalidMIMEType(ExceptionError):
    pass


class GErrorNullObject(ExceptionError):
    pass


class GErrorInvalidPath(ExceptionError):
    pass


class GErrorNotImplemented(ExceptionError):
    pass


class GErrorInvalidDataFormat(ExceptionError):
    pass


class GErrorOutOfRange(ExceptionError):
    pass


class GErrorMissingRequiredTag(ExceptionError):
    pass
