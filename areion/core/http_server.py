import asyncio
from .response import HttpResponse
from .request import HttpRequest


class HttpServer:
    def __init__(self, router, host: str = "localhost", port: int = 8080):
        if not isinstance(port, int):
            raise ValueError("Port must be an integer.")
        if not isinstance(host, str):
            raise ValueError("Host must be a string.")
        if not router:
            raise ValueError("Router must be provided.")
        self.router = router
        self.host = host
        self.port = port
        self._shutdown_event = asyncio.Event()

    async def _handle_client(self, reader, writer):
        try:
            request_line = await reader.readline()
            if not request_line:
                return

            # Parse the request line
            request_line = request_line.decode("utf-8").strip()
            method, path, _ = request_line.split(" ")

            # Parse headers
            headers = {}
            while True:
                header_line = await reader.readline()
                if header_line == b"\r\n":
                    break
                header_name, header_value = (
                    header_line.decode("utf-8").strip().split(": ", 1)
                )
                headers[header_name] = header_value

            # Create request object
            request = HttpRequest(method, path, headers)

            # Extract path parameters
            handler, path_params = self.router.get_handler(method, path)

            if handler:
                # Pass the request object and any path parameters to the handler
                if path_params:
                    response = handler(request, **path_params)
                else:
                    response = handler(request)

                # Send response
                response_data = HttpResponse(
                    status_code=200, content_type="text/html", body=response
                )
            else:
                # 404 not found
                response_data = HttpResponse(
                    status_code=404, content_type="text/html", body="404 Not Found"
                )

            # Send formatted response
            writer.write(response_data.format_response())
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    async def stop(self):
        self._shutdown_event.set()

    def run(self):
        try:
            asyncio.run(self.start())
        except (KeyboardInterrupt, SystemExit):
            print("Server shutting down...")
