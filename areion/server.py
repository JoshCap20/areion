import os
import sys
import signal
from http.server import HTTPServer


"""
Core web server.

Runs an HTTP server with the provided components.

Validation was added for easier development. Invalid components will be caught on startup.
Really wish Java interfaces existed, but this is temporary workaround.

Should we move to a runtime check with a bunch of assertions? Could be better in long term for debugging.
"""


class AreionServer:
    def __init__(self):
        self.orchestrator = None
        self.router = None
        self.static_dir = None
        self.logger = None
        self.engine = None
        self.port = 8080

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

    def with_port(self, port):
        if not isinstance(port, int):
            raise ValueError("Port must be an integer.")
        self.port = port
        return self

    def start(self):
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
            self._run_server()

    def _run_server(self):
        self.logger.info(f"Starting server on port {self.port}")
        server = HTTPServer(("localhost", self.port), self.router.get_handler(self))
        server.serve_forever()

    def _initialize_logger(self):
        if not self.logger:
            from .default import Logger as DefaultLogger

            self.logger = DefaultLogger()
            self.logger.info("Logger missing, defaulting to console logging.")

    def _validate_component(self, component, required_methods, component_name):
        if not all(hasattr(component, method) for method in required_methods):
            raise ValueError(
                f"{component_name} must implement {', '.join(required_methods)}"
            )


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
