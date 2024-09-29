from .main import (
    AreionServer,
    AreionServerBuilder,
    AREION_LOGO,
    DEFAULT_HOST,
    DEFAULT_PORT,
)

# Reminds people that people can build their own parts
from .default.logger import Logger as DefaultLogger
from .default.engine import Engine as DefaultEngine
from .default.router import Router as DefaultRouter
from .default.orchestrator import Orchestrator as DefaultOrchestrator

from .core import (
    __core__,
    __exceptions__,
    __response_utils__,
)

from .base import BaseEngine, BaseLogger, BaseOrchestrator, BaseRouter, BaseMiddleware

__version__ = "v1.1.7"

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
    *__core__,
    *__exceptions__,
    *__response_utils__,
    # Base classes
    "BaseEngine",
    "BaseLogger",
    "BaseOrchestrator",
    "BaseRouter",
    "BaseMiddleware",
    # Misc
    AREION_LOGO,
    DEFAULT_HOST,
    DEFAULT_PORT,
]
