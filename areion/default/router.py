from asyncio import iscoroutinefunction
from ..core.exceptions import MethodNotAllowedError, NotFoundError


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
        self.allowed_methods = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        ]
        self.middlewares = {}
        self.global_middlewares = []
        self.route_info = []
        self.logger = None
        self.strict_http: bool = False

    def add_route(
        self,
        path: str,
        handler: callable,
        methods: list[str] = ["GET"],
        middlewares: list[callable] = None,
    ) -> None:
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
        # Does not hurt perfomance since performed at startup
        if self.strict_http and not all(
            method in self.allowed_methods for method in methods
        ):
            raise ValueError("Invalid HTTP method specified.")
        # TODO: Investigate impact on route path
        if self.strict_http and not path.startswith("/"):
            raise ValueError("Path must start with a forward slash.")
        if self._check_if_route_and_methods_exists(path, methods):
            raise ValueError("A route already exists with one of these methods.")
        if not callable(handler):
            raise TypeError("Handler must be a callable function.")

        segments: list = self._split_path(path)
        current_node: TrieNode = self.root
        for segment in segments:
            if segment.startswith(":"):
                if current_node.dynamic_child is None:
                    current_node.dynamic_child = TrieNode()
                    current_node.dynamic_child.param_name = segment[1:]
                current_node = current_node.dynamic_child
            else:
                if segment not in current_node.children:
                    current_node.children[segment] = TrieNode()
                current_node = current_node.children[segment]

        for method in methods:
            combined_middlewares: list = self.global_middlewares + (middlewares or [])
            wrapped_handler: callable = handler
            for middleware in reversed(combined_middlewares):
                wrapped_handler: callable = middleware(wrapped_handler)

            current_node.handler[method] = {
                "handler": wrapped_handler,
                "is_async": iscoroutinefunction(handler),
                "middlewares": middlewares,
                "doc": handler.__doc__,
            }

            # For generating openapi documentation
            self.route_info.append(
                {
                    "path": path,
                    "method": method,
                    "handler": handler,
                    "middlewares": middlewares,
                    "doc": handler.__doc__,
                }
            )

    def group(self, base_path: str, middlewares: list[callable] = None) -> "Router":
        """
        Creates a sub-router (group) with a base path and optional group-specific middlewares.

        Args:
            base_path (str): The base path for the sub-router.
            middlewares (list, optional): List of middleware functions applied to all routes within this group.

        Returns:
            Router: A sub-router instance with the specified base path.
        """
        sub_router = Router()
        group_middlewares: list = middlewares or []

        def add_sub_route(sub_path, handler, methods=["GET"], middlewares=None):
            full_path = f"{base_path.rstrip('/')}/{sub_path.lstrip('/')}"
            combined_middlewares = (middlewares or []) + (group_middlewares or [])
            self.add_route(
                full_path, handler, methods, middlewares=combined_middlewares
            )

        sub_router.add_route = add_sub_route
        return sub_router

    def route(
        self, path: str, methods: list[str] = ["GET"], middlewares: list[callable] = []
    ):
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
            self.add_route(
                path=path, handler=func, methods=methods, middlewares=middlewares
            )
            return func

        return decorator

    def get_handler(self, method: str, path: str) -> tuple:
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
        path = self._remove_query_params(path)
        segments = self._split_path(path)
        current_node = self.root
        path_params = {}

        # TODO: [DESIGN] PASS MORE INFO TO THESE EXCEPTIONS TO GLOBALLY LOG
        for segment in segments:
            if segment in current_node.children:
                current_node = current_node.children[segment]
            elif current_node.dynamic_child:
                param_node = current_node.dynamic_child
                path_params[param_node.param_name] = segment
                current_node = param_node
            else:
                raise NotFoundError()

        if not current_node.handler:
            raise NotFoundError()

        if method in current_node.handler:
            handler_info = current_node.handler[method]
            is_async = handler_info["is_async"]
            return handler_info["handler"], path_params, is_async
        else:
            raise MethodNotAllowedError()

    def add_global_middleware(self, middleware: callable) -> None:
        """
        Adds a middleware that will be applied globally to all routes.

        Parameters:
            middleware (callable): A callable that represents the middleware to be added.
        """
        self.global_middlewares.append(middleware)

    def get_allowed_methods(self, path: str) -> list[str]:
        """
        Returns a list of allowed methods for a given path.
        """
        segments = self._split_path(path)
        current_node = self.root
        for segment in segments:
            if segment in current_node.children:
                current_node = current_node.children[segment]
            elif current_node.dynamic_child:
                current_node = current_node.dynamic_child
            else:
                return []
        return list(current_node.handler.keys())

    ### Utility Methods ###

    def _remove_query_params(self, path: str) -> str:
        """
        Removes query parameters from the path.
        """
        return path.split("?", 1)[0]

    def _split_path(self, path: str) -> list:
        """
        Splits a path into segments and normalizes it.
        """
        return [segment for segment in path.strip("/").split("/") if segment]

    def _check_if_route_and_methods_exists(self, path: str, methods: list[str]) -> bool:
        """
        Checks if a route exists in the router.
        """

        def _check_if_method_exists(path: str, method: str) -> bool:
            """
            Checks if a method exists for a given path.
            """
            path = self._remove_query_params(path)

            segments = self._split_path(path)
            current_node = self.root
            for segment in segments:
                if segment in current_node.children:
                    current_node = current_node.children[segment]
                elif current_node.dynamic_child:
                    current_node = current_node.dynamic_child
                else:
                    return False
            return method in current_node.handler

        for method in methods:
            return _check_if_method_exists(path, method)
        return False

    def log(self, level: str, message: str) -> None:
        """
        Safe logging method.
        (Bug fix for scheduled tasks before server is ran)
        """
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
