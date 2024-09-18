import unittest
from unittest.mock import Mock
from areion.default import Orchestrator

class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        self.orchestrator = Orchestrator(max_workers=2)

    def test_task_submission(self):
        mock_task = Mock()
        self.orchestrator.submit_task(mock_task)
        mock_task.assert_called()
    
    def test_task_concurrency(self):
        task1 = Mock()
        task2 = Mock()
        self.orchestrator.submit_task(task1)
        self.orchestrator.submit_task(task2)
        self.orchestrator.run_tasks()

        task1.assert_called()
        task2.assert_called()
