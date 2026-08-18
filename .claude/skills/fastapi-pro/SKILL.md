---
name: fastapi-pro
description: Use whenever writing, reviewing, or debugging FastAPI backend code — async route handlers, DB session dependencies, background jobs, RBAC dependency wiring, or Pydantic schemas. Trigger on any backend/app work, new API endpoint, async DB query, or background task, even if the user just says "add an endpoint" or "why is this route slow."
---

# FastAPI Pro

## Request lifecycle

- Every route is `async def`. No sync DB calls, no blocking I/O in a request handler — if something is inherently blocking (PDF generation, email send), it belongs in a background job, not inline in the route.
- DB access goes through a session dependency that resolves tenant context and issues `SET LOCAL app.current_tenant` before any query runs. Never construct a raw session that skips this.
- Auth: `get_current_user` resolves identity + tenant + RBAC permission in one dependency chain. New protected routes declare their required permission via this chain rather than hand-rolling role checks in the handler body.

## Conventions

- Config via `app/core/config.py` (pydantic settings), never hardcoded connection strings or secrets in route/service code.
- Structured JSON logging — use it for anything worth debugging later, not `print()`.
- Use `app/core/exceptions.py` custom exceptions with proper HTTP status codes.
- Pydantic v2 for all schemas — `model_config = ConfigDict(...)` not `class Config`.

## Testing

- `pytest` + `pytest-asyncio` for unit/integration tests under `tests/`, mirroring the `app/` structure.
- Tenant-isolation changes get a dedicated test that opens two sessions with different `app.current_tenant` values and asserts cross-tenant reads return nothing.
- Run the relevant test file after any change: `rtk pytest tests/<path> -v` before considering a step done.

## Error handling

- `detail` is a plain string for every `HTTPException` — human-readable, may be shown to the user.
- `422` responses have array shape from Pydantic: `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`.
- Never leak internals to the client — log server-side, return generic message for 500s.
