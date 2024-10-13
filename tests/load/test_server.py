from areion import (
    AreionServerBuilder,
    DefaultRouter,
    HttpRequest,
    HttpResponse,
    create_json_response,
)

router = DefaultRouter()


@router.route("/json", methods=["GET"])
async def json_response(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        status_code=200,
        body={"message": "Hello, World!"},
        content_type="application/json",
    )


@router.route("/plaintext", methods=["GET"])
async def text_response(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        status_code=200,
        body="Hello, World!",
        content_type="text/plain",
    )


server = AreionServerBuilder().with_router(router).with_port(8080).build()
server.run()
