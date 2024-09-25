import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from ... import DefaultRouter as Router


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router()

    def test_add_static_route(self):
        # Test adding a static route
        handler = MagicMock()
        self.router.add_route("/test", handler)
        route_handler, path_params, is_async = self.router.get_handler("GET", "/test")
        self.assertEqual(route_handler, handler)
        self.assertEqual(path_params, {})
        self.assertFalse(is_async)

    def test_add_dynamic_route(self):
        # Test adding a dynamic route
        handler = MagicMock()
        self.router.add_route("/user/:id", handler)
        route_handler, path_params, is_async = self.router.get_handler("GET", "/user/123")
        self.assertEqual(route_handler, handler)
        self.assertEqual(path_params, {"id": "123"})
        self.assertFalse(is_async)

    def test_get_handler_invalid_route(self):
        # Test invalid route
        handler = MagicMock()
        self.router.add_route("/valid", handler)
        route_handler, path_params, is_async = self.router.get_handler("GET", "/invalid")
        self.assertIsNone(route_handler)
        self.assertIsNone(path_params)
        self.assertIsNone(is_async)

    def test_get_handler_invalid_method(self):
        # Test invalid method for a valid route
        handler = MagicMock()
        self.router.add_route("/test", handler, methods=["POST"])
        route_handler, path_params, is_async = self.router.get_handler("GET", "/test")
        self.assertIsNone(route_handler)
        self.assertIsNone(path_params)
        self.assertIsNone(is_async)

    def test_add_global_middleware(self):
        # Test global middleware application
        middleware = MagicMock()
        handler = MagicMock()
        self.router.add_global_middleware(middleware)
        self.router.add_route("/test", handler)

        # Check that middleware wraps the handler
        route_handler, path_params, _ = self.router.get_handler("GET", "/test")
        route_handler("request")
        middleware.assert_called_once_with(handler)

    def test_apply_route_specific_middlewares(self):
        # Test route-specific middleware application
        middleware = MagicMock()
        handler = MagicMock()
        self.router.add_route("/test", handler, middlewares=[middleware])

        # Check that middleware wraps the handler
        route_handler, path_params, _ = self.router.get_handler("GET", "/test")
        route_handler("request")
        middleware.assert_called_once_with(handler)

    def test_apply_middleware_chain(self):
        # Test multiple middlewares (global and route-specific)
        global_middleware = MagicMock()
        route_middleware = MagicMock()
        handler = MagicMock()

        self.router.add_global_middleware(global_middleware)
        self.router.add_route("/test", handler, middlewares=[route_middleware])

        # Check that both middlewares are applied
        route_handler, path_params, _ = self.router.get_handler("GET", "/test")
        route_handler("request")
        global_middleware.assert_called_once()
        route_middleware.assert_called_once()

    def test_group_routes(self):
        # Test route grouping
        handler = MagicMock()
        group = self.router.group("/api")

        group.add_route("/user", handler)
        route_handler, path_params, _ = self.router.get_handler("GET", "/api/user")
        self.assertEqual(route_handler, handler)
        self.assertEqual(path_params, {})

    def test_group_routes_with_middleware(self):
        # Test grouped routes with middleware
        group_middleware = MagicMock()
        handler = MagicMock()
        group = self.router.group("/api", middlewares=[group_middleware])

        group.add_route("/user", handler)
        route_handler, path_params, _ = self.router.get_handler("GET", "/api/user")
        route_handler("request")
        group_middleware.assert_called_once_with(handler)

    def test_async_handler(self):
        # Test async route handler
        async_handler = AsyncMock()

        self.router.add_route("/async", async_handler, methods=["GET"])

        route_handler, path_params, is_async = self.router.get_handler("GET", "/async")
        self.assertTrue(is_async)

        # Simulate async handler call
        asyncio.run(route_handler("request"))
        async_handler.assert_called_once()

    def test_decorator_add_route(self):
        # Test route decorator
        @self.router.route("/decorated", methods=["GET"])
        def decorated_handler(request):
            return "Hello"

        route_handler, path_params, _ = self.router.get_handler("GET", "/decorated")
        self.assertEqual(route_handler("request"), "Hello")

    def test_route_with_param_and_middleware(self):
        # Test route with parameter and middleware
        def simple_middleware(next_handler):
            def wrapper(request, *args, **kwargs):
                return next_handler(request, *args, **kwargs) + " wrapped"
            return wrapper

        @self.router.route("/items/:id", methods=["GET"], middlewares=[simple_middleware])
        def item_handler(request, id):
            return f"Item {id}"

        route_handler, path_params, _ = self.router.get_handler("GET", "/items/42")

        response = route_handler("request", id=path_params['id'])

        self.assertEqual(response, "Item 42 wrapped")

    def test_split_path(self):
        # Test _split_path helper method
        result = self.router._split_path("/api/v1/users/")
        self.assertEqual(result, ["api", "v1", "users"])

    def test_dynamic_route_no_param(self):
        # Test dynamic route with missing parameter
        handler = MagicMock()
        self.router.add_route("/user/:id", handler)
        route_handler, path_params, is_async = self.router.get_handler("GET", "/user/")
        self.assertIsNone(route_handler)
        self.assertIsNone(path_params)
        self.assertIsNone(is_async)

    def test_no_middlewares(self):
        # Test route without middleware
        handler = MagicMock()
        self.router.add_route("/test", handler)
        route_handler, path_params, _ = self.router.get_handler("GET", "/test")
        self.assertEqual(route_handler, handler)

    def test_trie_structure(self):
        # Test if TrieNode correctly stores route segments
        handler = MagicMock()
        self.router.add_route("/test/route", handler)
        route_handler, path_params, _ = self.router.get_handler("GET", "/test/route")
        self.assertEqual(route_handler, handler)


if __name__ == "__main__":
    unittest.main()
