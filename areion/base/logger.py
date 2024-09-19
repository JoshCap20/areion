from .base import ABC, abstractmethod


class BaseLogger(ABC):
    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def debug(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass
