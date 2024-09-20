from .base import ABC, abstractmethod


class BaseMiddleware(ABC):
    @abstractmethod
    def handle(self, request):
        """
        Receives and returns a request object.
        """
        pass
