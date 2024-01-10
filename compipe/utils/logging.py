import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

# Optional import for colorlog
try:
    from colorlog import ColoredFormatter
    colorlog_available = True
except ImportError:
    colorlog_available = False


def setup_logger(logger_name='compipe', log_level=logging.DEBUG, keep_logs=False, backup_count=5):
    # Check if logger has already been created to avoid adding multiple handlers
    logger = logging.getLogger(logger_name)

    # If the logger already has handlers, return it as is
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    # Setup console handler
    console_handler = logging.StreamHandler()
    if colorlog_available:
        colored_formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            style='%'
        )
        console_handler.setFormatter(colored_formatter)
    else:
        console_formatter = logging.Formatter('%(levelname)-8s %(message)s')
        console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler setup
    if keep_logs:
        try:
            # Ensure log folder exists
            if log_folder is None:
                base_dir = os.path.dirname(os.path.abspath(
                    sys.modules['__main__'].__file__))
                log_folder = os.path.join(base_dir, 'logs')

            # Create a file handler that logs messages to a file, rotating daily
            log_file_path = os.path.join(log_folder, logger_name + '.log')
            file_handler = TimedRotatingFileHandler(
                log_file_path, when="midnight", interval=1, backupCount=backup_count)
            file_handler.suffix = "%Y-%m-%d"
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        except Exception as e:
            logger.error("Failed to create file handler: %s", e)

    return logger


# Example usage in any script
logger = setup_logger()
