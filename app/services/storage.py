import asyncio
import io
import uuid
from datetime import UTC, datetime
from pathlib import PurePosixPath

import boto3
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings

ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png"}
ALLOWED_CONTENT_TYPES = ALLOWED_IMAGE_CONTENT_TYPES | {"application/pdf"}
# 7.6: differentiated caps -- a headshot photo has no reason to approach the
# logo/ticket-PDF ceiling. MAX_UPLOAD_BYTES stays the default for callers
# that don't pass max_bytes explicitly (partner logos, ticket PDFs, 4.10).
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 Mo
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 Mo


class UploadRejectedError(ValueError):
    pass


def validate_is_real_image(content: bytes) -> None:
    """Reject anything whose bytes aren't actually a decodable image.

    A client-supplied Content-Type header is not proof of file content
    (e.g. a renamed .exe served as "image/jpeg") -- Pillow has to open and
    verify the pixel data itself (schema.md 4.3: "MIME réel + Pillow").
    """
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
    except UnidentifiedImageError as exc:
        raise UploadRejectedError("Le fichier n'est pas une image valide.") from exc


def _client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.b2_endpoint_url,
        aws_access_key_id=settings.b2_key_id,
        aws_secret_access_key=settings.b2_application_key,
    )


def _generate_key(original_filename: str) -> str:
    # Never the original filename -- UUID + timestamp only (4.10).
    suffix = PurePosixPath(original_filename).suffix.lower()
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{uuid.uuid4().hex}{suffix}"


async def upload_file(
    content: bytes,
    original_filename: str,
    content_type: str,
    *,
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise UploadRejectedError(f"Type de fichier non autorisé : {content_type}.")
    if len(content) > max_bytes:
        raise UploadRejectedError(f"Fichier trop volumineux (max {max_bytes // (1024 * 1024)} Mo).")
    if content_type in ALLOWED_IMAGE_CONTENT_TYPES:
        validate_is_real_image(content)

    settings = get_settings()
    key = _generate_key(original_filename)

    def _put() -> None:
        _client().put_object(
            Bucket=settings.b2_bucket_name, Key=key, Body=content, ContentType=content_type
        )

    await asyncio.to_thread(_put)
    return f"{settings.b2_public_url}/{key}"
