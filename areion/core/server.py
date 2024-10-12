import asyncio
import httptools

from .exceptions import HttpError, MethodNotAllowedError
from .response import HttpResponse, HTTP_STATUS_CODES
from .request import HttpRequest


class HttpServer:
    def __init__(
        self,
        router,
        request_factory,
        logger=None,
        host: str = "localhost",
        port: int = 8080,
        max_conns: int = 1000,
        buffer_size: int = 8192,
        keep_alive_timeout: int = 30,
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

        self.router = router
        self.max_conns = max_conns
        self.request_factory = request_factory
        self.host: str = host
        self.port: int = port
        self.buffer_size: int = buffer_size
        self.max_conns: int = max_conns
        self.keep_alive_timeout: int = keep_alive_timeout
        self._shutdown_event = asyncio.Event()
        self.logger = logger
        self.parser = httptools.HttpRequestParser(self)
        # self.semaphore = asyncio.Semaphore(max_conns) # TODO: Figure out performance tradeoffs of using semaphore

    async def _handle_client(self, reader, writer):
        try:
            await self._process_request(reader, writer)
        except Exception as e:
            self.log("error", f"{e}")
        finally:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()

    async def _process_request(self, reader, writer):
        try:
            await self._handle_request_logic(reader, writer)
        except asyncio.CancelledError:
            self.log("debug", "Client connection cancelled.")
        except ConnectionResetError:
            self.log("debug", "Connection reset by peer.")
            
    """
    For `httptools` integration, this class needs the following callback methods (all optional):
          - on_message_begin()
          - on_url(url: bytes)
          - on_header(name: bytes, value: bytes)
          - on_headers_complete()
          - on_body(body: bytes)
          - on_message_complete()
          - on_chunk_header()
          - on_chunk_complete()
          - on_status(status: bytes)
    """

    async def _handle_request_logic(self, reader, writer):
        keep_alive: bool = True
        # HttpErrors are NOT handled correctly outside of this method
        while keep_alive:
            # Handle request reading
            try:
                headers_data = await asyncio.wait_for(
                    reader.readuntil(b"\r\n\r\n"), timeout=self.keep_alive_timeout
                )
            except asyncio.TimeoutError:
                response = HttpResponse(
                    status_code=408,
                    body=HTTP_STATUS_CODES[408],
                    content_type="text/plain",
                    headers={"Connection": "close"},
                )
                await self._send_response(writer, response)
                break
            except asyncio.IncompleteReadError:
                response = HttpResponse(
                    status_code=400,
                    body=HTTP_STATUS_CODES[400],
                    content_type="text/plain",
                    headers={"Connection": "close"},
                )
                await self._send_response(writer, response)
                break
            except asyncio.LimitOverrunError:
                response = HttpResponse(
                    status_code=413,
                    body=HTTP_STATUS_CODES[413],
                    content_type="text/plain",
                    headers={"Connection": "close"},
                )
                await self._send_response(writer, response)
                break

            if not headers_data:
                break

            try:
                # TODO: Handle http_versions and keep alive better
                request_line, headers = self._parse_headers(headers_data)
                method, path, http_version = request_line
            except Exception as e:
                response = HttpResponse(
                    status_code=400,
                    body=HTTP_STATUS_CODES[400],
                    content_type="text/plain",
                    headers={"Connection": "close"},
                )
                await self._send_response(writer, response)
                self.log("error", f"Error parsing headers: {e}")
                break

            # TODO: Break this into specific HTTP version handling
            # TODO: Ensure proper host header

            # TODO: Handle Transfer-Encoding
            transfer_encoding = headers.get("Transfer-Encoding", "").lower()
            if "chunked" in transfer_encoding:
                response = HttpResponse(
                    status_code=501,
                    body="Not Implemented",
                    content_type="text/plain",
                    headers={"Connection": "close"},
                )
                await self._send_response(writer, response)
                break

            content_length = int(headers.get("Content-Length", 0))
            body = b""
            if content_length > 0:
                try:
                    body = await asyncio.wait_for(
                        reader.readexactly(content_length),
                        timeout=self.keep_alive_timeout,
                    )
                except asyncio.TimeoutError:
                    response = HttpResponse(
                        status_code=408,
                        body=HTTP_STATUS_CODES[408],
                        content_type="text/plain",
                        headers={"Connection": "close"},
                    )
                    await self._send_response(writer, response)
                    break
                except Exception as e:
                    response = HttpResponse(
                        status_code=400,
                        body=HTTP_STATUS_CODES[400],
                        content_type="text/plain",
                        headers={"Connection": "close"},
                    )
                    await self._send_response(writer, response)
                    self.log("error", f"Error reading body: {e}")
                    break

            try:
                request: HttpRequest = self.request_factory.create(
                    method=method, path=path, headers=headers, body=body
                )
                # self.log("info", f"[REQUEST] {request}")
                try:
                    handler, path_params, is_async = self.router.get_handler(
                        method, path
                    )
                except MethodNotAllowedError:
                    if hasattr(self.router, "get_allowed_methods"):
                        allowed_methods = self.router.get_allowed_methods(path)
                    else:
                        allowed_methods = []
                    response = HttpResponse(
                        status_code=405,
                        body=HTTP_STATUS_CODES[405],
                        content_type="text/plain",
                        headers={"Allow": ", ".join(allowed_methods)},
                    )
                    await self._send_response(writer, response)
                    break

                # Handle OPTIONS and HEAD requests
                if method == "OPTIONS":
                    response = HttpResponse(status_code=204, body="")
                    response.set_header(
                        "Allow", ", ".join(self.router.get_allowed_methods(path))
                    )
                elif method == "HEAD":
                    response = await handler(request, **path_params)
                    if not isinstance(response, HttpResponse):
                        response = HttpResponse(body=response)
                    response.body = b""
                elif request.method == "CONNECT":
                    response = HttpResponse(
                        status_code=501,
                        body=HTTP_STATUS_CODES[501],
                        content_type="text/plain",
                    )
                else:
                    if is_async:
                        response = await handler(request, **path_params)
                    else:
                        response = handler(request, **path_params)

            except HttpError as e:
                # Handles web exceptions raised by route handler
                response = HttpResponse(
                    status_code=e.status_code, body=e.message, content_type="text/plain"
                )
                self.log("warning", f"[RESPONSE] {e}")
                
            except Exception as e:
                # Handles all other exceptions
                # TODO: Return exception details only in debug mode
                response = HttpResponse(
                    status_code=500,
                    body=HTTP_STATUS_CODES[500],
                    content_type="text/plain",
                )

                self.log("error", f"[RESPONSE] {e}")
                
            if not isinstance(response, HttpResponse):
                response = HttpResponse(body=response)

            # Handle keep-alive connections
            # TODO
            connection_header = request.headers.get("Connection", "").lower()
            if connection_header == "close" or (
                http_version == "HTTP/1.0" and connection_header != "keep-alive"
            ):
                response.headers["Connection"] = "close"
                keep_alive = False
            else:
                response.headers["Connection"] = "keep-alive"

            await self._send_response(writer=writer, response=response)

    def _parse_headers(self, headers_data):
        try:
            headers_text = headers_data.decode("iso-8859-1")
            header_lines = headers_text.split("\r\n")
            request_line = header_lines[0]
            method, path, http_version = request_line.strip().split(" ", 2)
            headers = {}
            for line in header_lines[1:]:
                if line == "":
                    continue
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
            return (method, path, http_version), headers
        except Exception as e:
            raise ValueError(f"Invalid headers: {e}")

    async def _send_response(self, writer, response):
        # Recommended to use HttpResponse class for responses
        if not isinstance(response, HttpResponse):
            response = HttpResponse(body=response)

        # TODO: Add interceptor component here

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
        if self._server:
            self._server.close()
            await self._server.wait_closed()

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
