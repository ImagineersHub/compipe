from .general_error import ExceptionError


class GErrorSlackAPI(ExceptionError):
    """Represent the exception of invalid slack api call
    """

    pass


class GErrorConfluenceAPIOffline(ExceptionError):
    pass


class GErrorConfluenceAPIRequest(ExceptionError):
    pass
