from ..core.response import HttpResponse, HTTP_STATUS_CODES
import mimetypes
import os

"""
Wrappers for creating common HTTP responses.
**Not converted to bytes or formatted until server sends response.**

TODO: Should we pass strict http flag here to enforce status code ranges?
"""


def create_file_response(file_path: str, status_code: int = 200) -> HttpResponse:
    """
    Creates an HTTP response for serving a file.

    Args:
        file_path (str): The path to the file to be served.
        status_code (int, optional): The HTTP status code for the response. Defaults to 200.

    Returns:
        HttpResponse: An HTTP response object containing the file content or an error response if the file cannot be read.

    Raises:
        IOError: If there is an error reading the file.

    Notes:
        - If the file does not exist, a 404 error response is returned.
        - If there is an internal server error while reading the file, a 500 error response is returned.
        - The MIME type of the file is guessed based on the file extension. If it cannot be determined, it defaults to "application/octet-stream".
        - The response includes a "Content-Disposition" header to prompt the user to download the file with the original filename.
    """
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
    """
    Creates an HTTP redirect response.

    Args:
        location (str): The URL to which the client is redirected.
        status_code (int, optional): The HTTP status code for the redirect.
                                     Must be in the 3xx range. Defaults to 301.

    Returns:
        HttpResponse: The HTTP response object with the redirect status and location.

    Raises:
        ValueError: If the status_code is not in the 3xx range.
    """
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
    """
    Creates an HTTP JSON response with the given data and status code.

    Args:
        data (dict): The data to be included in the JSON response body.
        status_code (int, optional): The HTTP status code for the response. Defaults to 200.

    Returns:
        HttpResponse: An HTTP response object with the specified JSON data and status code.
    """
    response = HttpResponse(
        status_code=status_code,
        body=data,
        content_type="application/json",
    )
    return response


def create_html_response(html: str, status_code: int = 200) -> HttpResponse:
    """
    Creates an HTTP response with the given HTML content and status code.

    Args:
        html (str): The HTML content to include in the response body.
        status_code (int, optional): The HTTP status code for the response. Defaults to 200.

    Returns:
        HttpResponse: An HTTP response object containing the specified HTML content and status code.
    """
    response = HttpResponse(
        status_code=status_code,
        body=html,
        content_type="text/html",
    )
    return response


def create_text_response(text: str, status_code: int = 200) -> HttpResponse:
    """
    Creates an HTTP response with plain text content.

    Args:
        text (str): The text content to include in the response body.
        status_code (int, optional): The HTTP status code for the response. Defaults to 200.

    Returns:
        HttpResponse: An HTTP response object with the specified text content and status code.
    """
    response = HttpResponse(
        status_code=status_code,
        body=text,
        content_type="text/plain",
    )
    return response


def create_xml_response(data: str, status_code: int = 200) -> HttpResponse:
    """
    Creates an HTTP response with XML content.

    Args:
        data (str): The XML data to include in the response body.
        status_code (int, optional): The HTTP status code for the response. Defaults to 200.

    Returns:
        HttpResponse: An HTTP response object with the specified XML data and status code.
    """
    response = HttpResponse(
        status_code=status_code,
        body=data,
        content_type="application/xml",
    )
    return response


def create_empty_response(status_code: int = 204, headers: dict = None) -> HttpResponse:
    """
    Creates an empty HTTP response with the specified status code and headers.

    Args:
        status_code (int, optional): The HTTP status code for the response. Defaults to 204.
        headers (dict, optional): A dictionary of headers to set in the response. Defaults to None.

    Returns:
        HttpResponse: An HTTP response object with the specified status code and headers.
    """
    response = HttpResponse(
        status_code=status_code,
        body=b"",
        content_type="text/plain",
    )
    if headers:
        for key, value in headers.items():
            response.set_header(key, value)
    return response


def create_error_response(
    status_code: int, message: str = None, headers: dict = None
) -> HttpResponse:
    """
    Creates an HTTP error response with the given status code, message, and headers.

    Args:
        status_code (int): The HTTP status code for the error response. Must be in the 4xx or 5xx range.
        message (str, optional): The error message to include in the response body. Defaults to the standard message for the given status code.
        headers (dict, optional): Additional headers to include in the response. Defaults to None.

    Returns:
        HttpResponse: An HTTP response object with the specified error status code, message, and headers.

    Raises:
        ValueError: If the status code is not in the 4xx or 5xx range.
    """
    if status_code < 400 or status_code >= 600:
        raise ValueError("Invalid error status code: must be in the 4xx or 5xx range.")

    response = HttpResponse(
        status_code=status_code,
        body=message or HTTP_STATUS_CODES[status_code],
        content_type="text/plain",
        headers=headers,
    )
    return response
