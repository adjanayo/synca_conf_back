import io
from unittest.mock import MagicMock

import pytest
from PIL import Image

from app.services.storage import (
    MAX_UPLOAD_BYTES,
    UploadRejectedError,
    upload_file,
    validate_is_real_image,
)


def make_png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buffer, format="PNG")
    return buffer.getvalue()


def test_validate_is_real_image_accepts_real_image():
    validate_is_real_image(make_png_bytes())  # should not raise


def test_validate_is_real_image_rejects_fake_image():
    with pytest.raises(UploadRejectedError):
        validate_is_real_image(b"not-actually-an-image-just-text")


@pytest.mark.asyncio
async def test_upload_file_rejects_disallowed_content_type():
    with pytest.raises(UploadRejectedError):
        await upload_file(make_png_bytes(), "photo.png", "application/pdf")


@pytest.mark.asyncio
async def test_upload_file_rejects_oversized_file():
    oversized = b"0" * (MAX_UPLOAD_BYTES + 1)
    with pytest.raises(UploadRejectedError):
        await upload_file(oversized, "photo.png", "image/png")


@pytest.mark.asyncio
async def test_upload_file_rejects_fake_image_bytes():
    with pytest.raises(UploadRejectedError):
        await upload_file(b"fake-bytes-not-a-real-image", "photo.png", "image/png")


@pytest.mark.asyncio
async def test_upload_file_success_never_uses_original_filename(monkeypatch):
    mock_client = MagicMock()
    monkeypatch.setattr("app.services.storage._client", lambda: mock_client)
    monkeypatch.setattr(
        "app.services.storage.get_settings",
        lambda: type(
            "S", (), {"b2_bucket_name": "test-bucket", "b2_public_url": "https://cdn.example.com"}
        )(),
    )

    url = await upload_file(make_png_bytes(), "ma-photo-secrete.png", "image/png")

    mock_client.put_object.assert_called_once()
    call_kwargs = mock_client.put_object.call_args.kwargs
    assert call_kwargs["Bucket"] == "test-bucket"
    assert "ma-photo-secrete" not in call_kwargs["Key"]
    assert call_kwargs["Key"].endswith(".png")
    assert url.startswith("https://cdn.example.com/")
    assert "ma-photo-secrete" not in url
