from .general_error import ExceptionError


class GErrorUnsupportedPlatform(ExceptionError):
    """Represent the exception of running command/function on unsupported platform.
    """
    pass
