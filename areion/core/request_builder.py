import httptools
from .exceptions import HttpError
from .request import HttpRequest
from .response import HTTP_STATUS_CODES

class RequestBuilder:
    def __init__(self, request_factory):
        self.request_factory = request_factory
        self.reset()

    def reset(self):
        self.is_message_complete = False
        self.method = None
        self.path = None
        self.http_version = None
        self.headers = {}
        self.body = bytearray()
        self.parser = httptools.HttpRequestParser(self)

    def on_message_begin(self):
        pass

    def on_url(self, url: bytes):
        self.path = url.decode('utf-8')

    def on_header(self, name: bytes, value: bytes):
        self.headers[name.decode('utf-8').lower()] = value.decode('utf-8')

    def on_headers_complete(self):
        self.method = self.parser.get_method()
        self.http_version = self.parser.get_http_version()
    
    def on_body(self, body: bytes):
        self.body.extend(body)
    
    def on_message_complete(self):
        try:
            self.is_message_complete = True
            self.request = self.request_factory.create(
                method=self.method,
                path=self.path,
                headers=self.headers,
                body=bytes(self.body),
                http_version=self.http_version
            )
        except Exception as e:
            raise HttpError(status_code=400, message=HTTP_STATUS_CODES[400] + str(e)) from e

    def feed_data(self, data):
        try:
            self.parser.feed_data(data)
        except httptools.HttpParserError as e:
            raise HttpError(status_code=400, message=HTTP_STATUS_CODES[400] + str(e)) from e

    def get_request(self):
        return self.request
