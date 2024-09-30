import unittest
from unittest.mock import Mock, call
from areion.core.request_builder import RequestBuilder
from areion.core.exceptions import HttpError
import httptools

class TestRequestBuilder(unittest.TestCase):
    def setUp(self):
        self.request_factory = Mock()
        self.request_builder = RequestBuilder(self.request_factory)
        self.request_builder.parser = Mock()

    def test_on_url(self):
        self.request_builder.on_url(b'/test')
        self.assertEqual(self.request_builder.path, '/test')

    def test_on_header(self):
        self.request_builder.on_header(b'Content-Type', b'application/json')
        self.assertEqual(self.request_builder.headers['content-type'], 'application/json')

    def test_on_headers_complete(self):
        self.request_builder.parser.get_method = Mock(return_value="GET")
        self.request_builder.parser.get_http_version = Mock(return_value="HTTP/1.1")
        self.request_builder.on_headers_complete()
        self.assertEqual(self.request_builder.method, 'GET')
        self.assertEqual(self.request_builder.http_version, 'HTTP/1.1')

    def test_on_body(self):
        self.request_builder.on_body(b'{"key": "value"}')
        self.assertEqual(self.request_builder.body, b'{"key": "value"}')

    def test_on_message_complete(self):
        self.request_builder.method = 'GET'
        self.request_builder.path = '/test'
        self.request_builder.headers = {'content-type': 'application/json'}
        self.request_builder.body = b'{"key": "value"}'
        self.request_builder.request_factory.create = Mock(return_value='request_object')
        
        self.request_builder.on_message_complete()
        self.assertEqual(self.request_builder.get_request(), 'request_object')
        self.request_factory.create.assert_called_once_with(
            method='GET',
            path='/test',
            headers={'content-type': 'application/json'},
            body=b'{"key": "value"}'
        )

    def test_feed_data(self):
        data = b'GET /test HTTP/1.1\r\nHost: example.com\r\n\r\n'
        self.request_builder.parser.feed_data = Mock()
        self.request_builder.feed_data(data)
        self.request_builder.parser.feed_data.assert_called_once_with(data)

    def test_feed_data_populates_request(self):
        data = b'GET /test HTTP/1.1\r\nHost: example.com\r\n\r\n'
        self.request_builder.parser.is_message_complete = Mock(return_value=True)
        self.request_builder.get_request = Mock(return_value='request_object')
        self.request_builder._handle_http_request = Mock(return_value='response_object')
        self.request_builder.feed_data(data)
        self.request_builder.get_request.assert_called_once()
        self.request_builder._handle_http_request.assert_called_once_with('request_object')
        

    def test_feed_data_with_error(self):
        data = b'INVALID DATA'
        self.request_builder.parser.feed_data = Mock(side_effect=httptools.HttpParserError)
        with self.assertRaises(HttpError):
            self.request_builder.feed_data(data)

if __name__ == '__main__':
    unittest.main()