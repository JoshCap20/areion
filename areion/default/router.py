import json
from http.server import BaseHTTPRequestHandler


class Router:
    def __init__(self):
        self.routes = {}
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.middlewares = {}
        self.global_middlewares = []

    def add_route(self, path, handler, methods=["GET"], middlewares=None):
        """
        Adds a route to the router and optionally attaches middlewares.

        Args:
            path (str): The URL path for the route.
            handler (callable): The function to handle requests to the route.
            methods (list, optional): A list of HTTP methods that the route should respond to. Defaults to ["GET"].
            middlewares (list, optional): A list of middleware functions for this route.
        """
        methods = [
            method.upper()
            for method in methods
            if method.upper() in self.allowed_methods
        ]
        normalized_path = path.rstrip("/") if path != "/" else path

        if not methods:
            raise ValueError(
                "At least one valid HTTP method must be provided per route."
            )

        if normalized_path not in self.routes:
            self.routes[normalized_path] = {}

        for method in methods:
            self.routes[normalized_path][method] = handler
            if middlewares:
                self.middlewares[(method, normalized_path)] = middlewares

    def group(self, base_path, middlewares=None):
        """
        Creates a sub-router (group) with a base path and optional group-specific middlewares.
        Args:
            base_path (str): The base path for the sub-router.
            middlewares (list, optional): List of middleware functions applied to all routes within this group.
        Returns:
            Router: A sub-router instance with the specified base path.
        """
        sub_router = Router()
        group_middlewares = middlewares or []

        def add_sub_route(sub_path, handler, methods=["GET"], middlewares=None):
            full_path = f"{base_path.rstrip('/')}/{sub_path.lstrip('/')}"
            combined_middlewares = (middlewares or []) + (group_middlewares or [])
            self.add_route(
                full_path, handler, methods, middlewares=combined_middlewares
            )

        sub_router.add_route = add_sub_route
        return sub_router

    def route(self, path, methods=["GET"], middlewares=[]):
        """
        A decorator to define a route with optional middlewares.

        Args:
            path (str): The URL path for the route.
            methods (list, optional): HTTP methods allowed for the route. Defaults to ["GET"].
            middlewares (list, optional): List of middleware functions for the route.

        Returns:
            function: The decorated function with the route added.

        Example:
            @app.route("/hello", methods=["GET", "POST"], middlewares=[auth_middleware])
            def hello(request):
                return "Hello, world!"
        """

        def decorator(func):
            self.add_route(path, func, methods=methods, middlewares=middlewares)
            return func

        return decorator

    def get_handler(self, method, path):
        """
        Retrieves the appropriate route handler based on method and path, and applies middleware.

        Args:
            method (str): HTTP method.
            path (str): Request path.

        Returns:
            tuple: (handler, path_params) if a route is matched; otherwise (None, None).
        """
        normalized_path = path.rstrip("/") if path != "/" else path
        if normalized_path in self.routes and method in self.routes[normalized_path]:
            handler = self.routes[normalized_path][method]
            handler_with_middlewares = self._apply_middlewares(
                handler, method, normalized_path
            )
            path_params = {}  # TODO
            return handler_with_middlewares, path_params
        return None, None

    ### Middleware Handling ###

    def add_global_middleware(self, middleware) -> None:
        """Adds a middleware that will be applied globally to all routes."""
        self.global_middlewares.append(middleware)

    def _apply_middlewares(self, handler, method, path) -> callable:
        """
        Applies the middleware chain to the handler for the given method and path.
        Global middlewares are applied first, followed by route-specific middlewares.
        Args:
            handler (callable): The route handler function.
            method (str): HTTP method.
            path (str): Request path.
        Returns:
            callable: The final handler with middleware applied.
        """
        middlewares = self.global_middlewares[:]

        route_middlewares = self.middlewares.get((method, path), [])
        middlewares.extend(route_middlewares)

        # Wrap the handler with all middlewares in reverse order
        for middleware in reversed(middlewares):
            handler = middleware(handler)
        return handler
