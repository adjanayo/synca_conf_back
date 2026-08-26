from fastapi import HTTPException, Request, status
from pydantic import BaseModel, ValidationError
from starlette.datastructures import UploadFile as StarletteUploadFile


async def parse_multipart_form(request: Request, model: type[BaseModel]) -> BaseModel:
    """Validate a multipart form's non-file fields against a Pydantic model.

    Works around a FastAPI 0.141.1 limitation: combining
    `Annotated[Model, Form()]` with a `File(...)` parameter in the same
    route signature breaks form-field flattening (both end up nested under
    a literal "body" key instead of the individual field names). Parsing
    the form directly avoids that bug.
    """
    form = await request.form()
    data: dict[str, str] = {}
    for key in form:
        value = form[key]
        if isinstance(value, StarletteUploadFile):
            continue  # file fields are handled separately by the caller
        data[key] = value

    try:
        return model(**data)
    except ValidationError as exc:
        # exc.errors() can carry non-JSON-serializable "ctx" (e.g. the raw
        # exception from a custom @field_validator) -- strip it, matching
        # FastAPI's own 422 array shape without that risk.
        errors = [{k: v for k, v in error.items() if k != "ctx"} for error in exc.errors()]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=errors
        ) from exc
