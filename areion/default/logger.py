import logging
from ..base import BaseLogger


class Logger(BaseLogger):
    """
    Logger class for handling logging with both console and file output.
    Attributes:
        logger (logging.Logger): The logger instance used for logging messages.
    Methods:
        __init__(log_file=None, log_level=logging.INFO):
            Initializes the Logger instance with optional file logging and specified log level.
        info(message: str) -> None:
            Logs an informational message.
        debug(message: str) -> None:
            Logs a debug message.
        error(message: str) -> None:
            Logs an error message.
        warning(message: str) -> None:
            Logs a warning message.
        critical(message: str) -> None:
            Logs a critical message.
    """

    def __init__(self, log_file=None, log_level=logging.INFO):
        self.logger = logging.getLogger("areion")
        self.logger.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)
