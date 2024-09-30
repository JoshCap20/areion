import asyncio
from areion import DefaultRouter, HttpResponse, AreionServerBuilder, DefaultLogger

# Initialize the logger
logger = DefaultLogger()

# Create the router
router = DefaultRouter()

@router.route("/log", methods=["GET"])
async def some_handler(request):
    # Await the logger.info call since it's asynchronous
    await logger.info("Processing request")
    return HttpResponse(body="Response", status_code=200, headers={"Content-Type": "text/plain"})

# Create the server with the router and logger
server = AreionServerBuilder().with_router(router).with_logger(logger).build()

async def main():
    # Log the starting message asynchronously
    await logger.info(f"Starting server on {server.host}:{server.port}")
    
    # Run the server; the Areion server manages its own event loop
    await server.start()  # Assuming there is a method to start the server asynchronously

    # This line won't be reached until the server is stopped
    await logger.shutdown()  # Shutdown logger after the server stops

# Main entry point
if __name__ == "__main__":
    asyncio.run(main())
