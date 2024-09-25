from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from apscheduler.schedulers.background import BackgroundScheduler
from ..base import BaseOrchestrator

# TODO: Add Redis support for tasks


class Orchestrator(BaseOrchestrator):
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = []
        self.scheduler = BackgroundScheduler()
        self.logger = None  # Builder injects logger component

    def start(self) -> None:
        self.log(
            "info",
            f"Orchestrator started. Thread pool initialized with {self.executor._max_workers} workers.",
        )
        self.scheduler.start()
        self.run_tasks()  # Run any pending tasks immediately

    def submit_task(self, func: callable, *args) -> Future:
        task_name = getattr(func, "__name__", "unnamed_task")
        future = self.executor.submit(func, *args)
        self.tasks.append(future)
        self.log(
            "info",
            f"Task {task_name} submitted.",
        )
        return future

    def set_logger(self, logger) -> None:
        self.logger = logger

    def run_tasks(self) -> None:
        self.log(
            "info",
            f"Running {len(self.tasks)} tasks concurrently.",
        )
        for future in as_completed(self.tasks):
            try:
                result = future.result()
                self.log(
                    "info",
                    f"Task completed with result: {result}",
                )
            except Exception as e:
                self.log(
                    "error",
                    f"Task generated an exception: {e}",
                )

    def schedule_cron_task(self, func, cron_expression, *args) -> None:
        if not all(
            key in ["second", "minute", "hour", "day", "month", "year"]
            for key in cron_expression
        ):
            raise ValueError("Invalid cron expression")

        task_name = getattr(func, "__name__", "unnamed_task")
        self.log(
            "info",
            f"Scheduling task {task_name} with cron expression: {cron_expression}",
        )
        self.scheduler.add_job(func, "cron", *args, id=task_name, **cron_expression)

    def shutdown(self):
        # TODO: Orchestrator clean up work here
        self.scheduler.shutdown(wait=False)
        self.executor.shutdown(wait=True)

    def log(self, level: str, message: str) -> None:
        # Safe logging method (bug fix for scheduled tasks before server is ran)
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message)
        else:
            print(f"[{level.upper()}] {message}")
