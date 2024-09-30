import orjson
from .date_header_cache import DateHeaderCache

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


class ContentType:
    JSON = "application/json"
    HTML = "text/html"
    OCTET_STREAM = "application/octet-stream"
    PLAIN = "text/plain"

    TYPE_MAP = {
        str: PLAIN,
        dict: JSON,
        bytes: OCTET_STREAM,
    }

    @classmethod
    def map_type_to_content_type(cls, body: any) -> str:
        body_type = type(body)
        if body_type == str and body.startswith("<"):
            return ContentType.HTML
        return cls.TYPE_MAP.get(body_type, cls.PLAIN)


class HttpResponse:
    def __init__(self, body="", status_code=200, content_type=None, headers=None):
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
        self.headers["Server"] = "Areion"

    def _infer_content_type(self, body: any) -> str:
        """
        Infer the content type based on the body type.

        Args:
            body (any): The response body.

        Returns:
            str: The inferred content type.
        """
        return ContentType.map_type_to_content_type(body)

    def _format_body(self) -> bytes:
        """
        Format the body depending on its type (e.g., convert dict to JSON).

        Returns:
            bytes: The formatted body.
        """
        body_type = type(self.body)
        if body_type == dict:
            return orjson.dumps(self.body)
        elif body_type == bytes:
            return self.body
        elif body_type == str:
            return self.body.encode("utf-8")
        return str(self.body).encode("utf-8")

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

    def format_response(self) -> bytes:
        """
        Format the HTTP response, including headers and body.

        Returns:
            bytes: The formatted HTTP response.
        """
        # Format body
        body = self._format_body()
        content_length = len(body)

        # Set headers
        self.headers["Content-Length"] = str(content_length)
        self.headers["Date"] = DateHeaderCache().get_date()

        # Construct response
        response_line = f"HTTP/1.1 {self.status_code} {HTTP_STATUS_CODES.get(self.status_code, '')}\r\n".encode('utf-8')
        headers = b"".join(f"{key}: {value}\r\n".encode('utf-8') for key, value in self.headers.items())

        return response_line + headers + b"\r\n" + body

    def set_header(self, key: str, value: any) -> None:
        """
        Set a header in the response.

        Args:
            key (str): The name of the header.
            value (any): The value of the header.
        """
        self.headers[key] = value

    def set_headers(self, headers: dict) -> None:
        """
        Set multiple headers in the response.

        Args:
            headers (dict): A dictionary of headers to set.
        """
        self.headers.update(headers)

    def set_status_code(self, status_code: int) -> None:
        """
        Set the status code of the response.

        Args:
            status_code (int): The HTTP status code.
        """
        # TODO: Access http_strict flag and enforce here if needed
        if status_code > 599 or status_code < 100:
            raise ValueError(f"Invalid status code: {status_code}")
        self.status_code = status_code

    def __str__(self):
        return f"{self.status_code} {self._get_status_phrase()}"

    def __repr__(self):
        return f"<HttpResponse status_code={self.status_code} content_type={self.content_type} headers={self.headers}>"
