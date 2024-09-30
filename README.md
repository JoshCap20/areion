# Areion Server

[![License][license-shield]][license-url] [![Downloads](https://static.pepy.tech/badge/areion)](https://pepy.tech/project/areion)
[![Downloads](https://static.pepy.tech/badge/areion/month)](https://pepy.tech/project/areion)

[![PyPi][pypi-shield]][pypi-url] [![PyPi][pypiversion-shield]][pypi-url]

Welcome to the Areion HTTP Server documentation. Areion is a lightweight, asynchronous HTTP server written in Python, designed for simplicity and extensibility. This documentation provides a comprehensive guide to using Areion, covering everything from getting started to advanced usage and component details.

Areion supports asynchronous operations, multithreading, routing, orchestration, customizable loggers, and template engines. The framework provides an intuitive API for building web services, with components like the `Orchestrator`, `Router`, `Logger`, and `Engine` easily swappable or extendable.

We designed Areion to have as few dependencies as possible. We created our own HTTP server on top of asyncio's sockets. While we dream of being the fastest, most preferred Python web server, we know we have a long way to go. We are still in the early stages of development, and we welcome any feedback, contributions, or suggestions. The documentation below is likely to become outdated as we continue to migrate to v2.0.0 which will feature a whole documentation site with more examples, tutorials, and guides.

**Development Mode:** Add the flag `with_development_mode(True)` to the `AreionServerBuilder` to enable development mode. This mode will automatically add Swagger UI and OpenAPI routes to your server. They are accessible from the routes `/docs` and `/openapi` respectively.

## Table of Contents

- [Benchmark](#benchmark)
  - [Benchmark Results](#benchmark-results)
    - [Summary](#summary)
    - [Visualization](#visualization)
    - [Detailed Results](#detailed-results)
  - [Analysis](#analysis)
    - [Throughput (Requests per Second)](#throughput-requests-per-second)
    - [Average Latency](#average-latency)
    - [Total Requests Handled](#total-requests-handled)
    - [Socket Errors](#socket-errors)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Developing](#developing)
  - [Quick Start Guide](#quick-start-guide)
  - [Development Tools](#development-tools)
- [Core Components](#core-components)
  - [AreionServer](#areionserver)
  - [Router](#router)
  - [HttpServer](#httpserver)
- [Default Component Implementation](#default-component-implementation)
  - [Orchestrator](#orchestrator)
  - [Logger](#logger)
  - [Engine](#engine)
- [Advanced Usage](#advanced-usage)
  - [Middleware](#middleware)
  - [Grouping Routes](#grouping-routes)
  - [Template Rendering](#template-rendering)
  - [Task Scheduling](#task-scheduling)
- [API Reference](#api-reference)
  - [AreionServer API](#areionserver-api)
  - [Router API](#router-api)
  - [HttpRequest and HttpResponse](#httprequest-and-httpresponse)
    - [HttpRequest](#httprequest)
    - [HttpResponse](#httpresponse)
    - [Response Utility Functions](#response-utility-functions)
- [Exception Handling](#exception-handling)
- [Best Practices](#best-practices)
  - [Responses](#responses)
- [Missing HTTP/1.1 Features](#missing-http11-features)
- [Contributing](#contributing)
- [License](#license)

---

## Benchmark

We conducted performance benchmarks to compare **Areion**, **FastAPI**, and **Flask**, focusing on throughput and latency under high-load conditions. The goal was to evaluate each framework's ability to handle concurrent connections efficiently and provide fast response times. We used the same JSON response in all frameworks to ensure a fair comparison.

### Benchmark Results

These show the results of running the benchmark test for 30 seconds with 12 threads and 400 connections on my local machine. The test was conducted using the `wrk` benchmarking tool. The results are summarized below, followed by detailed output for each framework.

#### Summary

| Framework | Requests/sec | Avg Latency (ms) | Transfer/sec | Total Requests | Socket Errors             |
| --------- | ------------ | ---------------- | ------------ | -------------- | ------------------------- |
| Areion    | 47,241.97    | 8.46             | 4.42 MB      | 1,418,550      | Read: 545                 |
| FastAPI   | 3,579.10     | 111.53           | 531.27 KB    | 107,613        | Read: 419                 |
| Flask     | 555.98       | 47.45            | 104.79 KB    | 16,708         | Connect: 74, Read: 36,245 |

#### Visualization

![Requests per Second](assets/requests_per_second.png)

![Average Latency](assets/average_latency.png)

#### Detailed Results

**Results show the performance when keep-alive connections are used (HTTP/1.1 default). Areion still significantly outperforms when the header `Connection: close` is set.**

**Areion**

```bash
Running 30s test @ http://localhost:8000/json
  12 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     8.46ms    2.06ms  47.38ms   95.91%
    Req/Sec     3.96k   430.06     5.36k    87.17%
  1,418,550 requests in 30.03s, 132.58MB read
  Socket errors: connect 0, read 545, write 0, timeout 0
Requests/sec:  47,241.97
Transfer/sec:      4.42MB
```

**FastAPI**

```bash
Running 30s test @ http://localhost:8000/json
  12 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   111.53ms   31.97ms 498.08ms   89.55%
    Req/Sec   300.08     59.85   430.00     86.17%
  107,613 requests in 30.07s, 15.60MB read
  Socket errors: connect 0, read 419, write 0, timeout 0
Requests/sec:   3,579.10
Transfer/sec:    531.27KB
```

**Flask**

```bash
Running 30s test @ http://localhost:8000/json
  12 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    47.45ms   53.33ms 556.78ms   96.24%
    Req/Sec   183.12    104.16   590.00     70.64%
  16,708 requests in 30.05s, 3.08MB read
  Socket errors: connect 74, read 36,245, write 125, timeout 0
Requests/sec:     555.98
Transfer/sec:    104.79KB
```

### Analysis

#### Throughput (Requests per Second)

- **Areion:** 47,241.97 requests/sec
- **FastAPI:** 3,579.10 requests/sec
- **Flask:** 555.98 requests/sec

Areion handled approximately 13 times more requests per second than FastAPI and 85 times more than Flask.

#### Average Latency

- **Areion:** 8.46 ms
- **Flask:** 47.45 ms
- **FastAPI:** 111.53 ms

Areion's average latency is about 5.6 times lower than Flask and 13 times lower than FastAPI, indicating faster response times.

#### Total Requests Handled

- **Areion:** 1,418,550 requests
- **FastAPI:** 107,613 requests
- **Flask:** 16,708 requests

Areion processed significantly more total requests during the test duration.

#### Socket Errors

- **Areion:** Read errors: 545
- **FastAPI:** Read errors: 419
- **Flask:** Connect errors: 74, Read errors: 36,245, Write errors: 125

For handling 10x the requests of FastAPI and 85x the requests of Flask, Areion had a relatively low number of socket errors.

## Getting Started

### Installation

Areion can be installed via pip:

```bash
pip install areion
```

### Developing

To get started developing this project, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/JoshCap20/areion.git
```

2. Install the dependencies (preferably in a virtual environment):

```bash
pip install -r requirements.txt
```

3. Run the tests:

```bash
pytest
```

### Quick Start Guide

Below is a simple example to get you started with Areion.

```python

from areion import AreionServerBuilder, DefaultRouter

# Initialize the router
router = DefaultRouter()

# Define a simple route
@router.route("/hello")
def hello_world(request):
    return "Hello, World!"

# Build and run the server
server = AreionServerBuilder().with_router(router).build()
server.run()
```

**Explanation:**

- **Router Initialization:** We create a Router instance to manage our routes.
- **Defining Routes:** Using the @router.route decorator, we define a route that responds to /hello.
- **Server Building:** We use AreionServerBuilder to construct the server with the router.
- **Running the Server:** The server.run() method starts the server synchronously.

### Development Tools

Development tools are essential to increasing development ease and efficiency. With this in mind, we also don't want to slow down the server in production. To enable development tools, add the `with_development_mode(True)` flag to the `AreionServerBuilder`.

**Development Tools:**

- **Swagger UI:** Provides an interactive API documentation interface.
- **OpenAPI Routes:** Exposes auto-generated OpenAPI schema and routes for API exploration.

**Coming Soon:**

- **Automatic Reload:** Automatically reloads the server on code changes.
- **Debugging Tools:** Built-in debugging tools for inspecting requests and responses.
- **Testing Tools:** Integration with testing frameworks for automated testing.
- **Security Tools:** Security checks and recommendations for your server.
- **Performance Tools:** Performance monitoring and optimization tools.

## Core Components

### AreionServer

The `AreionServer` is the main class that represents the server. It manages components such as the router, orchestrator, logger, and HTTP server.

**Key Features:**

- **Asynchronous Operation:** Built on top of asyncio for non-blocking operations.
- **Component Integration:** Integrates with router, orchestrator, and other components.
- **Static File Serving:** Supports serving static files.

_Do not initialize AreionServer directly unless you know what you're doing. Use AreionServerBuilder to create an instance which includes safeguards and defaults required for other components._

#### AreionServerBuilder

The `AreionServerBuilder` provides a fluent interface for constructing an AreionServer instance with the desired components and configurations.

**Only a router is required for a minimal server setup.**

**Example:**

```python
from areion import AreionServerBuilder, DefaultRouter, DefaultLogger, DefaultOrchestrator, DefaultEngine

router = DefaultRouter()
logger = DefaultLogger()
orchestrator = DefaultOrchestrator()
engine = DefaultEngine()

server = AreionServerBuilder().with_router(router).with_logger(logger).with_orchestrator(orchestrator).with_port(8080).with_engine(engine).with_static_dir("static").build()
```

### Router

The `Router` class manages URL routes and their corresponding handlers. If no methods are defined, it defaults to only accepting GET requests. You can define middleware at the route, route group, or global level.

**Key Features:**

- **Dynamic Routing:** Supports dynamic path segments (e.g., /user/:id).
- **Method Specification:** Handlers can specify allowed HTTP methods.
- **Middleware Support:** Allows adding global and route-specific middleware.

**Usage:**

```python
from areion import DefaultRouter

router = DefaultRouter()

# Adding a route with a dynamic segment
@router.route("/user/:id", methods=["GET"])
def get_user(request, id):
    return f"User ID: {id}"

# Adding global middleware
def log_request(handler):
    def wrapper(request, *args, **kwargs):
        print(f"Received request: {request.path}")
        return handler(request, *args, **kwargs)
    return wrapper

router.add_global_middleware(log_request)
```

You can also use a Django-like syntax for defining routes:

```python
router = DefaultRouter()

def get_user(request, id):
    return f"User ID: {id}"

router.add_route("/user/:id", get_user, methods=["GET"])
```

Route with middleware:

```python
router = DefaultRouter()

def get_user(request, id):
    return f"User ID: {id}"

def log_request(handler):
    def wrapper(request, *args, **kwargs):
        print(f"Received request: {request.path}")
        return handler(request, *args, **kwargs)
    return wrapper

router.add_route("/user/:id", get_user, methods=["GET"], middlewares=[log_request])
```

### HttpServer

The `HttpServer` class handles the low-level HTTP protocol details.

**Key Features:**

- **Request Handling:** Processes incoming HTTP requests.
- **Response Sending:** Formats and sends HTTP responses.
- **Connection Management:** Manages client connections asynchronously.

**Usage:**

This class is usually managed internally by `AreionServer` and doesn't require direct interaction.

## Default Component Implementation

Areion provides default implementations for several core components that can be used out of the box. These components are designed to work together seamlessly and provide a solid foundation for building web applications. Feel free to use these default components or create your own custom implementations according to the interfaces in `areion/base`.

### Orchestrator

The `Orchestrator` class manages background tasks and scheduling. The startup and shutdown are managed by the `AerionServer`.

**Key Features:**

- **Task Submission:** Allows submitting tasks to be executed asynchronously.
- **Scheduling:** Supports scheduling tasks using cron expressions.
- **Thread Management:** Uses a thread pool for concurrent execution.

**Usage:**

```python
from areion import DefaultOrchestrator

orchestrator = DefaultOrchestrator(max_workers=4)

def background_task():
    print("Running background task")

# Submit a task
orchestrator.submit_task(background_task)

# Schedule a cron task
orchestrator.schedule_cron_task(background_task, {'hour': '*/1'})
```

### Logger

The `Logger` class provides logging capabilities. This logger is passed to multiple other components and also injected into each HttpRequest that is accesible in every route handler.

**Key Features:**

- **Configurable Levels:** Supports standard logging levels (INFO, DEBUG, ERROR, etc.).
- **File and Console Logging:** Can log to both files and the console.
- **Formatter Support:** Customizable log formatting.

**Usage:**

```python
from areion import DefaultLogger, AreionServerBuilder, DefaultRouter

router = DefaultRouter()
logger = DefaultLogger(log_file="server.log", log_level="INFO")

@router.route("/log", methods=["GET"])
def some_handler(request):
    logger.info("Processing request")
    return "Response"

server = AreionServerBuilder().with_router(router).with_logger(logger).build()
```

### Engine

The `Engine` class handles template rendering.

**Key Features:**

**Jinja2 Integration:** Uses Jinja2 for template rendering.
**Template Directory:** Configurable template directory.

**Usage:**

```python
from areion import DefaultEngine

engine = Engine(templates_dir="templates")

# Rendering a template
def home(request):
    context = {"title": "Home"}
    return request.render_template("home.html", context)
```

## Advanced Usage

### Middleware

Middleware functions allow you to process requests and responses globally or for specific routes.

**Creating Middleware:**

```python
def auth_middleware(handler):
    def wrapper(request, *args, **kwargs):
        if not request.get_header("Authorization"):
            return HttpResponse(status_code=401, body="Unauthorized")
        return handler(request, *args, **kwargs)
    return wrapper
```

**Applying Middleware:**

**Global Middleware:**

```python
router.add_global_middleware(auth_middleware)
```

**Route-specific Middleware:**

```python
@router.route("/dashboard", middlewares=[auth_middleware])
def dashboard(request):
    return "Welcome to the dashboard"
```

### Grouping Routes

You can group routes under a common path and apply middlewares to the group.

**Usage:**

```python
# Define group-specific middleware
def group_middleware(handler):
    def wrapper(request, *args, **kwargs):
        print("Group middleware executed")
        return handler(request, *args, **kwargs)
    return wrapper

# Create a route group
api_group = router.group("/api", middlewares=[group_middleware])

@api_group.route("/users")
def api_users(request):
    return "API Users"

@api_group.route("/posts")
def api_posts(request):
    return "API Posts"
```

### Template Rendering

Use the Engine component to render templates with dynamic content.

**Usage:**

```python
def profile(request):
    user_data = {"name": "John Doe", "age": 30}
    return request.render_template("profile.html", user_data)
```

### Task Scheduling

Schedule tasks to run at specified intervals using the Orchestrator.

**Usage:**

```python
def cleanup_task():
    print("Performing cleanup")

# Schedule to run every day at midnight
orchestrator.schedule_cron_task(cleanup_task, {'hour': '0', 'minute': '0'})
```

## API Reference

### AreionServer API

#### AreionServer

Represents the main server class.

**Constructor Parameters:**

- `host (str)`: Server host address.
- `port (int)`: Server port number.
- `router (Router)`: Router instance.
- `orchestrator (Orchestrator, optional)`: Orchestrator instance.
- `logger (Logger, optional)`: Logger instance.
- `engine (Engine, optional)`: Template engine instance.
- `static_dir (str, optional)`: Directory for static files.

**Methods:**

- `run()`: Starts the server synchronously.
- `start()`: Starts the server asynchronously.
- `stop()`: Initiates server shutdown.

#### AreionServerBuilder

Builder class for constructing AreionServer instances.

**Methods:**

- `with_host(host)`: Sets the server host.
- `with_port(port)`: Sets the server port.
- `with_router(router)`: Sets the router.
- `with_orchestrator(orchestrator)`: Sets the orchestrator.
- `with_logger(logger)`: Sets the logger.
- `with_engine(engine)`: Sets the template engine.
- `with_static_dir(static_dir)`: Sets the static directory.
- `with_development_mode(bool)`: Enables development mode and Swagger UI/OpenAPI routes.
- `build()`: Builds and returns an AreionServer instance.

### Router API

#### Router

Manages URL routes and their handlers.

**Methods:**

- `add_route(path, handler, methods, middlewares)`: Adds a route.
- `route(path, methods, middlewares)`: Decorator for adding routes.
- `group(base_path, middlewares)`: Creates a sub-router (group).
- `add_global_middleware(middleware)`: Adds a global middleware.
- `get_handler(method, path)`: Retrieves the handler for a given path and method.

### HttpRequest and HttpResponse

#### HttpRequest

Represents an HTTP request. These are injected into each route handler as the first argument via the HttpServer.

**Attributes:**

- `method (str)`: HTTP method.
- `path (str)`: Request path.
- `headers (dict)`: Request headers.
- `metadata (dict)`: Additional metadata.
- `body (str)`: Request body.
- `path (str)`: Request path.
- `query_params (dict)`: Query parameters.

**Methods:**

- `add_header(key, value)`: Adds a header.
- `get_header(key)`: Retrieves a header value.
- `get_body()`: Retrieves the request body.
- `get_query_param(key)`: Retrieves a query parameter.
- `add_metadata(key, value)`: Adds metadata.
- `get_metadata(key)`: Retrieves metadata.
- `render_template(template_name, context)`: Renders a template.
- `submit_task(task, *args)`: Submits a task to the orchestrator.
- `log(message, level)`: Logs a message.
- `as_dict()`: Converts the request to a dictionary.

#### HttpResponse

Represents an HTTP response.

**Constructor Parameters:**

- `body (any)`: Response body.
- `status_code (int)`: HTTP status code.
- `content_type (str, optional)`: Content type.
- `headers (dict, optional)`: Additional headers.

**Methods:**

- `format_response()`: Formats the response for sending.
- `set_header(key, value)`: Sets a header.
- `set_headers(headers)`: Sets multiple headers.
- `set_status_code(status_code)`: Sets the status code.

#### Response Utility Functions

- `create_file_response(file_path: str, status_code: int = 200)`: Creates a response for a file given a filepath.
- `create_json_response(data: dict, status_code: int = 200)`: Creates a JSON response.
- `create_text_response(text: str, status_code: int = 200)`: Creates a text response.
- `create_html_response(html: str, status_code: int = 200)`: Creates an HTML response.
- `create_redirect_response(location: str, status_code: int = 302)`: Creates a redirect response.
- `create_error_response(status_code: int, message: str = None, headers: dict = None)`: Creates an error response.
- `create_empty_response(status_code: int = 204, headers: dict = None)`: Creates an empty response.

## Exception Handling

Areion provides custom exceptions for common HTTP errors. These exceptions can be raised in route handlers to return the corresponding error response and status code.

- `HttpError`: Base class for HTTP errors.
- `BadRequestError`: Corresponds to 400 Bad Request.
- `UnauthorizedError`: Corresponds to 401 Unauthorized.
- `ForbiddenError`: Corresponds to 403 Forbidden.
- `NotFoundError`: Corresponds to 404 Not Found.
- `MethodNotAllowedError`: Corresponds to 405 Method Not Allowed.
- `InternalServerError`: Corresponds to 500 Internal Server Error.

**Easily create custom exceptions by subclassing the HttpError class.**

**Usage:**

```python
from areion import NotFoundError

def get_item(request, item_id):
    item = database.get(item_id)
    if not item:
        raise NotFoundError("Item not found")
    return item
```

_Exceptions in routes and middleware are handled globally and converted to a proper HTTP response._

## Best Practices

### Responses

We recommend returning a `HttpResponse` object directly from route handlers. This allows for more control over the response status code, headers, and body. Additionally, it is recommended, but not required, to pass an explicit `content_type` during construction for performance reasons.

_Helpful wrappers now exist in the `areion/utils/response_utils.py` to make this easier for common use cases._

_Make sure that objects are JSON serializable before returning them in the response body._

**Example:**

```python
from areion import HttpResponse

@router.route("/user", methods=GET)
def get_user(request):
    user = {
        "name": "John Doe",
        "age": 30
    }
    return HttpResponse(body=user, content_type="application/json")
```

## Missing HTTP/1.1 Features

- **Chunked Transfer Encoding:** Areion does not support chunked transfer encoding yet.
- **Compression:** Areion does not support compression yet.
- **Caching:** Areion does not support caching yet.
- **Cookies:** Areion does not support cookies yet.
- **Range Requests:** Areion does not support range requests yet.

## Contributing

Contributions are welcome! For feature requests, bug reports, or questions, please open an issue. If you would like to contribute code, please open a pull request with your changes.

## License

MIT License

Copyright (c) 2024 Joshua Caponigro

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

[pypi-shield]: https://img.shields.io/pypi/pyversions/areion?color=281158
[pypi-url]: https://pypi.org/project/areion/
[pypiversion-shield]: https://img.shields.io/pypi/v/areion?color=361776
[license-url]: https://github.com/JoshCap20/areion/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/joshcap20/areion
