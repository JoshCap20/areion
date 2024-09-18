import os
import sys
import signal
from http.server import HTTPServer

from .base import BaseOrchestrator, BaseLogger, BaseRouter, BaseEngine

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
        self.template_engine = None
        self.port = 8080

    def with_orchestrator(self, orchestrator):
        required_methods = ['submit_task', 'run_tasks', 'shutdown']
        if not all(hasattr(orchestrator, method) for method in required_methods):
            raise ValueError("Orchestrator must implement 'submit_task', 'run_tasks', and 'shutdown'.")
        self.orchestrator = orchestrator
        return self

    def with_router(self, router):
        required_methods = ['add_route', 'get_handler']
        if not all(hasattr(router, method) for method in required_methods):
            raise ValueError("Router must implement 'add_route' and 'get_handler'.")
        self.router = router
        return self

    def with_static_dir(self, static_dir):
        if not isinstance(static_dir, str):
            raise ValueError("Static directory must be a string.")
        self.static_dir = static_dir
        return self

    def with_logger(self, logger):
        required_methods = ['info', 'error']
        if not all(hasattr(logger, method) for method in required_methods):
            raise ValueError("Logger must implement 'info' and 'error'.")
        self.logger = logger
        return self

    def with_template_engine(self, template_engine):
        required_methods = ['render']
        if not all(hasattr(template_engine, method) for method in required_methods):
            raise ValueError("Template engine must implement 'render'.")
        self.template_engine = template_engine
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

        if not self.router:
            print("Router missing, cannot start server.", file=sys.stderr)
            return

        if self.logger:
            self.logger.info(f"Starting server on port {self.port}")

        if self.orchestrator:
            print("Starting orchestrator with the server.")
        else:
            print("Orchestrator missing, defaulting to single-threaded server.")

        if self.static_dir and not os.path.isdir(self.static_dir):
            print(
                f"Static directory {self.static_dir} does not exist.", file=sys.stderr
            )
            return
        
        if self.orchestrator:
            self.orchestrator.submit_task(self.run_server)
            self.orchestrator.run_tasks()
        else:
            self.run_server()

    def run_server(self):
        print(f"Starting server on port {self.port}")
        server = HTTPServer(("localhost", self.port), self.router.get_handler(self))
        if not self.orchestrator:
            print("Starting server in single-threaded mode.")
        server.serve_forever()


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
