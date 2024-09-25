import json
import os
import inspect
from ..core import HttpResponse

ENV = os.getenv("ENV", "development")


class SwaggerHandler:
    """
    Handles the generation of OpenAPI documentation and Swagger UI.

    Args:
        router (Router): The router instance used to register
            routes and retrieve route information.

    Can be toggled on via:
        1. Setting development flag on AerionServerBuilder
        2. Setting ENV variable to 'development'
    """

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
            handler = route["handler"]
            doc = route["doc"] or ""

            # Parse docstring for summary and description
            doc_lines = doc.strip().split("\n")
            summary = doc_lines[0] if doc_lines else ""
            description = "\n".join(doc_lines[1:]).strip() if len(doc_lines) > 1 else ""

            parameters = []

            # Get dynamic segments from path
            path_segments = self._split_path(path)
            path_params = [
                segment[1:] for segment in path_segments if segment.startswith(":")
            ]

            # Get handler signature
            sig = inspect.signature(handler)
            params = sig.parameters

            for param_name, param in params.items():
                if param_name == "request":
                    continue

                # Determine if parameter is in path or query
                if param_name in path_params:
                    param_in = "path"
                    required = True
                else:
                    param_in = "query"
                    required = param.default == inspect.Parameter.empty

                # Get parameter type from annotation
                annotation = param.annotation
                if annotation != inspect.Parameter.empty:
                    openapi_type = SwaggerHandler.map_python_type_to_openapi(annotation)
                else:
                    openapi_type = "string"

                parameter_spec = {
                    "name": param_name,
                    "in": param_in,
                    "required": required,
                    "schema": {"type": openapi_type},
                }
                parameters.append(parameter_spec)

            # Build the path item
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}

            openapi_spec["paths"][path][method] = {
                "summary": summary,
                "description": description,
                "parameters": parameters,
                "responses": {"200": {"description": "Successful Response"}},
            }

        return openapi_spec

    def _split_path(self, path):
        """Splits a path into segments and normalizes it."""
        return [segment for segment in path.strip("/").split("/") if segment]

    @staticmethod
    def map_python_type_to_openapi(python_type):
        type_mapping = {
            int: "integer",
            str: "string",
            bool: "boolean",
            float: "number",
            dict: "object",
            list: "array",
            type(None): "null",
        }
        return type_mapping.get(python_type, "any")
