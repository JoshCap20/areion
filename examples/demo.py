from areion import (
    AreionServerBuilder,
    DefaultRouter,
    HttpRequest,
    HttpResponse,
    create_redirect_response,
    create_text_response,
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


@router.route("/plaintext", methods=["GET", "POST"])
async def text_response(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        print(request.body)
        return create_text_response("Hello, World!")
    return HttpResponse(
        status_code=200,
        body="Hello, World!",
        content_type="text/plain",
    )


@router.route("/redirect")
def redirect_response(request: HttpRequest):
    return create_redirect_response(location="/json")


router.add_route(
    "/json-lambda", lambda _: create_json_response({"message": "Hello, World!"})
)

server = AreionServerBuilder().with_port(8000).with_router(router).build()

if __name__ == "__main__":
    server.run()
