import asyncio
from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from aiologger.handlers.streams import AsyncStreamHandler
from ..base import BaseLogger

class AsyncLogger(BaseLogger):
    """
    AsyncLogger class for handling asynchronous logging with both console and file output.
    Attributes:
        logger (aiologger.Logger): The asynchronous logger instance used for logging messages.
    Methods:
        __init__(log_file=None, log_level="INFO"):
            Initializes the AsyncLogger instance with optional file logging and specified log level.
        info(message: str) -> None:
            Logs an informational message asynchronously.
        debug(message: str) -> None:
            Logs a debug message asynchronously.
        error(message: str) -> None:
            Logs an error message asynchronously.
        warning(message: str) -> None:
            Logs a warning message asynchronously.
        critical(message: str) -> None:
            Logs a critical message asynchronously.
    """

    def __init__(self, log_file=None, log_level="INFO"):
        self.logger = Logger.with_default_handlers(name="areion", level=log_level)

        if log_file:
            # Add an asynchronous file handler if log_file is provided
            file_handler = AsyncFileHandler(log_file)
            self.logger.add_handler(file_handler)

        # Add an asynchronous console handler
        console_handler = AsyncStreamHandler()
        self.logger.add_handler(console_handler)

    async def info(self, message: str) -> None:
        await self.logger.info(message)

    async def debug(self, message: str) -> None:
        await self.logger.debug(message)

    async def error(self, message: str) -> None:
        await self.logger.error(message)

    async def warning(self, message: str) -> None:
        await self.logger.warning(message)

    async def critical(self, message: str) -> None:
        await self.logger.critical(message)

    async def shutdown(self) -> None:
        await self.logger.shutdown()