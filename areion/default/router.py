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

        if not methods:
            raise ValueError(
                "At least one valid HTTP method must be provided per route. Route: "
                + path
            )

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

    def get_handler(self, method, path):
        """
        Get the appropriate route handler based on the HTTP method and path.

        Args:
            method (str): The HTTP method of the request (e.g., "GET", "POST").
            path (str): The request path (e.g., "/hello").

        Returns:
            tuple: (handler, path_params) if a route is matched; otherwise (None, None).
        """
        normalized_path = path.rstrip("/") if path != "/" else path

        if normalized_path in self.routes and method in self.routes[normalized_path]:
            handler = self.routes[normalized_path][method]
            # TODO: Extract parameters
            path_params = {}
            return handler, path_params
        return None, None