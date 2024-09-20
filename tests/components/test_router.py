import unittest
from areion.default import Router


class TestRouter(unittest.TestCase):

    def setUp(self):
        self.router = Router()

    # Base functionality tests
    def test_add_route(self):
        def test_handler(request):
            return "OK"

        self.router.add_route("/test", test_handler, methods=["GET"])
        self.assertIn("/test", self.router.routes)
        self.assertIn("GET", self.router.routes["/test"])
        self.assertEqual(self.router.routes["/test"]["GET"], test_handler)

    def test_route_multiple_methods(self):
        def test_handler(request):
            return "OK"

        self.router.add_route("/test", test_handler, methods=["GET", "POST"])
        self.assertIn("/test", self.router.routes)
        self.assertIn("GET", self.router.routes["/test"])
        self.assertIn("POST", self.router.routes["/test"])
        self.assertEqual(self.router.routes["/test"]["GET"], test_handler)
        self.assertEqual(self.router.routes["/test"]["POST"], test_handler)

    def test_route_not_found(self):
        def test_handler(request):
            return "OK"

        self.router.add_route("/test", test_handler, methods=["GET"])
        # Simulate an invalid route request
        request = type("Request", (object,), {"path": "/wrong"})()
        handler = self.router.routes.get(request.path, {}).get("GET")
        self.assertIsNone(handler)

    def test_route_method_not_allowed(self):
        def test_handler(request):
            return "OK"

        self.router.add_route("/test", test_handler, methods=["GET"])
        # Simulate a method that is not allowed
        request = type("Request", (object,), {"path": "/test"})()
        handler = self.router.routes.get(request.path, {}).get("POST")
        self.assertIsNone(handler)

    # Group routes (Sub-router) tests
    def test_group_routes(self):
        api = self.router.group("/api")

        def test_handler(request):
            return "API OK"

        api.add_route("/test", test_handler, methods=["GET"])
        self.assertIn("/api/test", self.router.routes)
        self.assertEqual(self.router.routes["/api/test"]["GET"], test_handler)

    def test_group_inheriting_methods(self):
        api = self.router.group("/api")

        def test_handler(request):
            return "API OK"

        api.add_route("/test", test_handler)
        self.assertIn("/api/test", self.router.routes)
        self.assertIn("GET", self.router.routes["/api/test"])
        self.assertEqual(self.router.routes["/api/test"]["GET"], test_handler)

    def test_group_with_different_methods(self):
        api = self.router.group("/api")

        def get_handler(request):
            return "GET OK"

        def post_handler(request):
            return "POST OK"

        api.add_route("/test", get_handler, methods=["GET"])
        api.add_route("/test", post_handler, methods=["POST"])

        self.assertEqual(self.router.routes["/api/test"]["GET"], get_handler)
        self.assertEqual(self.router.routes["/api/test"]["POST"], post_handler)

    # Tests for decorators
    def test_route_decorator(self):
        @self.router.route("/decorator", methods=["GET"])
        def test_handler(request):
            return "Decorator OK"

        self.assertIn("/decorator", self.router.routes)
        self.assertIn("GET", self.router.routes["/decorator"])
        self.assertEqual(self.router.routes["/decorator"]["GET"], test_handler)

    def test_route_decorator_in_group(self):
        api = self.router.group("/api")

        @api.route("/message", methods=["GET"])
        def api_message_handler(request):
            return "Hello from the API"

        self.assertIn("/api/message", self.router.routes)
        self.assertIn("GET", self.router.routes["/api/message"])
        self.assertEqual(self.router.routes["/api/message"]["GET"], api_message_handler)

    def test_route_decorator_with_different_methods(self):
        @self.router.route("/multi-method", methods=["GET", "POST"])
        def test_handler(request):
            return "Multi Method OK"

        self.assertIn("/multi-method", self.router.routes)
        self.assertIn("GET", self.router.routes["/multi-method"])
        self.assertIn("POST", self.router.routes["/multi-method"])
        self.assertEqual(self.router.routes["/multi-method"]["GET"], test_handler)
        self.assertEqual(self.router.routes["/multi-method"]["POST"], test_handler)

    # Test default behavior as expected
    def test_add_route_no_methods_implicit(self):
        def test_handler(request):
            return "OK"

        self.router.add_route("/test", test_handler)

        self.assertIn("/test", self.router.routes)
        self.assertIn("GET", self.router.routes["/test"])
        self.assertEqual(self.router.routes["/test"]["GET"], test_handler)

    def test_add_route_no_methods_explicit(self):
        def test_handler(request):
            return "OK"

        with self.assertRaises(ValueError):
            self.router.add_route("/test", test_handler, methods=[""])

    def test_add_route_invalid_method(self):
        def test_handler(request):
            return "OK"

        with self.assertRaises(ValueError):
            self.router.add_route("/test", test_handler, methods=["INVALID"])

    def test_group_route_trailing_slash(self):
        api = self.router.group("/api/")

        def test_handler(request):
            return "API OK"

        api.add_route("/test", test_handler)
        self.assertIn("/api/test", self.router.routes)
        self.assertEqual(self.router.routes["/api/test"]["GET"], test_handler)

    def test_group_route_edge_case(self):
        api = self.router.group("/api//")

        def test_handler(request):
            return "API OK"

        api.add_route("/test", test_handler)
        self.assertIn("/api/test", self.router.routes)
        self.assertEqual(self.router.routes["/api/test"]["GET"], test_handler)

    # Test wildcard routing behavior
    def test_wildcard_route(self):
        def wildcard_handler(request):
            return "Wildcard OK"

        self.router.add_route("/wildcard/*", wildcard_handler, methods=["GET"])
        self.assertIn("/wildcard/*", self.router.routes)
        self.assertEqual(self.router.routes["/wildcard/*"]["GET"], wildcard_handler)

    # Test multiple routes
    def test_multiple_routes(self):
        def test_handler1(request):
            return "Handler 1"

        def test_handler2(request):
            return "Handler 2"

        self.router.add_route("/route1", test_handler1, methods=["GET"])
        self.router.add_route("/route2", test_handler2, methods=["GET"])

        self.assertIn("/route1", self.router.routes)
        self.assertIn("/route2", self.router.routes)
        self.assertEqual(self.router.routes["/route1"]["GET"], test_handler1)
        self.assertEqual(self.router.routes["/route2"]["GET"], test_handler2)

    # Test multiple groups
    def test_multiple_groups(self):
        api_v1 = self.router.group("/api/v1")
        api_v2 = self.router.group("/api/v2")

        def v1_handler(request):
            return "API V1"

        def v2_handler(request):
            return "API V2"

        api_v1.add_route("/users", v1_handler, methods=["GET"])
        api_v2.add_route("/users", v2_handler, methods=["GET"])

        self.assertIn("/api/v1/users", self.router.routes)
        self.assertEqual(self.router.routes["/api/v1/users"]["GET"], v1_handler)
        self.assertIn("/api/v2/users", self.router.routes)
        self.assertEqual(self.router.routes["/api/v2/users"]["GET"], v2_handler)


class TestRouterMiddleware(unittest.TestCase):
    def setUp(self):
        self.router = Router()

    def test_middleware_execution(self):
        def middleware(handler):
            def wrapper(request):
                request.processed = True
                return handler(request)

            return wrapper

        def test_handler(request):
            return "OK"

        self.router.add_route(
            "/test", test_handler, methods=["GET"], middlewares=[middleware]
        )
        request = type("Request", (object,), {"path": "/test", "processed": False})()
        handler, _ = self.router.get_handler("GET", "/test")
        response = handler(request)
        self.assertTrue(request.processed)
        self.assertEqual(response, "OK")

    def test_middleware_chain(self):
        def middleware1(handler):
            def wrapper(request):
                request.processed1 = True
                return handler(request)

            return wrapper

        def middleware2(handler):
            def wrapper(request):
                request.processed2 = True
                return handler(request)

            return wrapper

        def test_handler(request):
            return "OK"

        self.router.add_route(
            "/test",
            test_handler,
            methods=["GET"],
            middlewares=[middleware1, middleware2],
        )
        request = type(
            "Request",
            (object,),
            {"path": "/test", "processed1": False, "processed2": False},
        )()
        handler, _ = self.router.get_handler("GET", "/test")
        response = handler(request)
        self.assertTrue(request.processed1)
        self.assertTrue(request.processed2)
        self.assertEqual(response, "OK")

    def test_middleware_modifies_response(self):
        def middleware(handler):
            def wrapper(request):
                response = handler(request)
                return response + " Modified"

            return wrapper

        def test_handler(request):
            return "OK"

        self.router.add_route(
            "/test", test_handler, methods=["GET"], middlewares=[middleware]
        )
        request = type("Request", (object,), {"path": "/test"})()
        handler, _ = self.router.get_handler("GET", "/test")
        response = handler(request)
        self.assertEqual(response, "OK Modified")

    def test_middleware_in_group(self):
        api = self.router.group("/api")

        def middleware(handler):
            def wrapper(request):
                request.processed = True
                return handler(request)

            return wrapper

        def test_handler(request):
            return "API OK"

        api.add_route("/test", test_handler, methods=["GET"], middlewares=[middleware])
        request = type(
            "Request", (object,), {"path": "/api/test", "processed": False}
        )()
        handler, _ = self.router.get_handler("GET", "/api/test")
        response = handler(request)
        self.assertTrue(request.processed)
        self.assertEqual(response, "API OK")

    def test_middleware_decorator(self):
        def middleware(handler):
            def wrapper(request):
                request.processed = True
                return handler(request)

            return wrapper

        @self.router.route("/decorator", methods=["GET"], middlewares=[middleware])
        def test_handler(request):
            return "Decorator OK"

        request = type(
            "Request", (object,), {"path": "/decorator", "processed": False}
        )()
        handler, _ = self.router.get_handler("GET", "/decorator")
        response = handler(request)
        self.assertTrue(request.processed)
        self.assertEqual(response, "Decorator OK")

    def test_global_middleware(self):
        def global_middleware(handler):
            def wrapper(request):
                request.global_processed = True
                return handler(request)

            return wrapper

        def test_handler(request):
            return "OK"

        self.router.add_global_middleware(global_middleware)
        self.router.add_route("/test", test_handler, methods=["GET"])
        request = type(
            "Request", (object,), {"path": "/test", "global_processed": False}
        )()
        handler, _ = self.router.get_handler("GET", "/test")
        response = handler(request)
        self.assertTrue(request.global_processed)
        self.assertEqual(response, "OK")

    def test_global_and_route_specific_middleware(self):
        def global_middleware(handler):
            def wrapper(request):
                request.global_processed = True
                return handler(request)

            return wrapper

        def route_middleware(handler):
            def wrapper(request):
                request.route_processed = True
                return handler(request)

            return wrapper

        def test_handler(request):
            return "OK"

        self.router.add_global_middleware(global_middleware)
        self.router.add_route(
            "/test", test_handler, methods=["GET"], middlewares=[route_middleware]
        )
        request = type(
            "Request",
            (object,),
            {"path": "/test", "global_processed": False, "route_processed": False},
        )()
        handler, _ = self.router.get_handler("GET", "/test")
        response = handler(request)
        self.assertTrue(request.global_processed)
        self.assertTrue(request.route_processed)
        self.assertEqual(response, "OK")

    def test_middleware_order(self):
        def middleware1(handler):
            def wrapper(request):
                request.order.append(1)
                return handler(request)

            return wrapper

        def middleware2(handler):
            def wrapper(request):
                request.order.append(2)
                return handler(request)

            return wrapper

        def test_handler(request):
            request.order.append(3)
            return "OK"

        self.router.add_route(
            "/test",
            test_handler,
            methods=["GET"],
            middlewares=[middleware1, middleware2],
        )
        request = type("Request", (object,), {"path": "/test", "order": []})()
        handler, _ = self.router.get_handler("GET", "/test")
        response = handler(request)
        self.assertEqual(request.order, [1, 2, 3])
        self.assertEqual(response, "OK")


if __name__ == "__main__":
    unittest.main()
