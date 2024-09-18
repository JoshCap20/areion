# Areion

Areion is a lightweight, fast, and extensible Python web server framework. It supports multithreading, routing, orchestration, and customizable loggers and template engines.

Some say it is the simplest API ever. They might be right. To return a JSON response, you just return a dictionary. To return an HTML response, you just return a string. Return bytes for an octet-stream response. That's it.

Every component (Orchestrator, Router, Logger, etc.) is optional and can be replaced with your own implementation, just implement the interface. You can also add your own components to the server and easily extend its functionality.

## Key Features

- **Simple API**: Return dictionaries for JSON responses and strings for HTML responses.
- **Multithreading**: Support for multi-threading for concurrent requests.
- **Routing**: High-performance router that supports various HTTP methods (GET, POST, PUT, DELETE) with method control at both route and group levels.
- **Orchestration**: Orchestrator Handler for managing tasks like thread management, background jobs, and task queues.
- **Logging**: Structured logging system that allows multiple logging levels (DEBUG, INFO, WARN, ERROR).
- **Extensibility**: Add your own components to the server and easily extend its functionality.
- **Customizable**: Every component is optional and can be replaced with your own implementation.

## Installation

You can install Areion via pip:

```bash
pip install areion
```

## Usage Example

### Simple Usage

```python
from areion import AreionServer, DefaultRouter, DefaultOrchestrator

router = DefaultRouter()
orchestrator = DefaultOrchestrator(max_workers=3)

# Dictionaries are automatically returned as JSON responses
@router.route("/")
def home_handler(request):
    return {"msg": "Hello from Areion Server"}

# Build the server with whatever components you want. Nothing is required.
server = AreionServer()
            .with_orchestrator(orchestrator)
            .with_router(router)
            .with_port(8000)

# Start the server (also starts the orchestrator and background tasks)
server.start()
```

### Minimalist Usage

```python
from areion import AreionServer, DefaultRouter

def api_handler(request):
    x = 5 + 2
    return {"content": f"5 + 2 = {x}"}

router = DefaultRouter()
router.add_route("/api", api_handler)

server = AreionServer().with_router(router)

server.start()
```

The only required component is a router. This is because... it's a web server. You need to route requests to handlers. Everything else is optional.

## Components

### Orchestrator

The Orchestrator is a centralized component designed to manage tasks such as thread management, background jobs, and task queues. It is responsible for efficiently managing the server's resources and ensuring that tasks are executed in a timely manner. By assigning tasks to the Orchestrator, you can offload execution and scheduling, allowing the server to handle concurrent operations seamlessly.

#### Orchestrator Demo

Below is an example demonstrating how to use the Orchestrator to schedule and manage tasks:

```python
from areion import AreionServer, DefaultOrchestrator

def background_task(task_id, duration):
    print(f"Running background task {task_id} for {duration} seconds.")
    import time
    time.sleep(duration)
    return f"Background task {task_id} completed."

# Initialize the Orchestrator
orchestrator = DefaultOrchestrator(max_workers=3)

# Schedule a cron task to run every 10 seconds
orchestrator.schedule_cron_task(
    lambda: print("Scheduled task running..."), {"second": "*/10"}
)

# Submit background tasks to the Orchestrator
orchestrator.submit_task(background_task, "Task 1", 5)
orchestrator.submit_task(background_task, "Task 2", 3)

server = AerionServer().with_orchestrator(orchestrator)

# Start the server
server.start()
```

In this example:

- `background_task` is a function that simulates a background job.
- `schedule_cron_task` schedules a task to run every 10 seconds.
- `submit_task` submits tasks to be executed by the Orchestrator.
- `start` starts the server and the Orchestrator.

#### BaseOrchestrator Interface

```python
class BaseOrchestrator(ABC):
    @abstractmethod
    def submit_task(self, func, *args):
        pass

    @abstractmethod
    def schedule_cron_task(self, func, cron_expression, *args):
        pass

    @abstractmethod
    def shutdown(self):
        pass
```

### Router

The Router is a flexible, high-performance component that maps incoming requests to the appropriate handler functions based on the request’s path and method. It supports various HTTP methods (GET, POST, PUT, DELETE), and you can define specific allowed methods per route or even per group of routes.

The Router also supports:

- **Route Groups (Sub-routers):** Organize routes under common prefixes.
- **Route Decorators:** Define routes more concisely using decorators.
- **Per-route Method Control:** Specify allowed methods for each route or group.

#### Router Demo

Below is an example demonstrating how to use the Router to define routes, handlers, and engine rendering:

```python

from areion import AreionServer, DefaultRouter

router = DefaultRouter()

# Define handlers
def home_handler(request):
    return {"msg": "Welcome to Areion Server", "version": "1.0"}

# Add routes with different allowed methods
router.add_route("/", home_handler, methods=["GET"])  # Only GET allowed

# Create a sub-router (group)
api = router.group("/api")

# You can also use decorators to define routes
@api.route("/message", methods=["GET"])
def api_message_handler(request):
    return {"message": "Hello from the API"}

@api.route("/submit", methods=["POST"])
def api_submit_handler(request):
    return {"message": "Data submitted successfully"}

# Initialize the server
server = AreionServer().with_router(router)

# Start the server
server.start()
```

#### Sub-groups and Method Control

You can easily group routes together and define method restrictions for each group or individual route.

```python
# Create API sub-router
api = router.group("/api", allowed_methods=["GET", "POST"])

@api.route("/message", methods=["GET"])
def api_message_handler(request):
    return {"message": "Hello from the API"}

@api.route("/submit", methods=["POST"])
def api_submit_handler(request):
    return {"message": "Data submitted successfully!"}
```

- Sub-groups: Organize your routes under common prefixes using group().
- Method Control: Specify allowed methods per route or group. 

#### Simple API Demo

```python
from areion import AreionServer, DefaultRouter

router = DefaultRouter()

# Can add any logic, assign tasks to the orchestrator (if defined)
@router.route("/", methods=["GET"])
def home_handler(request):
    return {"msg": "Hello from Areion Server", "version": "1.0", "status": "OK"}

@router.route("/about", methods=["GET"])
def about_handler(request):
    return {"msg": "About Areion Server", "version": "1.0", "status": "OK"}

@router.route("/contact", methods=["GET"])
def contact_handler(request):
    return {"msg": "Contact Areion Server", "version": "1.0", "status": "OK"}

# Initialize the server with the router
server = AreionServer().with_router(router)

# Start the server
server.start()
```

In this example:

- `home_handler`, `about_handler`, and `contact_handler` are handler functions that return JSON responses.
- `add_route` adds routes to the router that map to the appropriate handler functions.
- `with_router` initializes the server with the router.

#### BaseRouter Interface

```python
from abc import ABC, abstractmethod
from typing import Callable, List

class BaseRouter(ABC):
    @abstractmethod
    def add_route(self, route: str, handler: Callable, methods: List[str]) -> None:
        pass

    @abstractmethod
    def get_handler(self, server: 'AreionServer') -> Callable:
        pass
```

### Logger

The Logger is a component that provides a structured logging system for the server. It allows you to log messages at different levels (DEBUG, INFO, WARN, ERROR) and provides a flexible way to customize the logging output. You can easily replace the default logger with your own implementation or add additional loggers to suit your needs.

#### Logger Demo

Below is an example demonstrating how to use the Logger to log messages at different levels:

```python
from areion import AreionServer, DefaultLogger, DefaultRouter

# Initialize the Logger
logger = DefaultLogger(
    log_file="server.log", log_level="INFO"
)

server = AreionServer().with_router(DefaultRouter()).with_logger(logger)

# Start the server
server.start()
```

In this example:

- `DefaultLogger` is a default implementation of the Logger interface.
- `log_file` specifies the file where log messages will be written.
- `log_level` specifies the minimum log level to be written to the log file.

#### BaseLogger Interface

```python
class BaseLogger(ABC):
    @abstractmethod
    def info(self, message):
        pass

    @abstractmethod
    def error(self, message):
        pass
```

### Engine

The Engine is a component that provides a template rendering engine for the server. It allows you to render HTML templates with optional variables and provides a flexible way to customize the rendering process. You can easily replace the default engine with your own implementation or add additional engines to suit your needs.

#### Engine Demo

Below is an example demonstrating how to use the Engine to render HTML templates with optional variables:

```python
from areion import AreionServer, DefaultEngine, DefaultRouter
import os

# Filepath Definitions
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "templates")

# Initialize the Engine and Router
engine = DefaultEngine(template_dir="templates")
router = DefaultRouter()

def render_template_handler(request):
    return engine.render(
        "index.html",
        {"title": "Hello from Areion", "message": "Areion is fast."},
    )

router.add_route("/template", render_template_handler)

server = AreionServer().with_router(router).with_engine(engine)

# Start the server
server.start()
```

In this example:

- `DefaultEngine` is a default implementation of the Engine interface.
- `template_dir` specifies the directory where HTML templates are stored.
- `render` renders an HTML template with optional variables.

#### BaseEngine Interface

```python
class BaseEngine(ABC):
    @abstractmethod
    def render(self, template_name: str, context: dict):
        pass
```

## Contributing

Contributions are welcome! For feature requests, bug reports, or questions, please open an issue. If you would like to contribute code, please open a pull request with your changes.

## License

MIT License

Copyright (c) 2024 Joshua Caponigro

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
