class HttpRequest:
    def __init__(self, method, path, headers, logger=None, engine=None, orchestrator=None):
        self.method = method
        self.path = path
        self.headers = headers
        self.logger = logger
        self.engine = engine
        self.orchestrator = orchestrator
        self.metadata = {}

    def add_header(self, key, value):
        self.headers[key] = value

    def get_header(self, key):
        return self.headers.get(key)

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata.get(key)

    def render_template(self, template_name, context=None):
        """
        Uses the injected template engine (e.g., Jinja2) to render a template.
        """
        if self.engine and context is None:
            context = {}
        return self.engine.render(template_name, context) if self.engine else None

    def submit_task(self, task, *args):
        """
        Submit a task to the orchestrator if available.
        """
        if self.orchestrator:
            return self.orchestrator.submit_task(task, *args)
        else:
            raise ValueError("No orchestrator available to submit the task.")

    def log(self, message, level="info"):
        """
        Log a message using the injected logger.
        """
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message)

    def __repr__(self):
        return f"<HttpRequest method={self.method} path={self.path} headers={self.headers} metadata={self.metadata}>"
    
    def as_dict(self):
        return {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "metadata": self.metadata
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
            orchestrator=self.orchestrator
        )
