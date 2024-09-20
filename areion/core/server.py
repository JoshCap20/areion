import asyncio
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
        keep_alive_timeout: int = 5
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
        self.semaphore = asyncio.Semaphore(max_conns)
        self.router = router
        self.request_factory = request_factory
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.keep_alive_timeout = keep_alive_timeout
        self._shutdown_event = asyncio.Event()

    async def _handle_client(self, reader, writer, timeout: int = 60) -> None:
        async with self.semaphore:
            try:
                while True:
                    try:
                        await asyncio.wait_for(self._process_request(reader, writer), timeout=timeout)
                    except asyncio.TimeoutError:
                        break  # Timeout, close connection

                    # Get transport headers (if available)
                    headers_info = writer.get_extra_info('headers')
                    
                    # Check if connection should be kept alive
                    if headers_info and "Connection" in headers_info and headers_info['Connection'].lower() == "keep-alive":
                        await asyncio.sleep(self.keep_alive_timeout)
                    else:
                        break
            finally:
                writer.close()
                await writer.wait_closed()

    async def _process_request(self, reader, writer):
        try:
            # Read the request line
            request_line = await reader.readline()
            if not request_line:
                return

            request_line = request_line.decode("utf-8").strip()
            method, path, _ = request_line.split(" ")

            # Parse headers
            headers = {}
            while True:
                line = await reader.readline()
                if line == b"\r\n":  # End of headers
                    break
                line = line.decode("utf-8").strip()
                if ": " in line:
                    header_name, header_value = line.split(": ", 1)
                    headers[header_name] = header_value
                else:
                    # Handle the case where the header is malformed
                    self.logger.warning(f"Malformed header: {line}")

            # Create the request object
            request = self.request_factory.create(method, path, headers)

            try:
                handler, path_params = self.router.get_handler(method, path)
                if handler:
                    response = handler(request, **path_params)
                else:
                    response = HttpResponse(status_code=404, body="404 Not Found")
            except Exception as e:
                # Log the error and send a 500 response
                self.logger.error(f"Error handling request: {e}")
                response = HttpResponse(status_code=500, body="Internal Server Error")

            # Ensure the response is an instance of HttpResponse
            if not isinstance(response, HttpResponse):
                response = HttpResponse(body=response)

            # Send the formatted response
            await self._send_response(writer, response)
        finally:
            writer.close()
            await writer.wait_closed()
            
    async def _send_response(self, writer, response):
        buffer = response.format_response()

        # Chunked response for large bodies
        chunk_size = self.buffer_size
        for i in range(0, len(buffer), chunk_size):
            writer.write(buffer[i:i+chunk_size])
            await writer.drain()

    async def start(self):
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def stop(self):
        self._shutdown_event.set()

    def run(self):
        try:
            asyncio.run(self.start())
        except (KeyboardInterrupt, SystemExit):
            asyncio.run(self.stop())
