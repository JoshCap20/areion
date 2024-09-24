"""
TODO: Fix timeout issues with tests to ensure builds don't hang
"""
# import asyncio
# import unittest
# from unittest.mock import AsyncMock, MagicMock, patch
# from ... import HttpServer, HttpResponse, HttpRequest


# class TestHttpServer(unittest.TestCase):
#     def setUp(self):
#         self.router = MagicMock()
#         self.request_factory = MagicMock()
#         self.logger = MagicMock()
#         self.server = HttpServer(
#             router=self.router,
#             request_factory=self.request_factory,
#             host="localhost",
#             port=8080,
#             max_conns=1000,
#             buffer_size=8192,
#             keep_alive_timeout=60,
#         )
#         self.server.logger = self.logger  # Mock the logger

#     @patch("asyncio.start_server", new_callable=AsyncMock)
#     def test_start_server(self, mock_start_server):
#         async def run_test():
#             await self.server.start()
#             mock_start_server.assert_called_once_with(
#                 self.server._handle_client, "localhost", 8080
#             )

#         asyncio.run(run_test())

#     @patch("asyncio.Event.set", new_callable=AsyncMock)
#     def test_stop_server(self, mock_set):
#         async def run_test():
#             await self.server.stop()
#             mock_set.assert_called_once()

#         asyncio.run(run_test())

# # TODO: Fix these tests
#     # @patch("asyncio.run")
#     # def test_run_server(self, mock_asyncio_run):
#     #     self.server.run()
#     #     mock_asyncio_run.assert_called_once_with(self.server.start())

#     # @patch("asyncio.run")
#     # def test_run_server_keyboard_interrupt(self, mock_asyncio_run):
#     #     mock_asyncio_run.side_effect = KeyboardInterrupt
#     #     self.server.run()
#     #     mock_asyncio_run.assert_any_call(self.server.start())
#     #     mock_asyncio_run.assert_any_call(self.server.stop())

#     # @patch("asyncio.run")
#     # def test_run_server_system_exit(self, mock_asyncio_run):
#     #     mock_asyncio_run.side_effect = SystemExit
#     #     self.server.run()
#     #     mock_asyncio_run.assert_any_call(self.server.start())
#     #     mock_asyncio_run.assert_any_call(self.server.stop())

#     @patch("asyncio.StreamReader")
#     @patch("asyncio.StreamWriter")
#     def test_handle_client(self, mock_writer, mock_reader):
#         async def run_test():
#             mock_reader.readline = AsyncMock(
#                 side_effect=[b"GET / HTTP/1.1\r\n", b"\r\n"]
#             )
#             mock_writer.get_extra_info = MagicMock(
#                 return_value={"Connection": "keep-alive"}
#             )
#             mock_writer.close = AsyncMock()
#             mock_writer.wait_closed = AsyncMock()

#             await self.server._handle_client(mock_reader, mock_writer)

#             mock_writer.close.assert_called_once()
#             mock_writer.wait_closed.assert_called_once()

#         asyncio.run(run_test())

#     @patch("asyncio.StreamReader")
#     @patch("asyncio.StreamWriter")
#     def test_process_request(self, mock_writer, mock_reader):
#         async def run_test():
#             mock_reader.readline = AsyncMock(
#                 side_effect=[b"GET / HTTP/1.1\r\n", b"Host: localhost\r\n", b"\r\n"]
#             )
#             mock_writer.drain = AsyncMock()  # Mock `drain`
#             mock_writer.close = AsyncMock()
#             mock_writer.wait_closed = AsyncMock()

#             self.request_factory.create = MagicMock(
#                 return_value=HttpRequest("GET", "/", {})
#             )
#             self.router.get_handler = MagicMock(
#                 return_value=(lambda: HttpResponse(body="OK"), {})
#             )

#             await self.server._process_request(mock_reader, mock_writer)

#             mock_writer.drain.assert_called_once()
#             mock_writer.close.assert_not_called()
#             mock_writer.wait_closed.assert_not_called()

#         asyncio.run(run_test())

#     @patch("asyncio.StreamWriter")
#     def test_send_response(self, mock_writer):
#         async def run_test():
#             mock_writer.drain = AsyncMock()  # Use AsyncMock for `drain`
#             response = HttpResponse(body="OK")
#             await self.server._send_response(mock_writer, response)
#             mock_writer.write.assert_called()
#             mock_writer.drain.assert_called()

#         asyncio.run(run_test())

#     def test_invalid_port(self):
#         with self.assertRaises(ValueError):
#             HttpServer(self.router, self.request_factory, port="not_an_int")

#     def test_invalid_host(self):
#         with self.assertRaises(ValueError):
#             HttpServer(self.router, self.request_factory, host=123)

#     def test_invalid_max_conns(self):
#         with self.assertRaises(ValueError):
#             HttpServer(self.router, self.request_factory, max_conns=-1)

#     def test_invalid_buffer_size(self):
#         with self.assertRaises(ValueError):
#             HttpServer(self.router, self.request_factory, buffer_size=-1)

#     def test_invalid_keep_alive_timeout(self):
#         with self.assertRaises(ValueError):
#             HttpServer(self.router, self.request_factory, keep_alive_timeout=-1)

#     # Additional edge case: malformed header
#     @patch("asyncio.StreamReader")
#     @patch("asyncio.StreamWriter")
#     def test_malformed_header(self, mock_writer, mock_reader):
#         async def run_test():
#             mock_reader.readline = AsyncMock(
#                 side_effect=[
#                     b"GET / HTTP/1.1\r\n",
#                     b"Malformed-Header\r\n",  # Malformed header (no ": ")
#                     b"\r\n",
#                 ]
#             )
#             mock_writer.drain = AsyncMock()  # Mock `drain`
#             mock_writer.close = AsyncMock()
#             mock_writer.wait_closed = AsyncMock()
#             self.server.logger.warning = MagicMock()

#             await self.server._process_request(mock_reader, mock_writer)

#             self.server.logger.warning.assert_called_once_with(
#                 "Malformed header: Malformed-Header"
#             )
#             mock_writer.drain.assert_called_once()  # Ensure `drain` is awaited
#             mock_writer.close.assert_not_called()
#             mock_writer.wait_closed.assert_not_called()

#         asyncio.run(run_test())

#     # Test for handling of 404 not found
#     @patch("asyncio.StreamReader")
#     @patch("asyncio.StreamWriter")
#     def test_404_not_found(self, mock_writer, mock_reader):
#         async def run_test():
#             mock_reader.readline = AsyncMock(
#                 side_effect=[
#                     b"GET /nonexistent HTTP/1.1\r\n",
#                     b"Host: localhost\r\n",
#                     b"\r\n",
#                 ]
#             )
#             mock_writer.drain = AsyncMock()  # Mock `drain`
#             mock_writer.close = AsyncMock()
#             mock_writer.wait_closed = AsyncMock()

#             # Simulate no handler found for the route
#             self.router.get_handler = MagicMock(return_value=(None, {}))

#             await self.server._process_request(mock_reader, mock_writer)

#             # Ensure 404 response is created and sent
#             self.assertTrue(mock_writer.write.called)
#             args = mock_writer.write.call_args[0]
#             self.assertIn(b"404 Not Found", args[0])

#             mock_writer.drain.assert_called_once()
#             mock_writer.close.assert_not_called()
#             mock_writer.wait_closed.assert_not_called()

#         asyncio.run(run_test())

#     # Test for handling 500 internal server error
#     @patch("asyncio.StreamReader")
#     @patch("asyncio.StreamWriter")
#     def test_500_internal_server_error(self, mock_writer, mock_reader):
#         async def run_test():
#             # Mock the reader's `readline` to simulate a request
#             mock_reader.readline = AsyncMock(
#                 side_effect=[
#                     b"GET /error HTTP/1.1\r\n",
#                     b"Host: localhost\r\n",
#                     b"\r\n",
#                 ]
#             )
#             mock_writer.drain = AsyncMock()

#             # Simulate a handler that raises an exception
#             def faulty_handler(request, *args):
#                 raise ValueError("Test exception")

#             self.router.get_handler = MagicMock(return_value=(faulty_handler, {}))

#             await self.server._process_request(mock_reader, mock_writer)

#             # Ensure the response is created and sent
#             self.assertTrue(mock_writer.write.called)
#             args = mock_writer.write.call_args[0]
#             self.assertIn(b"500 Internal Server Error", args[0])

#             # Ensure all response data is sent, no other writer methods are called
#             mock_writer.drain.assert_called_once()
#             mock_writer.close.assert_not_called()
#             mock_writer.wait_closed.assert_not_called()

#         asyncio.run(run_test())


# if __name__ == "__main__":
#     unittest.main()
