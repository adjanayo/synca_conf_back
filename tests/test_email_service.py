from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.email_service import send_email


@pytest.mark.asyncio
async def test_send_email_logs_in_dev_without_key(caplog):
    # No RESEND_API_KEY configured by default -- should log, not send.
    await send_email("test@example.com", "Sujet", "Corps du message.")


def _mock_response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code, request=httpx.Request("POST", "http://x"))


@pytest.mark.asyncio
async def test_send_email_calls_resend_when_key_configured():
    with (
        patch("app.services.email_service.get_settings") as mock_settings,
        patch.object(
            httpx.AsyncClient, "post", new=AsyncMock(return_value=_mock_response(200))
        ) as mock_post,
    ):
        mock_settings.return_value.resend_api_key = "fake-key"
        mock_settings.return_value.resend_from_email = "no-reply@synca.conf"

        await send_email("test@example.com", "Sujet", "Corps.")

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["to"] == ["test@example.com"]
        assert call_kwargs["json"]["subject"] == "Sujet"


@pytest.mark.asyncio
async def test_send_email_raises_on_resend_error():
    with (
        patch("app.services.email_service.get_settings") as mock_settings,
        patch.object(
            httpx.AsyncClient, "post", new=AsyncMock(return_value=_mock_response(500))
        ),
    ):
        mock_settings.return_value.resend_api_key = "fake-key"
        mock_settings.return_value.resend_from_email = "no-reply@synca.conf"

        with pytest.raises(httpx.HTTPStatusError):
            await send_email("test@example.com", "Sujet", "Corps.")
