import httptools
from .exceptions import HttpError
from .request import HttpRequest
from .response import HTTP_STATUS_CODES

class RequestBuilder:
    def __init__(self, request_factory):
        self.request_factory = request_factory
        self.reset()

    def reset(self):
        self.method = None
        self.path = None
        self.http_version = None
        self.headers = {}
        self.body = bytearray()
        self.parser = httptools.HttpRequestParser(self)
        print("RequestBuilder reset.")

    def on_message_begin(self):
        print("RequestBuilder on_message_begin.")

    def on_url(self, url: bytes):
        self.path = url.decode('utf-8')
        print(f"RequestBuilder on_url: {self.path}")

    def on_header(self, name: bytes, value: bytes):
        self.headers[name.decode('utf-8').lower()] = value.decode('utf-8')
        print(f"RequestBuilder on_header: {name.decode('utf-8').lower()}={value.decode('utf-8')}")
    def on_headers_complete(self):
        self.method = httptools.http_method_str(self.parser.get_method()).decode('utf-8')
        self.http_version = f"HTTP/{self.parser.get_http_version() // 10}.{self.parser.get_http_version() % 10}"
        print(f"RequestBuilder on_headers_complete: {self.method} {self.http_version}")
    def on_body(self, body: bytes):
        self.body.extend(body)
        print(f"RequestBuilder on_body: {body}")
    def on_message_complete(self):
        print("RequestBuilder on_message_complete.")
        try:
            self.request = self.request_factory.create(
                method=self.method,
                path=self.path,
                headers=self.headers,
                body=bytes(self.body)
            )
            print(f"RequestBuilder on_message_complete: {self.request}")
        except Exception as e:
            print(f"RequestBuilder on_message_complete: {e}")
            raise HttpError(status_code=400, message=HTTP_STATUS_CODES[400] + str(e)) from e

    def feed_data(self, data):
        try:
            self.parser.feed_data(data)
            print(f"RequestBuilder feed_data: {data}")
        except httptools.HttpParserError as e:
            print (f"RequestBuilder feed_data: {e}")
            raise HttpError(status_code=400, message=HTTP_STATUS_CODES[400] + str(e)) from e

    def get_request(self):
        return self.request
