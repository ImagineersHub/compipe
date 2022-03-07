import logging
from logging.handlers import QueueHandler
import os.path
import traceback
from collections import deque
from enum import IntEnum
from logging import DEBUG

LOG_FILE_NAME = 'current.log'
LOG_FOLDER_NAME = 'compipe_logs'
LOG_FILE_PATH = os.path.join(LOG_FOLDER_NAME, LOG_FILE_NAME)


class LOG_COLOR:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LogErrorCode(IntEnum):
    default = -1
    system = 0
    proto_error = 1


class CaptureHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.records = deque(maxlen=10)

    def emit(self, record):
        self.records.append(self.formatter.format(record))

    def get_records(self):
        return self.records


class Logger(object):
    """
    Logger mixin/base class adding verbose logging to subclasses.
    Subclasses get info(), debug(), warning() and error() methods which, alongside
    the information given, also show location of the message (file, line and
    function).
    By default, the logging mechanism will only show warning and error messages
    without any timestamping. A static method Logger.basicConfig() is provided
    for basic usage with all debugging turned on and showing debuglevel and
    timestamps. See the documentation of logging module for information how to
    customize debug levels, formatters and outputs.
    To activate the basic configuration:
    >>> Logger.basicConfig()
    Example mixin usage:
    >>> class MyClass(Logger):
    ...    def my_method(self):
    ...        self.debug('called')
    ...    def raises_exc(self):
    ...        try:
    ...            raise Exception("error message")
    ...        except:
    ...            self.error('got exception', exc_info=True)
    ...
    >>> x = MyClass()
    >>> x.my_method()
    >>> x.raises_exc()
    Module also provides a singleton "logger" instance of Logger class, which
    can be used when it's not feasible to use the mixin. The logger provides
    the same debug(), warning() and error() methods.
    Example singleton usage:
    >>> logger.debug('This is a debug message')
    """

    capture_handler = CaptureHandler()

    show_source_location = True

    # Formats the message as needed and calls the correct logging method
    # to actually handle it
    def _raw_log(self, logfn, message, exc_info):
        cname = ''
        loc = ''
        fn = ''
        tb = traceback.extract_stack()
        if len(tb) > 2:
            if self.show_source_location:
                loc = '(%s:%d):' % (os.path.basename(tb[-3][0]), tb[-3][1])
            fn = tb[-3][2]
            if fn != '<module>':
                if self.__class__.__name__ != Logger.__name__:
                    fn = self.__class__.__name__ + '.' + fn
                fn += '()'

        if isinstance(message, list):
            message = '\n'.join(message)
        elif isinstance(message, dict):
            message = '\n'.join(['{}:{}'.format(key, value) for key, value in message.items()])
        else:
            message = str(message)

        logfn(loc + cname + fn + ': ' +
              message or "Message is None", exc_info=exc_info)

    def info(self, message, exc_info=False):
        """
        Log a info-level message. If exc_info is True, if an exception
        was caught, show the exception information (message and stack trace).
        """
        self._raw_log(logging.info, message, exc_info)  # pylint: disable=no-member

    def debug(self, message, exc_info=False, color=LOG_COLOR.OKGREEN):
        """
        Log a debug-level message. If exc_info is True, if an exception
        was caught, show the exception information (message and stack trace).
        """
        self._raw_log(
            logging.debug, message if not color else f'\n{color}{message}{LOG_COLOR.ENDC}', exc_info)  # pylint: disable=no-member

    def warning(self, message, exc_info=False):
        """
        Log a warning-level message. If exc_info is True, if an exception
        was caught, show the exception information (message and stack trace).
        """
        self._raw_log(logging.warning, f'\n{LOG_COLOR.WARNING}{message}{LOG_COLOR.ENDC}', exc_info)  # pylint: disable=no-member

    def error(self, message, exc_info=False):
        """
        Log an error-level message. If exc_info is True, if an exception
        was caught, show the exception information (message and stack trace).
        """
        self._raw_log(logging.error, f'\n{LOG_COLOR.FAIL}{message}{LOG_COLOR.ENDC}', exc_info)  # pylint: disable=no-member

    @staticmethod
    def basicConfig(level=DEBUG, is_record=False):
        """
        Apply a basic logging configuration which outputs the log to the
        console (stderr). Optionally, the minimum log level can be set, one
        of DEBUG, WARNING, ERROR (or any of the levels from the logging
        module). If not set, DEBUG log level is used as minimum.
        """
        logging.basicConfig(  # pylint: disable=no-member
            level=level,
            format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

        if is_record:
            if not os.path.isdir(LOG_FOLDER_NAME):
                os.mkdir(LOG_FOLDER_NAME)

            root_logger = logging.getLogger('')  # pylint: disable=no-member
            rotate_logger = logging.handlers.TimedRotatingFileHandler(
                LOG_FILE_PATH,
                when='midnight',
                interval=1,
                backupCount=60)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # pylint: disable=no-member
            rotate_logger.setFormatter(formatter)
            # urllib_logger = logging.getLogger('urllib3.connectionpool')
            # urllib_logger.addFilter(lambda record: 'Starting new HTTP connection' not in record.getMessage())
            # urllib_logger.addFilter(lambda record: 'http://127.0.0.1:1300' not in record.getMessage())
            root_logger.addHandler(Logger.capture_handler)
            root_logger.addHandler(rotate_logger)

        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)


Logger.basicConfig(level=DEBUG, is_record=True)
logger = Logger()


if __name__ == '__main__':
    # Run the code from examples
    import doctest
    doctest.testmod()
