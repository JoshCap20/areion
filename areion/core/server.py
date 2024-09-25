import asyncio

from .exceptions import HttpError, NotFoundError
from .response import HttpResponse
from .request import HttpRequest


class HttpServer:
    def __init__(
        self,
        router,
        request_factory,
        host: str = "localhost",
        port: int = 8080,
        max_conns: int = 1000,
        buffer_size: int = 8192,
        keep_alive_timeout: int = 15,
    ):
        if not isinstance(port, int):
            raise ValueError("Port must be an integer.")
        if not isinstance(host, str):
            raise ValueError("Host must be a string.")
        if not router:
            raise ValueError("Router must be provided.")
        if not request_factory:
            raise ValueError("Request factory must be provided.")
        if not isinstance(max_conns, int) or max_conns <= 0:
            raise ValueError("Max connections must be a positive integer.")
        if not isinstance(buffer_size, int) or buffer_size <= 0:
            raise ValueError("Buffer size must be a positive integer.")
        if not isinstance(keep_alive_timeout, int) or keep_alive_timeout <= 0:
            raise ValueError("Keep alive timeout must be a positive integer.")
        self.semaphore = asyncio.Semaphore(max_conns)
        self.router = router
        self.request_factory = request_factory
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.keep_alive_timeout = keep_alive_timeout
        self._shutdown_event = asyncio.Event()
        self.logger = None

    async def _handle_client(self, reader, writer):
        try:
            await self._process_request(reader, writer)
        except Exception as e:
            if isinstance(e, ConnectionResetError):
                self.log("debug", f"Connection reset by peer: {e}")
            else:
                self.log("error", f"Error processing request: {e}")
        finally:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()

    async def _process_request(self, reader, writer):
        # Ensures that the request is processed within the timeout
        try:
            await asyncio.wait_for(
                self._handle_request_logic(reader, writer),
                timeout=self.keep_alive_timeout,
            )
        except asyncio.TimeoutError:
            response = HttpResponse(status_code=408, body="Request Timeout")
            await self._send_response(writer, response)

    async def _handle_request_logic(self, reader, writer):
        while True:
            try:
                request_line = await asyncio.wait_for(
                    reader.readline(), timeout=self.keep_alive_timeout
                )
            except asyncio.TimeoutError:
                break  # No new request received within the keep-alive timeout

            if not request_line:
                break  # Client closed the connection

            method, path, _ = request_line.decode("utf-8").strip().split(" ")
            headers = await self._parse_headers(reader)

            request = self.request_factory.create(method, path, headers)

            handler, path_params, is_async = self.router.get_handler(method, path)

            try:
                if not handler:
                    raise NotFoundError()

                if is_async:
                    response = await handler(request, **path_params)
                else:
                    response = handler(request, **path_params)
            except HttpError as e:
                # Handles web exceptions raised by the handler
                response = HttpResponse(status_code=e.status_code, body=e)
            except Exception as e:
                # Handles all other exceptions
                response = HttpResponse(status_code=500, body="Internal Server Error")

            await self._send_response(writer, response)

            if (
                "Connection" in request.headers
                and request.headers["Connection"].lower() == "close"
            ):
                break

    async def _parse_headers(self, reader):
        headers = {}
        while True:
            line = await reader.readline()
            if line == b"\r\n":
                break
            header_name, header_value = line.decode("utf-8").strip().split(": ", 1)
            headers[header_name] = header_value
        return headers

    async def _send_response(self, writer, response):
        if not isinstance(response, HttpResponse):
            response = HttpResponse(body=response)

        buffer = response.format_response()
        writer.write(buffer)
        await writer.drain()

    async def start(self):
        # Handles server startup
        self._server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        async with self._server:
            await self._shutdown_event.wait()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def run(self, *args, **kwargs):
        try:
            await self.start()
        except (KeyboardInterrupt, SystemExit):
            await self.stop()

    def log(self, level: str, message: str) -> None:
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message)
        else:
            print(f"{level.upper()}: {message}")
