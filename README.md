# Areion

Areion is a lightweight, fast, and extensible Python web server framework. It supports multithreading, routing, orchestration, and customizable loggers and template engines.

Some say it is the simplest API ever. They might be right. To return a JSON response, you just return a dictionary. To return an HTML response, you just return a string. That's it.

Every component (Orchestrator, Router, Logger, etc.) is optional and can be replaced with your own implementation, just implement the interface. You can also add your own components to the server and easily extend its functionality.

## Key Features

- **Simple API**: Return dictionaries for JSON responses and strings for HTML responses.
- **Multithreading**: Support for multi-threading for concurrent requests.
- **Routing**: High-performance router that supports various HTTP methods (GET, POST, PUT, DELETE).
- **Orchestration**: Orchestrator Handler for managing tasks like thread management, background jobs, and task queues.
- **Logging**: Build a structured logging system that allows multiple logging levels (DEBUG, INFO, WARN, ERROR).
- **Extensibility**: Add your own components to the server and easily extend its functionality.
- **Customizable**: Every component is optional and can be replaced with your own implementation.

## Components

### Orchestrator

The Orchestrator is a centralized component designed to manage tasks such as thread management, background jobs, and task queues. It is responsible for efficiently managing the server's resources and ensuring that tasks are executed in a timely manner. By assigning tasks to the Orchestrator, you can offload execution and scheduling, allowing the server to handle concurrent operations seamlessly.

#### Orchestrator Demo

Below is an example demonstrating how to use the Orchestrator to schedule and manage tasks:

```python
from areion import AreionServer, Orchestrator

def background_task(task_id, duration):
    print(f"Running background task {task_id} for {duration} seconds.")
    import time
    time.sleep(duration)
    return f"Background task {task_id} completed."

# Initialize the Orchestrator
orchestrator = Orchestrator(max_workers=3)

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

### Router

The Router is a high-performance component that maps incoming requests to the appropriate handler functions based on the request's path and method. It supports various HTTP methods such as GET, POST, PUT, and DELETE, and allows for easy routing of requests to the appropriate handler functions.

#### Router Demo

Below is an example demonstrating how to use the Router to define routes and handle requests:

```python

from areion import AreionServer, Router

router = Router()

# Define a route that returns a JSON response
@router.route("/api/hello")
def hello_handler(request):
    return {"message": "Hello, World!"}


## Installation

You can install Areion via pip:

```bash
pip install areion
```

## Usage Example

### Simple Usage

```python
from areion import AreionServer, Router, Logger, Orchestrator

# Dictionaries are automatically returned as JSON responses
def home_handler(request):
    return {"msg": "Hello from Areion Server"}

router = Router()
router.add_route("/", home_handler)

orchestrator = DefaultOrchestrator(max_workers=3)

# Build the server with whatever components you want. Only the router is required.
server = AreionServer()
            .with_orchestrator(Orchestrator())
            .with_router(Router())
            .with_port(8000)

# Start the server (also starts the orchestrator and background tasks)
server.start()
```

### Minimalist Usage

```python
from areion import AreionServer

server = AreionServer()

server.start()
```

## Documentation

[COMING SOON]

## License

MIT License

Copyright (c) 2024 Joshua Caponigro

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
