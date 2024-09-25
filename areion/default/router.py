from asyncio import iscoroutinefunction


class Router:
    """
    Router class for managing HTTP routes and their handlers.

    The Router class provides methods to add routes, group routes, and retrieve
    handlers based on HTTP methods and paths. It supports both static and dynamic
    path segments and allows for the application of middlewares at both global and
    route-specific levels.

    Attributes:
        root (TrieNode): The root node of the routing trie.
        allowed_methods (list): List of allowed HTTP methods.
        middlewares (dict): Dictionary to store middlewares.
        global_middlewares (list): List of global middlewares applied to all routes.
        route_info (list): List of route information for debugging or documentation.
        logger (logging.Logger or None): Logger instance for logging messages.

    Methods:
        add_route(path, handler, methods=["GET"], middlewares=None):
            Adds a route to the router with optional middlewares.

        group(base_path, middlewares=None) -> "Router":
            Creates a sub-router with a base path and optional group-specific middlewares.

        route(path, methods=["GET"], middlewares=[]):
            A decorator to define a route with optional middlewares.

        get_handler(method, path):
            Retrieve the handler for a given HTTP method and path.

        add_global_middleware(middleware) -> None:
            Adds a middleware that will be applied globally to all routes.

        log(level: str, message: str) -> None:
            Logs a message with the specified log level.
    """

    def __init__(self):
        self.root = TrieNode()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.middlewares = {}
        self.global_middlewares = []
        self.route_info = []
        self.logger = None

    def add_route(self, path, handler, methods=["GET"], middlewares=None):
        """
        Adds a route to the router.

        Args:
            path (str): The URL path for the route. Dynamic segments should start with ':'.
            handler (callable): The function or coroutine that handles requests to this route.
            methods (list, optional): A list of HTTP methods this route should respond to. Defaults to ["GET"].
            middlewares (list, optional): A list of middleware functions to apply to this route. Defaults to None.

        Raises:
            TypeError: If the handler is not callable.

        Example:
            def my_handler(request):
                return "Hello, world!"

            router.add_route("/hello", my_handler, methods=["GET"])
        """
        segments = self._split_path(path)
        current_node = self.root
        for segment in segments:
            if segment.startswith(":"):  # Dynamic path segment
                if current_node.dynamic_child is None:
                    current_node.dynamic_child = TrieNode()
                    current_node.dynamic_child.param_name = segment[1:]
                current_node = current_node.dynamic_child
            else:  # Static path segment
                if segment not in current_node.children:
                    current_node.children[segment] = TrieNode()
                current_node = current_node.children[segment]

        for method in methods:
            combined_middlewares = self.global_middlewares + (middlewares or [])
            wrapped_handler = handler
            for middleware in reversed(combined_middlewares):
                wrapped_handler = middleware(wrapped_handler)

            current_node.handler[method] = {
                "handler": wrapped_handler,
                "is_async": iscoroutinefunction(handler),
                "middlewares": middlewares,
                "doc": handler.__doc__,
            }

            self.route_info.append(
                {
                    "path": path,
                    "method": method,
                    "handler": handler,
                    "middlewares": middlewares,
                    "doc": handler.__doc__,
                }
            )

    def group(self, base_path, middlewares=None) -> "Router":
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
        Retrieve the handler for a given HTTP method and path.

        This method traverses the routing tree to find the appropriate handler
        for the specified HTTP method and path. It supports both static and
        dynamic path segments.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            path (str): The URL path to match against the routing tree.

        Returns:
            tuple: A tuple containing:
            - handler (callable or None): The matched handler function, or None if no match is found.
            - path_params (dict): A dictionary of dynamic path parameters and their values.
            - is_async (bool or None): A flag indicating if the handler is asynchronous, or None if no match is found.
        """
        segments = self._split_path(path)
        current_node = self.root
        path_params = {}

        for segment in segments:
            if segment in current_node.children:
                current_node = current_node.children[segment]
            elif current_node.dynamic_child:  # Match dynamic segments
                param_node = current_node.dynamic_child
                path_params[param_node.param_name] = segment  # Store dynamic param
                current_node = param_node
            else:
                return None, None, None

        if method in current_node.handler:
            handler_info = current_node.handler[method]
            is_async = handler_info["is_async"]
            return handler_info["handler"], path_params, is_async

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
        Applies global and route-specific middlewares to the given handler.

        This method takes a handler and wraps it with the middlewares specified
        both globally and for the specific route. If the handler is asynchronous,
        it ensures that the returned handler is also asynchronous.

        Args:
            handler_info (dict): A dictionary containing handler information.
                - "handler" (callable): The original handler function.
                - "is_async" (bool): A flag indicating if the handler is asynchronous.
                - "middlewares" (list, optional): A list of middlewares specific to the route.
            method (str): The HTTP method for the route.
            path (str): The path for the route.

        Returns:
            callable: The handler wrapped with the applied middlewares.
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

    def log(self, level: str, message: str) -> None:
        # Safe logging method (bug fix for scheduled tasks before server is ran)
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message)
        else:
            print(f"[{level.upper()}] {message}")


"""
Router Utility Classes
"""


class TrieNode:
    """
    A node in the Trie structure used for routing.

    Attributes:
        children (dict): A dictionary mapping child node keys to TrieNode objects.
        handler (dict): A dictionary to store handlers associated with this node.
        dynamic_child (TrieNode or None): A reference to a dynamic child node, if any.
        param_name (str or None): The name of the parameter if this node represents a dynamic segment.
    """

    def __init__(self):
        self.children = {}
        self.handler = {}
        self.dynamic_child = None
        self.param_name = None
