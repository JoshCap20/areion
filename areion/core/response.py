class HttpResponse:
    def __init__(
        self, status_code: int = 200, content_type: str = "text/html", body: str = ""
    ):
        self.status_code = status_code
        self.content_type = content_type
        self.body = body

    def format_response(self) -> bytes:
        """
        Format the HTTP response.
        """
        response_line = f"HTTP/1.1 {self.status_code} OK\r\n"
        headers = f"Content-Type: {self.content_type}\r\n"
        headers += f"Content-Length: {len(self.body.encode('utf-8'))}\r\n"
        return (response_line + headers + "\r\n" + self.body).encode("utf-8")
