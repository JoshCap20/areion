from ..core.response import HttpResponse, HTTP_STATUS_CODES
import mimetypes
import os

"""
Wrappers for creating common HTTP responses.
**Not converted to bytes or formatted until server sends response.**

TODO: Should we pass strict http flag here to enforce status code ranges?
"""


def create_file_response(file_path: str, status_code: int = 200) -> HttpResponse:
    if not os.path.isfile(file_path):
        return create_error_response(404, "File Not Found")

    try:
        with open(file_path, "rb") as f:
            content = f.read()
    except IOError:
        return create_error_response(500, "Internal Server Error: Cannot read file.")

    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "application/octet-stream"

    filename = os.path.basename(file_path)
    content_disposition = f'attachment; filename="{filename}"'

    response = HttpResponse(
        status_code=status_code,
        body=content,
        content_type=mime_type,
    )
    response.set_header("Content-Disposition", content_disposition)
    return response


def create_redirect_response(location: str, status_code: int = 301) -> HttpResponse:
    if status_code < 300 or status_code >= 400:
        raise ValueError("Invalid redirect status code: must be in the 3xx range.")

    response = HttpResponse(
        status_code=status_code,
        body=HTTP_STATUS_CODES[status_code],
        content_type="text/plain",
    )
    response.set_header("Location", location)
    return response


def create_json_response(data: dict, status_code: int = 200) -> HttpResponse:
    response = HttpResponse(
        status_code=status_code,
        body=data,
        content_type="application/json",
    )
    return response


def create_html_response(html: str, status_code: int = 200) -> HttpResponse:
    response = HttpResponse(
        status_code=status_code,
        body=html,
        content_type="text/html",
    )
    return response


def create_text_response(text: str, status_code: int = 200) -> HttpResponse:
    response = HttpResponse(
        status_code=status_code,
        body=text,
        content_type="text/plain",
    )
    return response


def create_xml_response(data: str, status_code: int = 200) -> HttpResponse:
    response = HttpResponse(
        status_code=status_code,
        body=data,
        content_type="application/xml",
    )
    return response


def create_empty_response(status_code: int = 204, headers: dict = None) -> HttpResponse:
    response = HttpResponse(
        status_code=status_code,
        body=b"",
        content_type="text/plain",
    )
    if headers:
        for key, value in headers.items():
            response.set_header(key, value)
    return response


def create_error_response(status_code: int, message: str = None, headers: dict = None) -> HttpResponse:
    if status_code < 400 or status_code >= 600:
        raise ValueError("Invalid error status code: must be in the 4xx or 5xx range.")

    response = HttpResponse(
        status_code=status_code,
        body=message or HTTP_STATUS_CODES[status_code],
        content_type="text/plain",
        headers=headers,
    )
    return response
