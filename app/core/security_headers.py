from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# The admin backoffice (SQLAdmin, 6.1) and the API docs (Swagger/Redoc, when
# enabled) are the only same-origin HTML/JS surfaces this API serves -- they
# need inline scripts/styles. Every other route is pure JSON and gets a
# fully locked-down CSP.
_UI_PATH_PREFIXES = ("/admin", "/docs", "/redoc", "/openapi.json")
_UI_CSP = (
    "default-src 'self'; script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "font-src 'self' data:; frame-ancestors 'none'"
)
_API_CSP = "default-src 'none'; frame-ancestors 'none'"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, hsts_enabled: bool) -> None:
        super().__init__(app)
        self._hsts_enabled = hsts_enabled

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        is_ui_route = request.url.path.startswith(_UI_PATH_PREFIXES)
        response.headers["Content-Security-Policy"] = _UI_CSP if is_ui_route else _API_CSP
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS only makes sense once the app is actually served over HTTPS
        # (production, behind Caddy) -- sending it in local/staging over
        # plain HTTP would just be a no-op header, not a real protection.
        if self._hsts_enabled:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains"
            )

        return response
