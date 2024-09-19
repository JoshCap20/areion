# Areion

Areion is a lightweight, fast, and extensible Python web server framework. It supports asynchronous operations, multithreading, routing, orchestration, customizable loggers, and template engines. The framework provides an intuitive API for building web services, with components like the `Orchestrator`, `Router`, `Logger`, and `Engine` easily swappable or extendable.

Some say it is the simplest API ever. They might be right. To return a JSON response, you just return a dictionary. To return an HTML response, you just return a string. Return bytes for an octet-stream response. That's it.

## Key Features

- **Simple API**: Return dictionaries for JSON responses and strings for HTML responses.
- **Asynchronous Server**: Supports asynchronous request handling with the `asyncio` library.
- **Multithreading**: Orchestrate tasks using the orchestrator to manage multiple threads.
- **Routing**: High-performance router supporting HTTP methods (GET, POST, PUT, DELETE) with method control at both route and group levels.
- **Orchestration**: Orchestrator component for managing background tasks, job scheduling, and concurrent execution.
- **Templating**: Render HTML templates using a customizable engine like Jinja2.
- **Builder Pattern**: Use the builder pattern to cleanly configure your server before building it.
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
from areion import AreionServerBuilder, DefaultRouter, DefaultOrchestrator

router = DefaultRouter()
orchestrator = DefaultOrchestrator(max_workers=3)

# Dictionaries are automatically returned as JSON responses
@router.route("/")
def home_handler(request):
    return {"msg": "Hello from Areion Server"}

# Use the builder pattern to configure the server
server = (
    AreionServerBuilder()
    .with_orchestrator(orchestrator)
    .with_router(router)
    .with_port(8082)
    .build()
)

# Start the server (also starts the orchestrator and background tasks)
server.run()
```

### Minimalist Usage

```python
from areion import AreionServerBuilder, DefaultRouter

router = DefaultRouter()

def api_handler(request):
    return {"result": 5 + 2}

router.add_route("/api", api_handler)

server = AreionServerBuilder().with_router(router).build()

server.run()
```

In this example:

- Builder Pattern: You configure the server with a builder before calling build() to instantiate it.
- Asynchronous Server: The server is asynchronous, meaning it can handle concurrent requests using Python's asyncio.

The only required component is a router. This is because... it's a web server. You need to route requests to handlers. Everything else is optional.

## Components

### Orchestrator

The Orchestrator manages concurrent tasks, thread pools, and job scheduling. It helps run background jobs, task queues, or other non-blocking operations efficiently.

#### Orchestrator Demo

Below is an example demonstrating how to use the Orchestrator to schedule and manage tasks:

```python
from areion import AreionServerBuilder, DefaultOrchestrator

def background_task(task_id):
    print(f"Running task {task_id}")
    return f"Task {task_id} completed."

# Initialize the orchestrator
router = DefaultRouter()
orchestrator = DefaultOrchestrator(max_workers=4)

# Submit tasks to the orchestrator
orchestrator.submit_task(background_task, "Task 1")
orchestrator.submit_task(background_task, "Task 2")

# Schedule a cron job to run every 10 seconds
orchestrator.schedule_cron_task(lambda: print("Scheduled task"), {"second": "*/10"})

# Build and start the server
server = AreionServerBuilder().with_router(router).with_orchestrator(orchestrator).build()
server.run()
```

### Router

The Router is responsible for mapping incoming HTTP requests to their respective handler functions. You can define routes, group them, and specify allowed methods for each.

The Router also supports:

- **Route Groups (Sub-routers):** Organize routes under common prefixes.
- **Route Decorators:** Define routes more concisely using decorators.
- **Per-route Method Control:** Specify allowed methods for each route or group.

#### Router Demo

Below is an example demonstrating how to use the Router to define routes, handlers, and engine rendering:

```python
from areion import AreionServerBuilder, DefaultRouter

router = DefaultRouter()

@router.route("/", methods=["GET"])
def home_handler(request):
    return {"message": "Welcome to Areion"}

@router.route("/submit", methods=["POST"])
def submit_handler(request):
    return {"message": "Data submitted successfully"}

server = AreionServerBuilder().with_router(router).build()
server.run()
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
server = AreionServerBuilder().with_router(router)

# Start the server
server.start()
```

### Logger

The Logger is a component that provides a structured logging system for the server. It allows you to log messages at different levels (DEBUG, INFO, WARN, ERROR) and provides a flexible way to customize the logging output. You can easily replace the default logger with your own implementation or add additional loggers to suit your needs.

#### Logger Demo

Below is an example demonstrating how to use the Logger to log messages at different levels:

```python
from areion import AreionServerBuilder, DefaultRouter, DefaultLogger

router = DefaultRouter()

@router.route("/", methods=["GET"])
def home_handler(request):
    request.log("Home handler accessed", level="info")
    request.log(request.as_dict(), level="debug")
    return {"message": "Welcome to Areion"}

# Custom logger
logger = DefaultLogger(log_file="areion.log", log_level="DEBUG")

server = AreionServerBuilder().with_router(router).with_logger(logger).build()
server.run()

```

### Engine

The Engine is responsible for rendering templates. By default, it supports Jinja2 and can be extended to support other template engines.

#### Engine Demo

Below is an example demonstrating how to use the Engine to render HTML templates with optional variables:

```python
from areion import AreionServerBuilder, DefaultRouter, DefaultEngine
import os

# Filepath Definitions
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "templates")

# Initialize the engine with the template directory
engine = DefaultEngine(templates_dir=template_dir)
router = DefaultRouter()

@router.route("/template", methods=["GET"])
def template_handler(request):
    return request.render_template("index.html", {"title": "Welcome", "message": "Hello from Areion"})

server = AreionServerBuilder().with_router(router).with_engine(engine).build()
server.run()
```

### Custom Request and Response Handling

Each request object automatically gets injected with the server's logger, engine, and orchestrator. This allows you to perform tasks like template rendering, logging, and background task submission directly within request handlers.

#### Custom Request Example

```python
from areion import AreionServerBuilder, DefaultRouter

router = DefaultRouter()

@router.route("/log", methods=["GET"])
def log_handler(request):
    request.log("Logging from the /log endpoint", level="info")
    return {"message": "Log entry added"}

@router.route("/background", methods=["GET"])
def background_handler(request):
    def task_to_run():
        print("Running background task")
        return "Task completed"

    request.submit_task(task_to_run)
    return {"message": "Background task submitted"}

server = AreionServerBuilder().with_router(router).build()
server.run()
```

## Contributing

Contributions are welcome! For feature requests, bug reports, or questions, please open an issue. If you would like to contribute code, please open a pull request with your changes.

## License

MIT License

Copyright (c) 2024 Joshua Caponigro

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
