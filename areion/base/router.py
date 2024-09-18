from .base import ABC, abstractmethod


class BaseRouter(ABC):
    @abstractmethod
    def add_route(self, route, handler, methods):
        pass
    
    @abstractmethod
    def get_handler(self, server):
        pass