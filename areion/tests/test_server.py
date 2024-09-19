import unittest
from unittest.mock import Mock, patch, MagicMock
from areion import AreionServer
from http.server import HTTPServer
import socket

class TestAreionServer(unittest.TestCase):

    def setUp(self):
        # Initialize the AreionServer instance for each test
        self.server = AreionServer()
        self.mock_orchestrator = Mock()
        self.mock_router = Mock()
        self.mock_logger = Mock()
        
        self.server.with_port(self._find_free_port())
        
    def _find_free_port(self):
        """Helper function to find a free port for testing"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))  # Bind to an available port
            return s.getsockname()[1]  # Return the free port number

    @patch('http.server.HTTPServer')
    def test_server_starts_correctly(self, mock_http_server):
        # Mock the router's get_handler method
        self.mock_router.get_handler.return_value = Mock()

        # Configure the server
        self.server.with_router(self.mock_router).with_logger(self.mock_logger)

        # Start the server and validate
        self.server.start()

        # Assert that the HTTPServer is initialized with the correct arguments
        mock_http_server.assert_called_with(("localhost", self.server.port), self.mock_router.get_handler.return_value)
        self.mock_logger.info.assert_called_with(f"Starting server on port {self.server.port}")

    @patch('signal.signal')
    @patch('http.server.HTTPServer')
    def test_signal_handling_and_shutdown(self, mock_http_server, mock_signal):
        self.mock_orchestrator.shutdown = Mock()

        # Configure the server with an orchestrator and a router
        self.server.with_orchestrator(self.mock_orchestrator).with_router(self.mock_router).with_logger(self.mock_logger)

        # Simulate the server startup
        self.server.start()

        # Simulate a SIGINT signal
        signal_handler = mock_signal.call_args[0][1]
        signal_handler(signal.SIGINT, None)

        # Check if orchestrator shutdown was called and server shutdown was graceful
        self.mock_orchestrator.shutdown.assert_called_once()
        self.mock_logger.info.assert_called_with("Received shutdown signal. Shutting down server...")

    @patch('http.server.HTTPServer')
    def test_missing_router_raises_error(self, mock_http_server):
        # Start the server without configuring a router
        self.server.with_logger(self.mock_logger)
        self.server.start()

        # Ensure the error was logged
        self.mock_logger.error.assert_called_with("Router missing.")

    def test_component_validation(self):
        # Test valid component
        self.server.with_logger(self.mock_logger)
        self.assertEqual(self.server.logger, self.mock_logger)

        # Test invalid component - passing an invalid orchestrator
        invalid_orchestrator = Mock()
        with self.assertRaises(ValueError):
            self.server.with_orchestrator(invalid_orchestrator)

    @patch('os.path.isdir')
    def test_static_directory_check(self, mock_isdir):
        # Set up static directory check to return False
        mock_isdir.return_value = False
        self.server.with_logger(self.mock_logger).with_static_dir("/invalid/path").with_router(self.mock_router)

        # Start the server
        self.server.start()

        # Check if the logger catches the invalid static directory
        self.mock_logger.error.assert_called_with("Static directory /invalid/path does not exist.")

    @patch('http.server.HTTPServer')
    def test_server_handles_requests(self, mock_http_server):
        # Mock handler response
        handler_mock = MagicMock()
        self.mock_router.get_handler.return_value = handler_mock

        # Configure the server
        self.server.with_router(self.mock_router).with_logger(self.mock_logger)

        # Start the server
        self.server.start()

        # Simulate an HTTP request
        mock_http_server_instance = mock_http_server.return_value
        mock_http_server_instance.handle_request.assert_called()

    def tearDown(self):
        # Ensure server shutdown after every test
        if self.server.orchestrator:
            self.server.orchestrator.shutdown()
