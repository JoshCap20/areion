class HttpRequest:
    def __init__(
        self, method, path, headers, logger=None, engine=None, orchestrator=None
    ):
        """
        Don't call this directly. Use HttpRequestFactory instead.
        """
        self.method = method
        self.path = path
        self.headers = headers
        self.logger = logger
        self.engine = engine
        self.orchestrator = orchestrator
        self.metadata = {}

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

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key):
        """
        Retrieve the value associated with a given key from the metadata.
        Args:
            key (str): The key for which to retrieve the value from the metadata.
        Returns:
            Any: The value associated with the specified key, or None if the key is not found.
        """
        return self.metadata.get(key)

    def render_template(self, template_name: str, context: dict = None):
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
        return self.engine.render(template_name, context)

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

    def log(self, message, level="info"):
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

    def __repr__(self):
        return f"<HttpRequest method={self.method} path={self.path} headers={self.headers} metadata={self.metadata}>"

    def as_dict(self, show_components: bool = False):
        if show_components:
            return {
                "method": self.method,
                "path": self.path,
                "headers": self.headers,
                "metadata": self.metadata,
                "logger": self.logger,
                "engine": self.engine,
                "orchestrator": self.orchestrator,
            }
        return {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
        }


class HttpRequestFactory:
    def __init__(self, logger=None, engine=None, orchestrator=None):
        """
        Factory to create HttpRequest instances with injected dependencies.
        The logger, engine, and orchestrator are singletons provided by the server.
        """
        self.logger = logger
        self.engine = engine
        self.orchestrator = orchestrator

    def create(self, method, path, headers):
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
        )
