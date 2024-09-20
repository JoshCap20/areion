import unittest
from unittest.mock import Mock
from areion.core import HttpRequest, HttpRequestFactory


class TestHttpRequest(unittest.TestCase):

    def setUp(self):
        self.method = "GET"
        self.path = "/test"
        self.headers = {"Content-Type": "application/json"}
        self.request = HttpRequest(self.method, self.path, self.headers)

    def test_initialization(self):
        self.assertEqual(self.request.method, self.method)
        self.assertEqual(self.request.path, self.path)
        self.assertEqual(self.request.headers, self.headers)
        self.assertEqual(self.request.metadata, {})

    def test_add_header(self):
        self.request.add_header("Authorization", "Bearer token")
        self.assertEqual(self.request.get_header("Authorization"), "Bearer token")

    def test_get_header(self):
        self.assertEqual(self.request.get_header("Content-Type"), "application/json")
        self.assertIsNone(self.request.get_header("Non-Existent-Header"))

    def test_add_metadata(self):
        self.request.add_metadata("user_id", 123)
        self.assertEqual(self.request.get_metadata("user_id"), 123)

    def test_get_metadata(self):
        self.assertIsNone(self.request.get_metadata("non_existent_key"))
        self.request.add_metadata("session_id", "abc123")
        self.assertEqual(self.request.get_metadata("session_id"), "abc123")

    def test_repr(self):
        expected_repr = f"<HttpRequest method={self.method} path={self.path} headers={self.headers} metadata={{}}>"
        self.assertEqual(repr(self.request), expected_repr)

    def test_as_dict_default(self):
        expected_dict = {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
        }
        self.assertEqual(self.request.as_dict(), expected_dict)

    def test_as_dict_with_components(self):
        self.request.logger = Mock()
        self.request.engine = Mock()
        self.request.orchestrator = Mock()
        expected_dict = {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "metadata": self.request.metadata,
            "logger": self.request.logger,
            "engine": self.request.engine,
            "orchestrator": self.request.orchestrator,
        }
        self.assertEqual(self.request.as_dict(show_components=True), expected_dict)

    def test_as_dict_without_components(self):
        expected_dict = {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
        }
        self.assertEqual(self.request.as_dict(show_components=False), expected_dict)

    def test_add_header_overwrite(self):
        self.request.add_header("Content-Type", "text/plain")
        self.assertEqual(self.request.get_header("Content-Type"), "text/plain")

    def test_add_metadata_overwrite(self):
        self.request.add_metadata("user_id", 123)
        self.request.add_metadata("user_id", 456)
        self.assertEqual(self.request.get_metadata("user_id"), 456)

    def test_empty_headers(self):
        request = HttpRequest(self.method, self.path, {})
        self.assertEqual(request.headers, {})

    def test_empty_metadata(self):
        self.assertEqual(self.request.metadata, {})

    def test_none_header_value(self):
        self.request.add_header("X-Test-Header", None)
        self.assertIsNone(self.request.get_header("X-Test-Header"))

    def test_none_metadata_value(self):
        self.request.add_metadata("test_key", None)
        self.assertIsNone(self.request.get_metadata("test_key"))

    def test_large_headers(self):
        large_headers = {f"Header-{i}": f"Value-{i}" for i in range(1000)}
        request = HttpRequest(self.method, self.path, large_headers)
        self.assertEqual(request.headers, large_headers)

    def test_large_metadata(self):
        for i in range(1000):
            self.request.add_metadata(f"key-{i}", f"value-{i}")
        for i in range(1000):
            self.assertEqual(self.request.get_metadata(f"key-{i}"), f"value-{i}")

    def test_special_characters_in_headers(self):
        special_header = "X-Special-Header"
        special_value = "Value!@#$%^&*()_+"
        self.request.add_header(special_header, special_value)
        self.assertEqual(self.request.get_header(special_header), special_value)

    def test_special_characters_in_metadata(self):
        special_key = "special_key!@#$%^&*()_+"
        special_value = "Value!@#$%^&*()_+"
        self.request.add_metadata(special_key, special_value)
        self.assertEqual(self.request.get_metadata(special_key), special_value)

    def test_render_template(self):
        mock_engine = Mock()
        mock_engine.render.return_value = "Rendered Content"
        self.request.engine = mock_engine
        result = self.request.render_template("template.html", {"key": "value"})
        self.assertEqual(result, "Rendered Content")
        mock_engine.render.assert_called_once_with("template.html", {"key": "value"})

    def test_render_template(self):
        mock_engine = Mock()
        mock_engine.render.return_value = "Rendered Content"
        self.request.engine = mock_engine
        result = self.request.render_template("template.html", {"key": "value"})
        self.assertEqual(result, "Rendered Content")
        mock_engine.render.assert_called_once_with("template.html", {"key": "value"})

    def test_render_template_no_engine(self):
        self.request.engine = None
        with self.assertRaises(ValueError) as context:
            self.request.render_template("template.html")
        self.assertEqual(
            str(context.exception),
            "No template engine available to render the template.",
        )

    def test_render_template_default_context(self):
        mock_engine = Mock()
        mock_engine.render.return_value = "Rendered Content"
        self.request.engine = mock_engine
        result = self.request.render_template("template.html")
        self.assertEqual(result, "Rendered Content")
        mock_engine.render.assert_called_once_with("template.html", {})

    def test_submit_task(self):
        mock_orchestrator = Mock()
        mock_orchestrator.submit_task.return_value = "Task Submitted"
        self.request.orchestrator = mock_orchestrator
        result = self.request.submit_task("task_name", "arg1", "arg2")
        self.assertEqual(result, "Task Submitted")
        mock_orchestrator.submit_task.assert_called_once_with(
            "task_name", "arg1", "arg2"
        )

    def test_submit_task_no_orchestrator(self):
        self.request.orchestrator = None
        with self.assertRaises(ValueError) as context:
            self.request.submit_task("task_name")
        self.assertEqual(
            str(context.exception), "No orchestrator available to submit the task."
        )

    def test_log(self):
        mock_logger = Mock()
        self.request.logger = mock_logger
        self.request.log("Test message", "info")
        mock_logger.info.assert_called_once_with("Test message")

    def test_log_no_logger(self):
        self.request.logger = None
        self.request.log("Test message", "info")  # Should not raise an exception


class TestHttpRequestFactory(unittest.TestCase):

    def setUp(self):
        self.logger = Mock()
        self.engine = Mock()
        self.orchestrator = Mock()
        self.factory = HttpRequestFactory(
            logger=self.logger, engine=self.engine, orchestrator=self.orchestrator
        )

    def test_create(self):
        method = "POST"
        path = "/create"
        headers = {"Authorization": "Bearer token"}
        request = self.factory.create(method, path, headers)
        self.assertEqual(request.method, method)
        self.assertEqual(request.path, path)
        self.assertEqual(request.headers, headers)
        self.assertEqual(request.logger, self.logger)
        self.assertEqual(request.engine, self.engine)
        self.assertEqual(request.orchestrator, self.orchestrator)

    def test_create_no_logger(self):
        factory = HttpRequestFactory(engine=self.engine, orchestrator=self.orchestrator)
        request = factory.create("GET", "/path", {})
        self.assertIsNone(request.logger)
        self.assertEqual(request.engine, self.engine)
        self.assertEqual(request.orchestrator, self.orchestrator)

    def test_create_no_engine(self):
        factory = HttpRequestFactory(logger=self.logger, orchestrator=self.orchestrator)
        request = factory.create("GET", "/path", {})
        self.assertEqual(request.logger, self.logger)
        self.assertIsNone(request.engine)
        self.assertEqual(request.orchestrator, self.orchestrator)

    def test_create_no_orchestrator(self):
        factory = HttpRequestFactory(logger=self.logger, engine=self.engine)
        request = factory.create("GET", "/path", {})
        self.assertEqual(request.logger, self.logger)
        self.assertEqual(request.engine, self.engine)
        self.assertIsNone(request.orchestrator)


if __name__ == "__main__":
    unittest.main()
