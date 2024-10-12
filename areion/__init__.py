from .main import AreionServer, AreionServerBuilder, AREION_LOGO, DEFAULT_HOST, DEFAULT_PORT

# Reminds people that people can build their own parts
from .default import (
    Logger as DefaultLogger,
    Engine as DefaultEngine,
    Router as DefaultRouter,
    Orchestrator as DefaultOrchestrator,
)

from .core import (
    HttpResponse,
    HttpRequest,
    HttpRequestFactory,
    HttpServer,
    HTTP_STATUS_CODES,
    HttpError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    InternalServerError,
)

from .base import BaseEngine, BaseLogger, BaseOrchestrator, BaseRouter, BaseMiddleware

from .utils import (
    create_empty_response,
    create_error_response,
    create_html_response,
    create_json_response,
    create_redirect_response,
    create_text_response,
    create_xml_response,
)

__version__ = "v1.1.10"

__all__ = [
    # Main classes
    "AreionServer",
    "AreionServerBuilder",
    # Default Component classes
    "DefaultRouter",
    "DefaultLogger",
    "DefaultOrchestrator",
    "DefaultEngine",
    # Core classes
    "HttpResponse",
    "HttpRequest",
    "HttpRequestFactory",
    "HttpServer",
    "HTTP_STATUS_CODES",
    # Response Utils
    "create_empty_response",
    "create_error_response",
    "create_html_response",
    "create_json_response",
    "create_redirect_response",
    "create_text_response",
    "create_xml_response",
    # Base classes
    "BaseEngine",
    "BaseLogger",
    "BaseOrchestrator",
    "BaseRouter",
    "BaseMiddleware",
    # Exceptions and Status Codes
    "HttpError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "MethodNotAllowedError",
    "InternalServerError",
    # Misc
    AREION_LOGO,
    DEFAULT_HOST,
    DEFAULT_PORT,
]
