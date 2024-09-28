"""
Custom exceptions for Areion.

These are globally handled in the core server.
"""

from .response import HTTP_STATUS_CODES


class HttpError(Exception):
    """Base class for HTTP errors."""

    status_code: int = 500
    message: str = "Internal Server Error"

    def __init__(self, message: str = None, status_code: int = None):
        self.status_code = status_code or self.status_code
        if status_code and not message:
            self.message = HTTP_STATUS_CODES.get(status_code, "Internal Server Error")
        elif message:
            self.message = message
        super().__init__(self.message)

    def __str__(self):
        return str(self.status_code) + " " + self.message


class BadRequestError(HttpError):
    """400 Bad Request."""

    status_code = 400
    message = "Bad Request"


class UnauthorizedError(HttpError):
    """401 Unauthorized."""

    status_code = 401
    message = "Unauthorized"


class ForbiddenError(HttpError):
    """403 Forbidden."""

    status_code = 403
    message = "Forbidden"


class NotFoundError(HttpError):
    """404 Not Found."""

    status_code = 404
    message = "Not Found"


class MethodNotAllowedError(HttpError):
    """405 Method Not Allowed."""

    status_code = 405
    message = "Method Not Allowed"


class InternalServerError(HttpError):
    """500 Internal Server Error."""

    status_code = 500
    message = "Internal Server Error"
