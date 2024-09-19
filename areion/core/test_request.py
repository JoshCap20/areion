import unittest
from areion.core import HttpRequest

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

    def test_as_dict(self):
        expected_dict = {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "metadata": {}
        }
        self.assertEqual(self.request.as_dict(), expected_dict)

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

if __name__ == "__main__":
    unittest.main()