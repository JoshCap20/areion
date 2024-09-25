from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from apscheduler.schedulers.background import BackgroundScheduler
from ..base import BaseOrchestrator

# TODO: Add Redis support for tasks


class Orchestrator(BaseOrchestrator):
    """
    Orchestrator class for managing and executing tasks asynchronously.

    Attributes:
        executor (ThreadPoolExecutor): The thread pool executor for running tasks.
        tasks (list): A list to store the futures of submitted tasks.
        scheduler (BackgroundScheduler): The scheduler for managing cron tasks.
        logger (Logger): The logger component for logging messages.

    Methods:
        __init__(self, max_workers=4):
            Initializes the Orchestrator with a specified number of worker threads.

        start(self) -> None:

        submit_task(self, func: callable, *args) -> Future:

        set_logger(self, logger) -> None:

        run_tasks(self) -> None:

        schedule_cron_task(self, func, cron_expression, *args) -> None:

        shutdown(self):
            Shuts down the scheduler and executor, performing any necessary cleanup.

        log(self, level: str, message: str) -> None:
            Logs a message at the specified log level using the injected logger.
    """

    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = []
        self.scheduler = BackgroundScheduler()
        self.logger = None  # Builder injects logger component

    def start(self) -> None:
        """
        Starts the orchestrator by initializing the scheduler and running any pending tasks.

        This method performs the following actions:
        1. Logs an informational message indicating that the orchestrator has started and the thread pool has been initialized.
        2. Starts the scheduler.
        3. Runs any pending tasks immediately.

        Returns:
            None
        """
        self.log(
            "info",
            f"Orchestrator started. Thread pool initialized with {self.executor._max_workers} workers.",
        )
        self.scheduler.start()
        self.run_tasks()  # Run any pending tasks immediately

    def submit_task(self, func: callable, *args) -> Future:
        """
        Submits a task to the executor for asynchronous execution.

        Args:
            func (callable): The function to be executed asynchronously.
            *args: Variable length argument list to be passed to the function.

        Returns:
            Future: A Future object representing the execution of the task.

        Logs:
            info: Logs the submission of the task with its name.
        """
        task_name = getattr(func, "__name__", "unnamed_task")
        future = self.executor.submit(func, *args)
        self.tasks.append(future)
        self.log(
            "info",
            f"Task {task_name} submitted.",
        )
        return future

    def set_logger(self, logger) -> None:
        """
        Used by AerionServerBuilder to inject a logger component into the orchestrator.
        """
        self.logger = logger

    def run_tasks(self) -> None:
        """
        Executes all tasks concurrently and logs their results.

        This method runs all tasks stored in `self.tasks` concurrently. It logs the
        number of tasks being run, and for each task, it logs either the result of
        the task or any exception that was raised during its execution.

        Raises:
            Exception: If any task generates an exception, it will be caught and
                       logged as an error.
        """
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
        """
        Schedules a function to be executed based on a cron expression.

        Args:
            func (callable): The function to be scheduled.
            cron_expression (dict): A dictionary representing the cron expression.
            The keys should be one or more of ["second", "minute", "hour", "day", "month", "year"].
            *args: Additional arguments to pass to the function when it is called.

        Raises:
            ValueError: If the cron_expression contains invalid keys.

        Logs:
            Schedules the task and logs the task name and cron expression.
        """
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
