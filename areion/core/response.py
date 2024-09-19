import json

HTTP_STATUS_CODES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    503: "Service Unavailable",
}


class HttpResponse:
    def __init__(self, body=None, status_code=200, content_type=None, headers=None):
        """
        Initializes the HttpResponse object.

        Args:
            body (any): The response body, which could be a dict (for JSON), string (for HTML/text), or bytes (for files).
            status_code (int): The HTTP status code.
            content_type (str, optional): The content type (e.g., "application/json"). If not specified, it will be inferred from the body type.
            headers (dict, optional): Any additional headers to include in the response.
        """
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}
        self.content_type = content_type or self._infer_content_type(body)

        self.headers["Content-Type"] = self.content_type

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
        return "text/plain"  # Default content type

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

    def _get_status_phrase(self):
        """
        Get the standard HTTP status phrase for the given status code.

        Returns:
            str: The status phrase.
        """
        return HTTP_STATUS_CODES.get(self.status_code, "")

    def _get_response_line(self):
        """
        Get the response line for the HTTP response (e.g., "HTTP/1.1 200 OK").

        Returns:
            str: The HTTP response line.
        """
        return f"HTTP/1.1 {self.status_code} {self._get_status_phrase()}\r\n"

    def _ensure_content_length(self, body):
        """
        Ensure that the Content-Length header is set based on the body length.

        Args:
            body (bytes): The response body.
        """
        self.headers["Content-Length"] = str(len(body))

    def _format_headers(self):
        """
        Format the headers for the HTTP response.

        Returns:
            str: The formatted headers.
        """
        return "".join(f"{key}: {value}\r\n" for key, value in self.headers.items())

    def format_response(self) -> bytes:
        """
        Format the HTTP response, including headers and body.

        Returns:
            bytes: The formatted HTTP response.
        """
        body = self._format_body()
        self._ensure_content_length(body)
        response_line = self._get_response_line()
        headers = self._format_headers()

        return (response_line + headers + "\r\n").encode("utf-8") + body
