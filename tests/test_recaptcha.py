from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.services.recaptcha import verify_recaptcha


@pytest.mark.asyncio
async def test_verify_recaptcha_skips_when_no_secret_configured():
    # settings.recaptcha_secret_key is "" by default (no .env override in
    # tests) -- should return without making any network call.
    await verify_recaptcha("whatever-token")


def _mock_response(json_body: dict) -> AsyncMock:
    response = httpx.Response(200, json=json_body, request=httpx.Request("POST", "http://x"))
    return response


@pytest.mark.asyncio
async def test_verify_recaptcha_accepts_good_score():
    with (
        patch("app.services.recaptcha.get_settings") as mock_settings,
        patch.object(
            httpx.AsyncClient,
            "post",
            new=AsyncMock(return_value=_mock_response({"success": True, "score": 0.9})),
        ),
    ):
        mock_settings.return_value.recaptcha_secret_key = "fake-key"
        mock_settings.return_value.recaptcha_min_score = 0.5
        await verify_recaptcha("good-token")


@pytest.mark.asyncio
async def test_verify_recaptcha_rejects_low_score():
    with (
        patch("app.services.recaptcha.get_settings") as mock_settings,
        patch.object(
            httpx.AsyncClient,
            "post",
            new=AsyncMock(return_value=_mock_response({"success": True, "score": 0.1})),
        ),
    ):
        mock_settings.return_value.recaptcha_secret_key = "fake-key"
        mock_settings.return_value.recaptcha_min_score = 0.5
        with pytest.raises(HTTPException) as exc_info:
            await verify_recaptcha("bot-token")
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_verify_recaptcha_rejects_unsuccessful_response():
    with (
        patch("app.services.recaptcha.get_settings") as mock_settings,
        patch.object(
            httpx.AsyncClient,
            "post",
            new=AsyncMock(return_value=_mock_response({"success": False})),
        ),
    ):
        mock_settings.return_value.recaptcha_secret_key = "fake-key"
        mock_settings.return_value.recaptcha_min_score = 0.5
        with pytest.raises(HTTPException) as exc_info:
            await verify_recaptcha("invalid-token")
        assert exc_info.value.status_code == 400
