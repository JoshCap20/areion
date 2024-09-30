import asyncio
import httptools

from .exceptions import HttpError, MethodNotAllowedError
from .response import HttpResponse, HTTP_STATUS_CODES
from .request import HttpRequest
from .request_builder import RequestBuilder


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
        self.request_factory = request_factory
        self.host: str = host
        self.port: int = port
        self.buffer_size: int = buffer_size
        self.max_conns: int = max_conns
        self.keep_alive_timeout: int = keep_alive_timeout
        self._shutdown_event = asyncio.Event()
        self.logger = logger
        self.request_builder = RequestBuilder(self.request_factory)
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

    async def _process_request(self, reader, writer):
        keep_alive: bool = True
        # HttpErrors are NOT handled correctly outside of this method
        while keep_alive:
            # Handle request reading
            try:
                data = await asyncio.wait_for(
                    reader.read(self.buffer_size), timeout=self.keep_alive_timeout
                )
                if not data:
                    break
                
                print(data)
                
                self.request_builder.feed_data(data)
                
                if self.request_builder.parser.is_message_complete():
                    request = self.request_builder.get_request()
                    print(request)
                    response = await self._handle_http_request(request)
                    
                    connection_header = request.headers.get("connection", "").lower()
                    if connection_header == "close" or (
                        request.http_version == "HTTP/1.0" and connection_header != "keep-alive"
                    ):
                        keep_alive = False
                        response.headers["Connection"] = "close"
                    else:
                        response.headers["Connection"] = "keep-alive"
                    await self._send_response(writer, response)

                    self.request_builder.reset()
                    
            except asyncio.TimeoutError:
                response = HttpResponse(
                    status_code=408,
                    body=HTTP_STATUS_CODES[408],
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

    async def _handle_http_request(self, request: HttpRequest) -> HttpResponse:
        try:
            handler, path_params, is_async = self.router.get_handler(request.method, request.path)
        except MethodNotAllowedError:
            allowed_methods = self.router.get_allowed_methods(request.path)
            return HttpResponse(
                status_code=405,
                body=HTTP_STATUS_CODES[405],
                content_type="text/plain",
                headers={"Allow": ", ".join(allowed_methods)},
            )
        except Exception as e:
            self.log("error", f"Routing error: {e}")
            return HttpResponse(
                status_code=500,
                body=HTTP_STATUS_CODES[500],
                content_type="text/plain",
            )

        # Handle OPTIONS and HEAD requests
        if request.method == "OPTIONS":
            return HttpResponse(
                status_code=204,
                body="",
                content_type="text/plain",
                headers={"Allow": ", ".join(self.router.get_allowed_methods(request.path))},
            )
        elif request.method == "HEAD":
            response = await self._execute_handler(handler, request, path_params, is_async)
            response.body = b""  # Empty body for HEAD requests
            return response
        elif request.method == "CONNECT":
            return HttpResponse(
                status_code=501,
                body=HTTP_STATUS_CODES[501],
                content_type="text/plain",
            )
        else:
            return await self._execute_handler(handler, request, path_params, is_async)

    async def _execute_handler(self, handler, request, path_params, is_async):
        try:
            if is_async:
                response = await handler(request, **path_params)
            else:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(None, handler, request, **path_params)
            if not isinstance(response, HttpResponse):
                response = HttpResponse(body=response)
            return response
        except HttpError as e:
            return HttpResponse(
                status_code=e.status_code,
                body=e.message,
                content_type="text/plain",
            )
        except Exception as e:
            return HttpResponse(
                status_code=500,
                body=HTTP_STATUS_CODES[500],
                content_type="text/plain",
            )

    async def _send_response(self, writer, response):
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
        self._shutdown_event.set()

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
