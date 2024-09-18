from .base import ABC, abstractmethod


class BaseEngine(ABC):
    @abstractmethod
    def render(self, template_name, context):
        pass
