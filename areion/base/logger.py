from .base import ABC, abstractmethod


class BaseLogger(ABC):
    @abstractmethod
    def info(self, message):
        pass

    @abstractmethod
    def error(self, message):
        pass
