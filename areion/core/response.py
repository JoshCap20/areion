import orjson

HTTP_STATUS_CODES: dict[int, str] = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Switch Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    421: "Misdirected Request",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required",
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

    def _infer_content_type(self, body) -> str:
        """
        Infer the content type based on the body type.

        Args:
            body (any): The response body.

        Returns:
            str: The inferred content type.
        """
        if isinstance(body, dict):
            return "application/json"
        elif isinstance(body, str) and body.startswith("<"):
            return "text/html"
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
            return orjson.dumps(self.body)
        elif isinstance(self.body, str):
            return self.body.encode("utf-8")  # Convert string to bytes
        elif isinstance(self.body, bytes):
            return self.body  # Return bytes as-is
        return str(self.body).encode(
            "utf-8"
        )  # Convert other types to string and encode

    def _get_status_phrase(self) -> str:
        """
        Get the standard HTTP status phrase for the given status code.

        Returns:
            str: The status phrase.
        """
        return HTTP_STATUS_CODES.get(self.status_code, "")

    def _get_response_line(self) -> str:
        """
        Get the response line for the HTTP response (e.g., "HTTP/1.1 200 OK").

        Returns:
            str: The HTTP response line.
        """
        return f"HTTP/1.1 {self.status_code} {self._get_status_phrase()}\r\n"

    def _ensure_content_length(self, body) -> None:
        """
        Ensure that the Content-Length header is set based on the body length.

        Args:
            body (bytes): The response body.
        """
        self.headers["Content-Length"] = str(len(body))

    def _format_headers(self) -> str:
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
