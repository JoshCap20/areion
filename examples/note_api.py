from areion import (
    AreionServerBuilder,
    DefaultRouter,
    HttpRequest,
    HttpResponse,
    create_json_response
)
import uuid

# In-memory storage for notes
notes = {}

# Initialize the router
router = DefaultRouter()

@router.route("/notes", methods=["POST"])
def create_note(request: HttpRequest):
    """
    Handles the creation of a new note from an HTTP request.

    Args:
        title (str): The title of the note.
        content (str): The content of the note.

    Returns:
        HttpResponse: A response object with status code 201 and the created note in JSON format if successful.
                      Returns a response with status code 400 and an error message if the title or content is missing.
    """
    data = request.get_parsed_body()
    if not data or 'title' not in data or 'content' not in data:
        return HttpResponse(
            status_code=400,
            body="Title and content are required.",
            content_type="text/plain"
        )

    note_id = str(uuid.uuid4())
    note = {
        'id': note_id,
        'title': data['title'],
        'content': data['content']
    }
    notes[note_id] = note
    return HttpResponse(
        status_code=201,
        body=note,
        content_type="application/json"
    )
    
@router.route("/notes/:note_id", methods=["GET"])
def get_note(request: HttpRequest, note_id: str):
    """
    Handles GET requests to retrieve a note by its ID.

    Args:
        note_id (str): The ID of the note to retrieve.

    Returns:
        HttpResponse: A response object containing the note data in JSON format if found,
                    otherwise a 404 response with a "Note not found." message.
    """
    note = notes.get(note_id)
    if note is None:
        return HttpResponse(
            status_code=404,
            body="Note not found.",
            content_type="text/plain"
        )
    return create_json_response(note)

@router.route("/notes/:note_id", methods=["PUT"])
def update_note(request: HttpRequest, note_id: int):
    """
    Update an existing note with new data provided in the request.

    Args:
        title (str): The new title of the note.
        content (str): The new content of the note.

    Returns:
        HttpResponse: A response object indicating the result of the update operation.
            - 404 status code if the note is not found.
            - 400 status code if no data is provided in the request.
            - 200 status code with the updated note in JSON format if the update is successful.
    """
    note = notes.get(note_id)
    if note is None:
        return HttpResponse(
            status_code=404,
            body="Note not found.",
            content_type="text/plain"
        )

    data = request.get_parsed_body()
    if not data:
        return HttpResponse(
            status_code=400,
            body="No data provided.",
            content_type="text/plain"
        )

    note.update({
        'title': data.get('title', note['title']),
        'content': data.get('content', note['content'])
    })
    notes[note_id] = note
    return create_json_response(note)

@router.route("/notes/:note_id", methods=["DELETE"])
def delete_note(request: HttpRequest, note_id):
    """
    Deletes a note with the given note_id.

    Args:
        note_id (str): The ID of the note to be deleted.

    Returns:
        HttpResponse: A response with status code 204 if the note was successfully deleted.
                    A response with status code 404 if the note was not found.
    """
    note = notes.pop(note_id, None)
    if note is None:
        return HttpResponse(
            status_code=404,
            body="Note not found.",
            content_type="text/plain"
        )
    return HttpResponse(status_code=204)

# Build and run the server
server = (
    AreionServerBuilder()
    .with_router(router)
    .with_development_mode(True)  # Enables Swagger UI and OpenAPI routes
    .build()
)

if __name__ == "__main__":
    server.run()


