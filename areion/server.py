import os
import sys
import signal
import threading
from http.server import HTTPServer


# Constants
DEFAULT_PORT = 8080
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
        self.port: int = DEFAULT_PORT
        self.server: HTTPServer | None = None
        self._server_thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def with_orchestrator(self, orchestrator):
        self._validate_component(
            orchestrator, ["submit_task", "run_tasks", "shutdown"], "Orchestrator"
        )
        self.orchestrator = orchestrator
        return self

    def with_router(self, router):
        self._validate_component(router, ["add_route", "get_handler"], "Router")
        self.router = router
        return self

    def with_static_dir(self, static_dir):
        if not isinstance(static_dir, str):
            raise ValueError("Static directory must be a string.")
        self.static_dir = static_dir
        return self

    def with_logger(self, logger):
        self._validate_component(logger, ["info", "error"], "Logger")
        self.logger = logger
        return self

    def with_engine(self, engine):
        self._validate_component(engine, ["render"], "Template engine")
        self.engine = engine
        return self

    def with_port(self, port: int) -> 'AreionServer':
        if not isinstance(port, int):
            raise ValueError("Port must be an integer.")
        self.port = port
        return self

    def start(self, in_thread: bool = False) -> None:
        print(AREION_LOGO)

        def signal_handler(sig, frame):
            print("Received shutdown signal. Shutting down server...")
            if self.orchestrator:
                self.orchestrator.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        self._initialize_logger()

        if not self.router:
            self.logger.error("Router missing.")
            return

        self.logger.info(f"Starting server on port {self.port}")

        if self.static_dir and not os.path.isdir(self.static_dir):
            self.logger.error(f"Static directory {self.static_dir} does not exist.")
            return

        if self.orchestrator:
            self.orchestrator.submit_task(self._run_server)
            self.orchestrator.run_tasks()
        else:
            if in_thread:
                self._start_in_thread()
            else:
                self._run_server()

    def _run_server(self) -> None:
        with self._lock:
            self.logger.info(f"Starting server on port {self.port}")
            try:
                self.server = HTTPServer(("localhost", self.port), self.router.get_handler(self))
                self.server.serve_forever()
            except Exception as e:
                self.logger.error(f"Failed to start server: {e}")
                raise

    def _start_in_thread(self) -> None:
        with self._lock:
            self._server_thread = threading.Thread(target=self._run_server)
            self._server_thread.daemon = True
            self._server_thread.start()
            self.logger.info(f"Server running in thread on port {self.port}")
        
    def stop(self):
        if self.server:
            self.logger.info("Shutting down server...")
            self.server.shutdown()  # Gracefully shutdown server
        if self._server_thread:
            self._server_thread.join()
            self.logger.info("Server thread has terminated.")

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


