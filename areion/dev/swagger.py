import json
import os
import inspect
import re
from ..core import HttpResponse, HttpRequest

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
            "info": {"title": "Areion Swagger UI", "version": "v1.1.11"},
            "paths": {},
        }

        for route in self.router.route_info:
            path = route["path"]
            method = route["method"].lower()
            handler = route["handler"]
            doc = (
                inspect.getdoc(handler)
                or "No documentation available for this endpoint."
            )

            # Parse docstring for summary, description, parameters, and responses
            summary, description, doc_params, response_description = (
                self._parse_docstring(doc)
            )

            parameters = []
            request_body_content = None

            # Get dynamic segments from path
            path_segments = self.split_path(path)
            path_params = [
                segment[1:] for segment in path_segments if segment.startswith(":")
            ]

            for param_name, param_info in doc_params.items():
                # Determine if parameter is in path, query, or request body
                if param_name in path_params:
                    param_in = "path"
                    required = True
                elif method in ["post", "put", "patch"]:
                    # For request body parameters
                    param_in = "body"
                    required = param_info.get("required", True)
                else:
                    param_in = "query"
                    required = param_info.get("required", False)

                openapi_type = param_info.get("type", "string")
                description = param_info.get("description", "")

                if param_in == "body":
                    if request_body_content is None:
                        request_body_content = {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": [],
                                }
                            }
                        }
                    request_body_content["application/json"]["schema"]["properties"][
                        param_name
                    ] = {"type": openapi_type, "description": description}
                    if required:
                        request_body_content["application/json"]["schema"][
                            "required"
                        ].append(param_name)
                else:
                    parameter_spec = {
                        "name": param_name,
                        "in": param_in,
                        "required": required,
                        "schema": {"type": openapi_type},
                        "description": description,
                    }
                    parameters.append(parameter_spec)

            # Build the path item
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}

            operation = {
                "summary": summary,
                "description": description,
                "parameters": parameters,
                "responses": {
                    "200": {
                        "description": response_description or "Successful Response"
                    }
                },
            }

            if request_body_content:
                operation["requestBody"] = {
                    "content": request_body_content,
                    "required": True,
                }

            openapi_spec["paths"][path][method] = operation

        return openapi_spec

    def _parse_docstring(self, doc):
        """
        Parse the docstring to extract summary, description, parameters, and response details.

        Args:
            doc (str): The docstring to parse.

        Returns:
            tuple: summary, description, parameters, response_description
        """
        lines = doc.strip().split("\n")
        summary = lines[0].strip() if lines else ""
        description_lines = []
        parameters = {}
        response_description = ""

        current_section = None
        param_pattern = re.compile(r"^(\s*)([\w_]+)\s*\(([\w\[\]]+)\):\s*(.+)")
        for line in lines[1:]:
            stripped_line = line.strip()
            if not stripped_line:
                continue  # skip empty lines

            if stripped_line.lower() == "parameters:":
                current_section = "parameters"
                continue
            elif stripped_line.lower() == "returns:":
                current_section = "returns"
                continue
            elif current_section == "parameters":
                # Try to match a parameter definition
                match = param_pattern.match(line)
                if match:
                    indent, param_name, param_type, param_desc = match.groups()
                    required = True
                    default_match = re.search(
                        r"\(default\s*is\s*([^)]+)\)", param_desc, re.IGNORECASE
                    )
                    if default_match:
                        required = False
                        param_desc = param_desc.replace(
                            default_match.group(0), ""
                        ).strip()
                    parameters[param_name] = {
                        "type": SwaggerHandler.map_python_type_to_openapi(param_type),
                        "description": param_desc,
                        "required": required,
                    }
                else:
                    # Maybe a continuation of the previous parameter's description
                    if parameters and line.startswith(" " * 4):
                        last_param = list(parameters.keys())[-1]
                        parameters[last_param]["description"] += " " + stripped_line
                    else:
                        # Unindented line, exit parameters section
                        current_section = None
            elif current_section == "returns":
                # Collect return description
                if not response_description:
                    response_description = stripped_line
                else:
                    response_description += " " + stripped_line
            else:
                # Accumulate description
                description_lines.append(line)

        description = (
            "\n".join(description_lines).strip()
            if description_lines
            else "No detailed description provided."
        )
        return summary, description, parameters, response_description

    def split_path(self, path):
        """Splits a path into segments and normalizes it."""
        return [segment for segment in path.strip("/").split("/") if segment]

    @staticmethod
    def map_python_type_to_openapi(python_type):
        type_mapping = {
            int: "integer",
            "int": "integer",
            str: "string",
            "str": "string",
            bool: "boolean",
            "bool": "boolean",
            float: "number",
            "float": "number",
            dict: "object",
            "dict": "object",
            list: "array",
            "list": "array",
            type(None): "null",
            "None": "null",
        }
        return type_mapping.get(python_type, "any")
