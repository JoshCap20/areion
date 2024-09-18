import json
from http.server import BaseHTTPRequestHandler


class Router:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, handler, methods=["GET"]):
        if path not in self.routes:
            self.routes[path] = {}
        for method in methods:
            self.routes[path][method] = handler

    def get_handler(self, server):
        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.handle_request("GET")

            def do_POST(self):
                self.handle_request("POST")

            def do_PUT(self):
                self.handle_request("PUT")

            def do_DELETE(self):
                self.handle_request("DELETE")

            def handle_request(self, method):
                route = self.path
                if (
                    route in server.router.routes
                    and method in server.router.routes[route]
                ):
                    handler = server.router.routes[route][method]
                    response = handler(self)

                    if isinstance(response, dict):  # JSON response
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(response).encode("utf-8"))
                    else:  # HTML response
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        self.wfile.write(response.encode("utf-8"))
                else:
                    self.send_error(404, "Route Not Found")

        return RequestHandler
