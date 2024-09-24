from asyncio import iscoroutinefunction


class Router:
    def __init__(self):
        self.root = TrieNode()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.middlewares = {}
        self.global_middlewares = []

    def add_route(self, path, handler, methods=["GET"], middlewares=None):
        """
        Adds a route to the Trie, supporting dynamic path segments (e.g., /users/:id).
        """
        methods = [
            method.upper()
            for method in methods
            if method.upper() in self.allowed_methods
        ]
        if not methods:
            raise ValueError(
                "At least one valid HTTP method must be provided per route."
            )

        segments = self._split_path(path)

        current_node = self.root
        for segment in segments:
            if segment.startswith(":"):
                segment = ":"
                current_node.is_dynamic = True
                current_node.param_name = segment[1:]

            if segment not in current_node.children:
                current_node.children[segment] = TrieNode()
            current_node = current_node.children[segment]

        for method in methods:
            current_node.handler[method] = {
                "handler": handler,
                "is_async": iscoroutinefunction(handler),
                "middlewares": middlewares or [],
            }

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
        Retrieves the appropriate route handler based on method and path using Trie traversal.
        Supports dynamic paths.
        """
        segments = self._split_path(path)
        current_node = self.root
        path_params = {}

        for segment in segments:
            if segment in current_node.children:
                # Static path segment
                current_node = current_node.children[segment]
            elif ":" in current_node.children:
                # Dynamic path segment
                param_node = current_node.children[":"]
                path_params[param_node.param_name] = segment
                current_node = param_node
            else:
                # No matching path segment
                return None, None, None

        if method in current_node.handler:
            handler_info = current_node.handler[method]
            handler_with_middlewares = self._apply_middlewares(
                handler_info, method, path
            )
            is_async = handler_info["is_async"]
            return handler_with_middlewares, path_params, is_async

        return None, None, None

    def _split_path(self, path):
        """Splits a path into segments and normalizes it."""
        return [segment for segment in path.strip("/").split("/") if segment]

    ### Middleware Handling ###

    def add_global_middleware(self, middleware) -> None:
        """Adds a middleware that will be applied globally to all routes."""
        self.global_middlewares.append(middleware)

    def _apply_middlewares(self, handler_info, method, path) -> callable:
        """
        Applies the middleware chain to the handler for the given method and path.
        All middlewares are assumed to be synchronous.

        Args:
            handler_info (dict): The route handler information containing the handler function and middlewares.
            method (str): HTTP method.
            path (str): Request path.

        Returns:
            callable: The final handler with middleware applied.
        """
        handler = handler_info["handler"]
        is_async = handler_info["is_async"]

        middlewares = self.global_middlewares[:]
        route_middlewares = handler_info.get("middlewares", [])
        middlewares.extend(route_middlewares)

        for middleware in reversed(middlewares):
            handler = middleware(handler)

        if is_async:

            async def async_wrapper(*args, **kwargs):
                return await handler(*args, **kwargs)

            return async_wrapper

        return handler


"""
Router Utility Classes
"""


class TrieNode:
    def __init__(self):
        self.children = {}
        self.handler = {}
        self.is_dynamic = False
        self.param_name = None
