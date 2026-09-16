import asyncio
import io
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from botocore.handlers import add_expect_header
from loguru import logger
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings

ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png"}
ALLOWED_CONTENT_TYPES = ALLOWED_IMAGE_CONTENT_TYPES | {"application/pdf"}
# 7.6: differentiated caps -- a headshot photo has no reason to approach the
# logo/ticket-PDF ceiling. MAX_UPLOAD_BYTES stays the default for callers
# that don't pass max_bytes explicitly (partner logos, ticket PDFs, 4.10).
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 Mo
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 Mo
MAX_IMAGE_DIMENSION = 1920


class UploadRejectedError(ValueError):
    pass


class StorageUnavailableError(RuntimeError):
    """Raised when the storage backend (B2 or disk) call itself fails --
    misconfiguration or an outage, not something the uploader did wrong."""


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


def _optimize_image(content: bytes, content_type: str) -> bytes:
    """Downscale + re-encode an image before it leaves for object storage.

    Keeps the original format (no PNG->JPEG conversion, would break
    transparency and the extension in _generate_key). Skips images already
    within MAX_IMAGE_DIMENSION -- never upscale.
    """
    with Image.open(io.BytesIO(content)) as image:
        if max(image.size) <= MAX_IMAGE_DIMENSION:
            return content
        image = image.copy()
        image.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)
        buffer = io.BytesIO()
        if content_type == "image/jpeg":
            image = image.convert("RGB")
            image.save(buffer, format="JPEG", quality=85, optimize=True, progressive=True)
        else:
            image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()


def _s3_client(endpoint_url: str, key_id: str, secret_key: str):
    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
    )
    # B2 (and some other S3-compatible backends) reset the connection instead
    # of replying to an Expect: 100-continue handshake, which botocore sends
    # by default for any streaming PutObject body -- surfaces as a
    # ConnectionClosedError with no useful detail. Harmless to strip for
    # MinIO too.
    client.meta.events.unregister("before-call.s3", add_expect_header)
    return client


def _client():
    """Resolve a client for the active object-storage backend (B2 or MinIO).

    Sole patch point for tests (monkeypatch "app.services.storage._client")
    -- kept as a no-arg function, as it was before MinIO support was added,
    so existing tests didn't need to change. getattr() defaults to "b2" for
    any settings stub that predates the storage_backend field entirely.
    """
    settings = get_settings()
    if getattr(settings, "storage_backend", "b2") == "minio":
        return _s3_client(
            settings.minio_endpoint_url, settings.minio_access_key, settings.minio_secret_key
        )
    return _s3_client(settings.b2_endpoint_url, settings.b2_key_id, settings.b2_application_key)


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
        logger.bind(channel="security").warning(
            f"Upload rejeté : type de fichier non autorisé ({content_type})"
        )
        raise UploadRejectedError(f"Type de fichier non autorisé : {content_type}.")
    if len(content) > max_bytes:
        logger.bind(channel="security").warning(
            f"Upload rejeté : fichier trop volumineux ({len(content)} octets, max {max_bytes})"
        )
        raise UploadRejectedError(f"Fichier trop volumineux (max {max_bytes // (1024 * 1024)} Mo).")
    if content_type in ALLOWED_IMAGE_CONTENT_TYPES:
        try:
            validate_is_real_image(content)
        except UploadRejectedError:
            logger.bind(channel="security").warning(
                "Upload rejeté : contenu non identifiable comme image valide"
            )
            raise
        content = _optimize_image(content, content_type)

    settings = get_settings()
    backend = getattr(settings, "storage_backend", "b2")
    key = _generate_key(original_filename)

    if backend == "local":
        return await _upload_local(content, key, settings)

    if backend == "minio":
        bucket = settings.minio_bucket_name
        public_url = settings.minio_public_url
    else:
        bucket = settings.b2_bucket_name
        public_url = settings.b2_public_url

    def _put() -> None:
        _client().put_object(Bucket=bucket, Key=key, Body=content, ContentType=content_type)

    try:
        await asyncio.to_thread(_put)
    except (BotoCoreError, ClientError) as exc:
        logger.bind(channel="storage").error(f"Échec de l'upload vers le stockage objet : {exc}")
        raise StorageUnavailableError(
            "Le service de stockage est momentanément indisponible."
        ) from exc
    if backend == "minio":
        return f"{public_url}/{bucket}/{key}"
    return f"{public_url}/{key}"


async def _upload_local(content: bytes, key: str, settings) -> str:
    """Dev/no-budget fallback: write to disk instead of B2, served back by
    the /uploads static mount in app/main.py (see STORAGE_BACKEND setting)."""

    def _write() -> None:
        target = Path(settings.local_upload_dir) / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    try:
        await asyncio.to_thread(_write)
    except OSError as exc:
        logger.bind(channel="storage").error(f"Échec de l'écriture du fichier local : {exc}")
        raise StorageUnavailableError(
            "Le service de stockage est momentanément indisponible."
        ) from exc
    return f"{settings.local_public_base_url}/uploads/{key}"


def _public_read_policy(bucket: str) -> str:
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
    )


async def ensure_minio_bucket_ready(*, attempts: int = 5, delay_seconds: float = 2.0) -> None:
    """Create the MinIO bucket if missing and make it world-readable.

    Called once from app/main.py's lifespan when STORAGE_BACKEND=minio --
    MinIO isn't guaranteed to already accept connections right after its
    container starts (no `depends_on: condition: service_healthy` wait is
    assumed here), so this retries a few times rather than failing startup
    on a race. A no-op once the bucket already exists with the right policy.
    """
    settings = get_settings()
    if settings.storage_backend != "minio":
        return

    client = _s3_client(
        settings.minio_endpoint_url, settings.minio_access_key, settings.minio_secret_key
    )
    bucket = settings.minio_bucket_name

    def _setup() -> None:
        try:
            client.create_bucket(Bucket=bucket)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                raise
        client.put_bucket_policy(Bucket=bucket, Policy=_public_read_policy(bucket))

    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            await asyncio.to_thread(_setup)
            logger.bind(channel="storage").info(f"Bucket MinIO '{bucket}' prêt (lecture publique).")
            return
        except (BotoCoreError, ClientError) as exc:
            last_exc = exc
            if attempt < attempts:
                await asyncio.sleep(delay_seconds)
    logger.bind(channel="storage").error(
        f"Échec de préparation du bucket MinIO '{bucket}' après {attempts} tentatives : {last_exc}"
    )
