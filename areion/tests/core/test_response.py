import unittest
from areion.core import HttpResponse

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
        
        self.assertIn(b"HTTP/1.1 404 OK", formatted_response)
        self.assertIn(b"Content-Type: text/plain", formatted_response)
        self.assertIn(b"Not Found", formatted_response)

    def test_custom_content_type(self):
        body = "<xml><data>Hello</data></xml>"
        response = HttpResponse(body=body, content_type="application/xml")
        formatted_response = response.format_response()
        
        self.assertIn(b"HTTP/1.1 200 OK", formatted_response)
        self.assertIn(b"Content-Type: application/xml", formatted_response)
        self.assertIn(b"Hello", formatted_response)

if __name__ == "__main__":
    unittest.main()