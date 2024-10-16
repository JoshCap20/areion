"""
HttpRequest is the representation of the request passed to route handlers by the server.
"""

from .response import HttpResponse
from urllib.parse import urlparse, parse_qsl
import orjson


class HttpRequest:
    """
    HttpRequest class represents an HTTP request with various attributes and methods to manipulate and retrieve request data.
    Request objects are passed as arguments to route handlers by the server. It includes access to certain HTTP request components,
        such as headers, body, and metadata, as well as provide access to logging, template rendering, and task submission.
    Attributes:
        method (str): The HTTP method (e.g., GET, POST).
        path (str): The path of the request.
        headers (dict): A dictionary of request headers.
        body (str, optional): The body of the request. Defaults to None.
        logger (object, optional): A logger instance for logging messages. Defaults to None.
        engine (object, optional): A template engine instance for rendering templates. Defaults to None.
        orchestrator (object, optional): An orchestrator instance for submitting tasks. Defaults to None.
        metadata (dict): A dictionary for storing additional metadata. Always an empty dictionary on initialization.
    Methods:
        add_header(key: str, value: any) -> None:
            Adds a header to the request.
        get_header(key: str) -> str | None:
            Retrieve the value of a specified header.
        get_raw_body() -> str | None:
            Retrieve the raw request body as a str if available.
        get_parsed_body() -> dict | str | None:
            Retrieve the parsed request body as a dictionary.
        add_metadata(key: str, value: any) -> None:
            Adds a metadata entry to the request.
        get_metadata(key: str) -> any:
            Retrieve the value associated with a given key from the metadata.
        get_query_param(key: str) -> any:
            Retrieve the value associated with a given key from the query parameters
        render_template(template_name: str, context: dict = None) -> str:
            Renders a template using the injected template engine.
        submit_task(task: callable, *args):
            Submit a task to the orchestrator for execution.
        log(message: str, level: str = "info"):
            Log a message using the injected logger.
        as_dict(show_components: bool = False) -> dict:
            Returns a dictionary representation of the HttpRequest instance.
    """

    def __init__(
        self,
        method,
        path,
        headers,
        body=None,
        logger=None,
        engine=None,
        orchestrator=None,
    ):
        """
        Don't call this directly. Use HttpRequestFactory instead.
        """
        self.method: str = method
        self.headers: dict = headers
        self.body: bytes = body
        self.metadata: dict = {}
        self.logger = logger
        self.engine = engine
        self.orchestrator = orchestrator

        parsed_url = urlparse(path)
        self.path = parsed_url.path
        self.query_params = parsed_url.query

        # Internal variables for lazy parsing
        self._parsed_body = None
        self._parsed_query_params = None

    def add_header(self, key: str, value: any) -> None:
        """
        Adds a header to the request.
        Args:
            key (str): The name of the header.
            value (any): The value of the header.
        """
        self.headers[key] = value

    def get_header(self, key) -> str | None:
        """
        Retrieve the value of a specified header.
        Args:
            key (str): The name of the header to retrieve.
        Returns:
            str or None: The value of the specified header if it exists, otherwise None.
        """
        return self.headers.get(key)

    def get_parsed_body(self) -> dict | str | None:
        """
        Lazily parse the body of the request and return it as a dictionary or string.

        Supports 'application/json', 'application/x-www-form-urlencoded', and 'multipart/form-data'.

        Returns:
            dict or str or None: The parsed body of the request if it exists, otherwise None.
        """
        if self._parsed_body is not None:
            return self._parsed_body

        if not self.body:
            return None

        content_type: str = self.get_header("Content-Type")
        if not content_type:
            return None

        content_type_main = content_type.split(";")[0].strip()

        try:
            if content_type_main == "application/json":
                self._parsed_body = self._parse_json_body()
            elif content_type_main == "application/x-www-form-urlencoded":
                self._parsed_body = self._parse_form_urlencoded_body()
            elif content_type_main == "multipart/form-data":
                self._parsed_body = self._parse_multipart_body(content_type)
            else:
                self._parsed_body = self.body.decode("utf-8")
        except Exception as e:
            self.log(f"Error parsing body: {e}", level="error")
            self._parsed_body = None

        return self._parsed_body

    def _parse_json_body(self) -> dict | None:
        """
        Parse the JSON body of the request.

        Returns:
            dict or None: The parsed JSON body, or None if parsing fails.
        """
        try:
            return orjson.loads(self.body)
        except orjson.JSONDecodeError as e:
            self.log(f"JSON parsing error: {e}", level="error")
            return None

    def _parse_form_urlencoded_body(self) -> dict:
        """
        Parse 'application/x-www-form-urlencoded' body.

        Returns:
            dict: The parsed form data.
        """
        return dict(parse_qsl(self.body.decode("utf-8")))

    def get_raw_body(self) -> str | None:
        """
        Retrieve the body of the request.
        Returns:
            str or None: The body of the request if it exists, otherwise None.
        """
        return self.body if self.body else None

    def add_metadata(self, key: str, value: any) -> None:
        """
        Adds a metadata entry to the request.
        Args:
            key (str): The key for the metadata entry.
            value (any): The value for the metadata entry.
        """
        self.metadata[key] = value

    def get_metadata(self, key) -> any:
        """
        Retrieve the value associated with a given key from the metadata.
        Args:
            key (str): The key for which to retrieve the value from the metadata.
        Returns:
            Any: The value associated with the specified key, or None if the key is not found.
        """
        return self.metadata.get(key)

    def get_query_param(self, key) -> any:
        """
        Retrieve the value associated with a given key from the query parameters.
        Args:
            key (str): The key for which to retrieve the value from the query parameters.
        Returns:
            Any: The value associated with the specified key, or None if the key is not found.
        """
        return self.get_parsed_query_params().get(key)

    def get_raw_query_params(self) -> str:
        """
        Retrieve the raw query parameters from the request URL.
        Returns:
            str: The query parameters as an unparsed string.
        """
        return self.query_params

    def get_parsed_query_params(self) -> dict:
        """
        Lazily parse the query parameters from the request URL and return them as a dictionary.

        Returns:
            dict: A dictionary containing the parsed query parameters.
        """
        if self._parsed_query_params is not None:
            return self._parsed_query_params

        self._parsed_query_params = dict(parse_qsl(self.query_params))
        return self._parsed_query_params

    def render_template(self, template_name: str, context: dict = None) -> str:
        """
        Renders a template using the injected template engine.
        Args:
            template_name (str): The name of the template to render.
            context (dict, optional): A dictionary containing context variables to pass to the template. Defaults to an empty dictionary if not provided.
        Returns:
            str: The rendered template as a string.
        Raises:
            ValueError: If no template engine is available.
        """
        if not self.engine:
            raise ValueError("No template engine available to render the template.")
        if context is None:
            context = {}
        template = self.engine.render(template_name, context)
        return HttpResponse(content_type="text/html", body=template)

    def submit_task(self, task: callable, *args):
        """
        Submit a task to the orchestrator for execution.
        Args:
            task (callable): The task to be submitted.
            *args: Additional arguments to pass to the task.
        Returns:
            Future: A future object representing the task. (from concurrent.futures)
        Raises:
            ValueError: If no orchestrator is available to submit the task.
        """
        if self.orchestrator:
            return self.orchestrator.submit_task(task, *args)
        else:
            raise ValueError("No orchestrator available to submit the task.")

    def log(self, message: str, level: str = "info") -> None:
        """
        Log a message using the injected logger.
        Parameters:
            message (str): The message to log.
            level (str): The logging level to use (default is "info").
                - options: "debug", "info", "warning", "error", "critical"
        Returns:
            None
        """
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message)
        else:
            print(f"[{level.upper()}] {message}")

    def as_dict(self, show_components: bool = False) -> dict:
        """
        Returns a dictionary representation of the HttpRequest instance.

        Args:
            show_components (bool): Whether to include components like logger, engine, and orchestrator.

        Returns:
            dict: The dictionary representation of the HttpRequest.
        """
        base_dict = {
            "method": self.method,
            "path": self.path,
            "query_params": self.get_parsed_query_params(),
            "headers": self.headers,
            "metadata": self.metadata,
            "body": self.get_parsed_body(),
        }
        if show_components:
            base_dict.update(
                {
                    "logger": self.logger,
                    "engine": self.engine,
                    "orchestrator": self.orchestrator,
                }
            )
        return base_dict

    def __repr__(self) -> str:
        return f"<HttpRequest method={self.method} path={self.path} query_params={self.query_params} headers={self.headers} body={self.body}>"

    def __str__(self) -> str:
        return self.__repr__()


class HttpRequestFactory:
    def __init__(self, logger=None, engine=None, orchestrator=None):
        """
        Factory to create HttpRequest instances with injected dependencies.
        The logger, engine, and orchestrator are singletons provided by the server.
        """
        self.logger = logger
        self.engine = engine
        self.orchestrator = orchestrator

    def create(self, method, path, headers, body: bytes = b"") -> HttpRequest:
        """
        Creates an HttpRequest with injected logger, engine, and orchestrator.
        """
        return HttpRequest(
            method=method,
            path=path,
            headers=headers,
            logger=self.logger,
            engine=self.engine,
            orchestrator=self.orchestrator,
            body=body,
        )
