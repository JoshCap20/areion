import os
import asyncio
import threading
from .core import HttpServer, HttpRequestFactory

# Constants
DEFAULT_PORT = 8080
DEFAULT_HOST = "localhost"
AREION_LOGO = """
           >>\\.
          /_  )`.
         /  _)`^)`.   _.---. _ 
        (_,' \\  `^-)""      `.\\
              |           | \\ \\--._
             /   /  /     | | |
            /   /  /      | | |
        ___/___/__/_______|_|__\\______
       /                              \\
      /         A R E I O N            \\
     /__________________________________\\
      | | |                        | | |
      | | |                        | | |
      |_|_|________________________|_|_|
      \\_\\_\\                        /_/_/
"""


class AreionServer:
    def __init__(self):
        self.orchestrator: any | None = None
        self.router: any | None = None
        self.static_dir: str | None = None
        self.logger: any | None = None
        self.engine: any | None = None
        self.host: str = DEFAULT_HOST
        self.port: int = DEFAULT_PORT
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._shutdown_event: asyncio.Event = asyncio.Event()
        self.http_server: HttpServer | None = None

    def with_orchestrator(self, orchestrator) -> "AreionServer":
        self._validate_component(
            orchestrator,
            ["start", "submit_task", "run_tasks", "shutdown"],
            "Orchestrator",
        )
        self.orchestrator = orchestrator
        return self

    def with_router(self, router) -> "AreionServer":
        self._validate_component(router, ["add_route", "get_handler"], "Router")
        self.router = router
        return self

    def with_static_dir(self, static_dir) -> "AreionServer":
        if not isinstance(static_dir, str):
            raise ValueError("Static directory must be a string.")
        if not os.path.isdir(static_dir):
            raise ValueError(f"Static directory {static_dir} does not exist.")
        self.static_dir = static_dir
        return self

    def with_logger(self, logger) -> "AreionServer":
        self._validate_component(logger, ["info", "error", "debug"], "Logger")
        self.logger = logger
        return self

    def with_engine(self, engine):
        self._validate_component(engine, ["render"], "Template engine")
        self.engine = engine
        return self

    def with_port(self, port: int) -> "AreionServer":
        if not isinstance(port, int):
            raise ValueError("Port must be an integer.")
        self.port = port
        # TODO: add more validation
        return self

    def with_host(self, host: str) -> "AreionServer":
        if not isinstance(host, str):
            raise ValueError("Host must be a string.")
        # TODO: add more validation
        self.host = host
        return self

    def run(self) -> None:
        """
        Start the server synchronously. This is a simplified entry point for users
        to start the server without dealing with asyncio directly.
        """
        try:
            asyncio.run(self.start())
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    async def start(self) -> None:
        """
        Start the Areion server asynchronously
        """
        print(AREION_LOGO)
        self._initialize_logger()

        if not self.router:
            self.logger.error("Router missing.")
            return

        self.logger.info(f"Starting server on port {self.port}")

        # Start orchestrator tasks in a separate thread
        if self.orchestrator:
            orchestrator_thread = threading.Thread(
                target=self._start_orchestrator, daemon=True
            )
            orchestrator_thread.start()

        self.initialize_request_factory()
        
        # Add the HTTP Server
        # TODO: Could pass logger here
        self.http_server = HttpServer(
            router=self.router, host=self.host, port=self.port, request_factory=self.request_factory
        )
        
        # TODO: Attach static file handler here
        if self.static_dir:
            self._serve_static_files()

        # Start the HTTP server
        server_task = asyncio.create_task(self.http_server.start())

        self.logger.info(f"Server running on http://{self.host}:{self.port}")
        self.logger.debug("Press Ctrl+C to stop the server.")
        self.logger.info(f"Available Routes and Handlers: {self.router.routes}")

        # Wait for shutdown signal
        await self._shutdown_event.wait()

        self.logger.info("Shutting down server...")
        await self.shutdown(server_task)
        self.logger.info("Server shutdown complete.")

    async def shutdown(self, server_task):
        """
        Gracefully shutdown the server.
        """
        # Trigger the HTTP server to stop
        if self.http_server:
            await self.http_server.stop()

        # Wait for the HTTP server to finish
        await server_task

        # Shutdown orchestrator
        if self.orchestrator:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.orchestrator.shutdown
                )
                self.logger.info("Orchestrator shutdown complete.")
            except Exception as e:
                self.logger.error(f"Error during orchestrator shutdown: {e}")

    def stop(self):
        """
        Initiate server shutdown.
        """
        self.logger.info("Shutdown initiated.")
        self.loop.call_soon_threadsafe(self._shutdown_event.set)

    def _start_orchestrator(self):
        if self.orchestrator:
            self.logger.info("Starting orchestrator...")
            try:
                self.orchestrator.start()
            except Exception as e:
                self.logger.error(f"Orchestrator error: {e}")

    def _initialize_logger(self) -> None:
        if not self.logger:
            from .default import Logger as DefaultLogger

            self.logger = DefaultLogger()
            self.logger.info("Logger missing, defaulting to console logging.")

    def _validate_component(self, component, required_methods, component_name):
        if not all(hasattr(component, method) for method in required_methods):
            raise ValueError(
                f"{component_name} must implement {', '.join(required_methods)}"
            )
            
    def initialize_request_factory(self):
        """
        Initialize the HttpRequestFactory with the orchestrator, logger, and engine.
        """
        self.request_factory = HttpRequestFactory(
            logger=self.logger, engine=self.engine, orchestrator=self.orchestrator
        )


    def _serve_static_files(self):
        # TODO: Implement serving static files
        raise NotImplementedError("Serving static files is not yet implemented.")
    
