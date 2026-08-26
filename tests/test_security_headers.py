import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from app.core.security_headers import SecurityHeadersMiddleware
from app.main import app


def _make_test_app(*, hsts_enabled: bool) -> Starlette:
    async def endpoint(request):
        return PlainTextResponse("ok")

    test_app = Starlette(routes=[Route("/probe", endpoint)])
    test_app.add_middleware(SecurityHeadersMiddleware, hsts_enabled=hsts_enabled)
    return test_app


@pytest.mark.asyncio
async def test_common_headers_always_present():
    test_app = _make_test_app(hsts_enabled=False)
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as http:
        response = await http.get("/probe")

    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


@pytest.mark.asyncio
async def test_hsts_only_sent_when_enabled():
    disabled_app = _make_test_app(hsts_enabled=False)
    enabled_app = _make_test_app(hsts_enabled=True)

    async with AsyncClient(
        transport=ASGITransport(app=disabled_app), base_url="http://test"
    ) as http:
        disabled_response = await http.get("/probe")
    async with AsyncClient(
        transport=ASGITransport(app=enabled_app), base_url="http://test"
    ) as http:
        enabled_response = await http.get("/probe")

    assert "Strict-Transport-Security" not in disabled_response.headers
    assert enabled_response.headers["Strict-Transport-Security"] == (
        "max-age=63072000; includeSubDomains"
    )


@pytest.mark.asyncio
async def test_api_routes_get_locked_down_csp():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as http:
        response = await http.get("/health")

    assert response.headers["Content-Security-Policy"] == (
        "default-src 'none'; frame-ancestors 'none'"
    )


@pytest.mark.asyncio
async def test_admin_routes_get_permissive_same_origin_csp():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as http:
        response = await http.get("/admin/login")

    csp = response.headers["Content-Security-Policy"]
    assert csp.startswith("default-src 'self'")
    assert "frame-ancestors 'none'" in csp
