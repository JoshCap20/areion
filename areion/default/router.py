import json
from http.server import BaseHTTPRequestHandler


class Router:
    def __init__(self):
        self.routes = {}
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    def add_route(self, path, handler, methods=["GET"]):
        """
        Adds a route to the router.

        Args:
            path (str): The URL path for the route.
            handler (callable): The function to handle requests to the route.
            methods (list, optional): A list of HTTP methods that the route should respond to. Defaults to ["GET"].
            
        Example:
            def my_handler(request):
                return "Hello, world!"

            router.add_route("/hello", my_handler, methods=["GET", "POST"])
        """
        methods = [method.upper() for method in methods if method.upper() in self.allowed_methods]
        normalized_path = path.rstrip("/") if path != "/" else path
        if methods == []:
            raise ValueError("At least one valid HTTP method must be provided per route. Route: " + path)
        if normalized_path not in self.routes:
            self.routes[normalized_path] = {} 
        for method in methods:
            self.routes[normalized_path][method] = handler

    def group(self, base_path):
        """
        Creates a sub-router with a base path.

        Args:
            base_path (str): The base path for the sub-router.

        Returns:
            Router: A sub-router instance with the specified base path.

        The sub-router allows adding routes relative to the base path. The `add_route`
        method of the sub-router is overridden to prepend the base path to the sub-path
        before adding the route to the main router.
        """
        sub_router = Router()

        def add_sub_route(sub_path, handler, methods=["GET"]):
            full_path = f"{base_path.rstrip('/')}/{sub_path.lstrip('/')}"
            self.add_route(full_path, handler, methods)

        sub_router.add_route = add_sub_route
        return sub_router

    def route(self, path, methods=["GET"]):
        """
        A decorator to define a route for the web application.

        Args:
            path (str): The URL path for the route.
            methods (list, optional): The HTTP methods allowed for the route. Defaults to ["GET"].

        Returns:
            function: The decorated function with the route added.
        """
        def decorator(func):
            self.add_route(path, func, methods)
            return func
        return decorator

    def get_handler(self, server):
        """
        Returns a request handler class for the given server.

        The returned RequestHandler class inherits from BaseHTTPRequestHandler and 
        handles HTTP GET, POST, PUT, and DELETE requests. It routes the requests 
        to the appropriate handler based on the server's routing table.

        Methods:
            do_GET(self):
                Handles HTTP GET requests.
            
            do_POST(self):
                Handles HTTP POST requests.
            
            do_PUT(self):
                Handles HTTP PUT requests.
            
            do_DELETE(self):
                Handles HTTP DELETE requests.
            
            _handle_request(self, method):
                Routes the request to the appropriate handler based on the method 
                and the request path. Sends a 404 error if the route is not found.
            
            _send_response(self, response):
                Sends the response to the client. Supports JSON, HTML, plain text, 
                and binary data responses. Sends a 500 error for unsupported response types.

        Args:
            server: The server instance that contains the routing table.

        Returns:
            RequestHandler: A class that handles HTTP requests for the given server.
        """
        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self._handle_request("GET")

            def do_POST(self):
                self._handle_request("POST")

            def do_PUT(self):
                self._handle_request("PUT")

            def do_DELETE(self):
                self._handle_request("DELETE")

            def _handle_request(self, method):
                route = self.path.rstrip("/") if self.path != "/" else self.path
                if route in server.router.routes and method in server.router.routes[route]:
                    handler = server.router.routes[route][method]
                    response = handler(self)
                    self._send_response(response)
                else:
                    self.send_error(404, "Route Not Found")

            def _send_response(self, response):
                if isinstance(response, dict):  # JSON response
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                elif isinstance(response, str):  # HTML or plain text
                    content_type = "text/html" if "<html" in response else "text/plain"
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.end_headers()
                    self.wfile.write(response.encode("utf-8"))
                elif isinstance(response, bytes):  # Binary data
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.end_headers()
                    self.wfile.write(response)
                else:
                    self.send_error(500, "Unsupported response type")

        return RequestHandler
