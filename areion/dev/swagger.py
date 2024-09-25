import json
import os
from ..core import HttpResponse

ENV = os.getenv("ENV", "development")


class SwaggerHandler:
    def __init__(self, router):
        self.router = router
        if ENV == "development":
            self._register_routes()

    def _register_routes(self):
        # Route to serve the OpenAPI spec
        @self.router.route("/openapi.json")
        def openapi_spec(request):
            spec = self.generate_openapi_spec()
            return HttpResponse(body=json.dumps(spec), content_type="application/json")

        # Route to serve Swagger UI
        @self.router.route("/docs")
        def swagger_ui(request):
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>API Documentation</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.css" />
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui-bundle.js"></script>
                <script>
                const ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                });
                </script>
            </body>
            </html>
            """
            return HttpResponse(body=html_content, content_type="text/html")

    def generate_openapi_spec(self):
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Areion API", "version": "1.0.0"},
            "paths": {},
        }

        for route in self.router.route_info:
            path = route["path"]
            method = route["method"].lower()
            doc = route["doc"] or ""

            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}

            openapi_spec["paths"][path][method] = {
                "summary": doc.strip().split("\n")[0] if doc else "",
                "responses": {"200": {"description": "Successful Response"}},
            }

        return openapi_spec
