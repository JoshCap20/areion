import json


class HttpResponse:
    def __init__(self, body=None, status_code=200, content_type=None):
        """
        Initializes the HttpResponse object.

        Args:
            body (any): The response body, which could be a dict (for JSON), string (for HTML/text), or bytes (for files).
            status_code (int): The HTTP status code.
            content_type (str, optional): The content type (e.g., "application/json"). If not specified, it will be inferred from the body type.
        """
        self.status_code = status_code
        self.body = body
        self.content_type = content_type or self._infer_content_type(body)

    def _infer_content_type(self, body):
        """
        Infer the content type based on the body type.

        Args:
            body (any): The response body.

        Returns:
            str: The inferred content type.
        """
        if isinstance(body, dict):
            return "application/json"
        elif isinstance(body, str):
            return "text/html" if "<html" in body else "text/plain"
        elif isinstance(body, bytes):
            return "application/octet-stream"
        return "text/plain"

    def _format_body(self):
        """
        Format the body depending on its type (e.g., convert dict to JSON).

        Returns:
            str or bytes: The formatted body.
        """
        if isinstance(self.body, dict):
            return json.dumps(self.body).encode("utf-8")  # Convert dict to JSON
        elif isinstance(self.body, str):
            return self.body.encode("utf-8")  # Convert string to bytes
        elif isinstance(self.body, bytes):
            return self.body  # Return bytes as-is
        return str(self.body).encode(
            "utf-8"
        )  # Convert other types to string and encode

    def format_response(self) -> bytes:
        """
        Format the HTTP response, including headers and body.

        Returns:
            bytes: The formatted HTTP response.
        """
        body = self._format_body()
        response_line = f"HTTP/1.1 {self.status_code} OK\r\n"
        headers = f"Content-Type: {self.content_type}\r\n"
        headers += f"Content-Length: {len(body)}\r\n"
        return (response_line + headers + "\r\n").encode("utf-8") + body
