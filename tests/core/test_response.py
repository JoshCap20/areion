import unittest
from areion.core import HttpResponse, HTTP_STATUS_CODES


class TestHttpResponse(unittest.TestCase):
    def test_json_response(self):
        body = {"key": "value"}
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: application/json", formatted_response)
        self.assertIn(b'"key": "value"', formatted_response)

    def test_html_response(self):
        body = "<html><body>Hello, World!</body></html>"
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: text/html", formatted_response)
        self.assertIn(b"Hello, World!", formatted_response)

    def test_text_response(self):
        body = "Hello, World!"
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn(b"Hello, World!", formatted_response)

    def test_bytes_response(self):
        body = b"binary data"
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: application/octet-stream", formatted_response)
        self.assertIn(b"binary data", formatted_response)

    def test_custom_status_code(self):
        body = "Not Found"
        response = HttpResponse(body=body, status_code=404)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 404 Not Found", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn(b"Not Found", formatted_response)

    def test_custom_content_type(self):
        body = "<xml><data>Hello</data></xml>"
        response = HttpResponse(body=body, content_type="application/xml")
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: application/xml", formatted_response)
        self.assertIn(b"Hello", formatted_response)

    def test_empty_body(self):
        body = ""
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn(b"", formatted_response)

    def test_none_body(self):
        body = None
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn(b"", formatted_response)

    def test_large_body(self):
        body = "A" * 10000
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn(b"A" * 10000, formatted_response)

    def test_special_characters_body(self):
        body = "Hello, 世界!"
        response = HttpResponse(body=body)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn("Hello, 世界!".encode("utf-8"), formatted_response)

    def test_custom_headers(self):
        body = "Hello, World!"
        headers = {"X-Custom-Header": "CustomValue"}
        response = HttpResponse(body=body, headers=headers)
        formatted_response = response.format_response()

        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn(b"X-Custom-Header: CustomValue", formatted_response)
        self.assertIn(b"Hello, World!", formatted_response)

    def test_status_codes(self):
        for status_code, status_phrase in HTTP_STATUS_CODES.items():
            with self.subTest(status_code=status_code):
                body = f"Status {status_code}"
                response = HttpResponse(body=body, status_code=status_code)
                formatted_response = response.format_response()

                self.assertIn(
                    f"HTTP/1.1 {status_code} {status_phrase}".encode("utf-8"),
                    formatted_response,
                )
                self.assertIn(b"Content-Type: text/plain", formatted_response)
                self.assertIn(
                    f"Status {status_code}".encode("utf-8"), formatted_response
                )

    def test_infer_content_type(self):
        self.assertEqual(
            HttpResponse()._infer_content_type({"key": "value"}), "application/json"
        )
        self.assertEqual(HttpResponse()._infer_content_type("<html>"), "text/html")
        self.assertEqual(HttpResponse()._infer_content_type("plain text"), "text/plain")
        self.assertEqual(
            HttpResponse()._infer_content_type(b"bytes"), "application/octet-stream"
        )
        self.assertEqual(HttpResponse()._infer_content_type(None), "text/plain")


if __name__ == "__main__":
    unittest.main()
