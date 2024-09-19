from concurrent.futures import ThreadPoolExecutor, as_completed
from apscheduler.schedulers.background import BackgroundScheduler
from ..base import BaseOrchestrator


class Orchestrator(BaseOrchestrator):
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = []
        self.scheduler = BackgroundScheduler()
        print("Orchestrator initialized with thread pool of", max_workers, "workers.")

    def start(self):
        print("Orchestrator running.")
        self.scheduler.start()
        self.run_tasks()  # Run any pending tasks immediately

    def submit_task(self, func, *args):
        task_name = getattr(func, "__name__", "unnamed_task")
        future = self.executor.submit(func, *args)
        self.tasks.append(future)
        print(f"Task {task_name} submitted.")
        return future

    def run_tasks(self):
        print("Running tasks concurrently.")
        for future in as_completed(self.tasks):
            try:
                result = future.result()
                print(f"Task completed with result: {result}")
            except Exception as e:
                print(f"Task generated an exception: {e}")

    def schedule_cron_task(self, func, cron_expression, *args):
        if not all(
            key in ["second", "minute", "hour", "day", "month", "year"]
            for key in cron_expression
        ):
            raise ValueError("Invalid cron expression")

        task_name = getattr(func, "__name__", "unnamed_task")
        print(f"Scheduling task {task_name} with cron expression: {cron_expression}")
        self.scheduler.add_job(func, "cron", *args, id=task_name, **cron_expression)

    def shutdown(self):
        print("Shutting down Orchestrator...")
        self.scheduler.shutdown(wait=False)
        self.executor.shutdown(wait=True)
        print("Orchestrator shutdown complete.")
