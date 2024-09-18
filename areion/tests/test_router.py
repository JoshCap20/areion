import unittest
from areion.default import Router

class TestRouter(unittest.TestCase):

    def setUp(self):
        self.router = Router()

    def test_add_route(self):
        def test_handler(request):
            return "OK"
        self.router.add_route("/test", test_handler, methods=["GET"])
        self.assertIn("/test", self.router.routes)
        self.assertIn("GET", self.router.routes["/test"])
        self.assertEqual(self.router.routes["/test"]["GET"], test_handler)

    def test_group_routes(self):
        api = self.router.group("/api")
        
        def test_handler(request):
            return "API OK"
        
        api.add_route("/test", test_handler, methods=["GET"])
        self.assertIn("/api/test", self.router.routes)
        self.assertEqual(self.router.routes["/api/test"]["GET"], test_handler)

    def test_route_not_found(self):
        def test_handler(request):
            return "OK"
        self.router.add_route("/test", test_handler, methods=["GET"])
        
        request = type('Request', (object,), {'path': '/wrong'})()
        handler = self.router.routes.get(request.path, {}).get("GET")
        self.assertIsNone(handler)
