from abc import ABC, abstractmethod


class BaseOrchestrator(ABC):
    @abstractmethod
    def submit_task(self, func, *args):
        pass

    @abstractmethod
    def schedule_cron_task(self, func, cron_expression, *args):
        pass

    @abstractmethod
    def shutdown(self):
        pass
