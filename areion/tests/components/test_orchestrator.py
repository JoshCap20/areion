import unittest
from unittest.mock import Mock, patch
from areion.default import Orchestrator
from concurrent.futures import ThreadPoolExecutor


class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        self.orchestrator = Orchestrator(max_workers=2)
        self.logger = Mock()
        self.orchestrator.set_logger(self.logger)

    # Base functionality: Test task submission
    def test_task_submission(self):
        mock_task = Mock()
        self.orchestrator.submit_task(mock_task)
        mock_task.assert_called_once()

    # Base functionality: Test multiple task submission and concurrency
    def test_task_concurrency(self):
        task1 = Mock()
        task2 = Mock()

        self.orchestrator.submit_task(task1)
        self.orchestrator.submit_task(task2)
        self.orchestrator.run_tasks()

        task1.assert_called_once()
        task2.assert_called_once()

    # Test task result handling and return values
    def test_task_return_values(self):
        def task():
            return "Task completed"

        future = self.orchestrator.submit_task(task)
        self.orchestrator.run_tasks()

        self.assertEqual(future.result(), "Task completed")

    # Test scheduling tasks with cron expressions
    @patch("apscheduler.schedulers.background.BackgroundScheduler.add_job")
    def test_schedule_cron_task(self, mock_add_job):
        mock_task = Mock()
        cron_expression = {"second": "*/10"}

        mock_task.__name__ = "test_task"

        self.orchestrator.schedule_cron_task(mock_task, cron_expression)

        mock_add_job.assert_called_once_with(
            mock_task, "cron", id=mock_task.__name__, **cron_expression
        )

    # Edge case: Task with exceptions (ensure it doesnt raise error to stop thread, just logs)
    def test_task_exception_handling(self):
        def task_with_exception():
            raise ValueError("Test Exception")

        self.orchestrator.submit_task(task_with_exception)

        # TODO: Test for logging on error later

    @patch.object(ThreadPoolExecutor, "shutdown", return_value=None)
    @patch("apscheduler.schedulers.background.BackgroundScheduler.shutdown")
    def test_orchestrator_shutdown(
        self, mock_scheduler_shutdown, mock_executor_shutdown
    ):
        orchestrator = Orchestrator(max_workers=2)
        orchestrator.shutdown()

        mock_scheduler_shutdown.assert_called_once()
        mock_executor_shutdown.assert_called_once()

    # Test cron scheduling edge cases (invalid cron expression)
    @patch("apscheduler.schedulers.background.BackgroundScheduler.add_job")
    def test_schedule_cron_task_invalid(self, mock_add_job):
        mock_task = Mock()
        invalid_cron_expression = {"invalid": "value"}

        with self.assertRaises(ValueError):
            self.orchestrator.schedule_cron_task(mock_task, invalid_cron_expression)

    # Test multiple cron tasks scheduled
    @patch("apscheduler.schedulers.background.BackgroundScheduler.add_job")
    def test_multiple_cron_tasks(self, mock_add_job):
        mock_task_1 = Mock()
        mock_task_2 = Mock()

        # Provide a default __name__ for these tasks
        mock_task_1.__name__ = "task1"
        mock_task_2.__name__ = "task2"

        cron_expression_1 = {"minute": "*/5"}
        cron_expression_2 = {"hour": "*/1"}

        self.orchestrator.schedule_cron_task(mock_task_1, cron_expression_1)
        self.orchestrator.schedule_cron_task(mock_task_2, cron_expression_2)

        mock_add_job.assert_any_call(
            mock_task_1, "cron", id=mock_task_1.__name__, **cron_expression_1
        )
        mock_add_job.assert_any_call(
            mock_task_2, "cron", id=mock_task_2.__name__, **cron_expression_2
        )

    # Edge case: Cron task missing name
    def test_cron_task_no_name(self):
        mock_task = Mock()
        delattr(
            mock_task, "__name__"
        )  # Remove the __name__ attribute to simulate missing task name

        cron_expression = {"second": "*/10"}
        self.orchestrator.schedule_cron_task(mock_task, cron_expression)

        self.assertIn("unnamed_task", self.orchestrator.scheduler.get_jobs()[0].id)

    # Test task submission with arguments
    def test_task_submission_with_arguments(self):
        def task_with_args(arg1, arg2):
            return f"Task received: {arg1}, {arg2}"

        future = self.orchestrator.submit_task(
            task_with_args, "arg1_value", "arg2_value"
        )
        self.orchestrator.run_tasks()

        self.assertEqual(future.result(), "Task received: arg1_value, arg2_value")

    # Edge case: Empty task submission
    def test_empty_task_submission(self):
        with self.assertRaises(TypeError):
            self.orchestrator.submit_task()

    # Test orchestrator max workers limit
    def test_max_workers_limit(self):
        task1 = Mock()
        task2 = Mock()
        task3 = Mock()

        self.orchestrator.submit_task(task1)
        self.orchestrator.submit_task(task2)
        self.orchestrator.submit_task(
            task3
        )  # Should not raise an error, but will queue

        self.orchestrator.run_tasks()

        task1.assert_called_once()
        task2.assert_called_once()
        task3.assert_called_once()
