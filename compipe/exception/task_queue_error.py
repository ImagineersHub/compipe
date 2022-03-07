from .general_error import ExceptionError


class GErrorDuplicateSingletonCMD(ExceptionError):
    """Represent the exception of finding duplicate
    command tasks. Singleton command could not be 
    triggered through multi-thread at the same time.
    """

    pass
