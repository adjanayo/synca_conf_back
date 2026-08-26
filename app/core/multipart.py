import types
import typing

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, ValidationError
from starlette.datastructures import UploadFile as StarletteUploadFile


def _is_list_annotation(annotation: object) -> bool:
    origin = typing.get_origin(annotation)
    if origin is list:
        return True
    if origin in (typing.Union, types.UnionType):
        return any(_is_list_annotation(arg) for arg in typing.get_args(annotation))
    return False


async def parse_multipart_form(request: Request, model: type[BaseModel]) -> BaseModel:
    """Validate a multipart form's non-file fields against a Pydantic model.

    Works around a FastAPI 0.141.1 limitation: combining
    `Annotated[Model, Form()]` with a `File(...)` parameter in the same
    route signature breaks form-field flattening (both end up nested under
    a literal "body" key instead of the individual field names). Parsing
    the form directly avoids that bug.

    A field typed as a list (e.g. `objectives: list[str]`) is always read
    with `getlist()`, even when the client sends exactly one value for it
    -- otherwise a single-item list is indistinguishable from a plain
    scalar field on the wire, and Pydantic won't auto-wrap a bare string
    into a one-item list.
    """
    form = await request.form()
    data: dict[str, str | list[str]] = {}

    for field_name, field_info in model.model_fields.items():
        if field_name not in form:
            continue
        if _is_list_annotation(field_info.annotation):
            data[field_name] = form.getlist(field_name)
            continue
        value = form[field_name]
        if not isinstance(value, StarletteUploadFile):
            data[field_name] = value

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
