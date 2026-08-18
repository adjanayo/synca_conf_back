---
name: error-handling
description: Use whenever raising, returning, or rendering an error anywhere — a FastAPI HTTPException, a Pydantic validation failure, or how an error message displays to the user. Trigger on "what status code," "how should this error look," "the error isn't showing," "add validation," or when building any new form/endpoint that can fail.
---

# Error Handling

**A correctly-firing error nobody can see is exactly as broken as no error.** Both halves — what the API returns, and how the frontend shows it — matter equally.

## Backend: API error contract

| Status | When | Shape |
|---|---|---|
| `400` | Malformed/semantically invalid input | `HTTPException(400, detail="human-readable message")` |
| `401` | No/invalid credentials | `HTTPException(401, detail="...")` |
| `403` | Authenticated but not permitted | `HTTPException(403, detail="...")` |
| `404` | Resource doesn't exist | `HTTPException(404, detail="...")` |
| `409` | Conflicts with existing state | `HTTPException(409, detail="...")` |
| `422` | Pydantic validation failure | FastAPI's default array shape |
| `500` | Unexpected/unhandled | Generic message only — never leak internals |

- **`detail` is a plain string** for every hand-raised `HTTPException` — complete, human-readable sentence.
- **`422` responses have array shape**: `{"detail": [{"loc": [...], "msg": "...", "type": "..."}, ...]}`. Frontend must handle both shapes.
- **Never leak internals** — log server-side, return generic for 500s.

## Frontend: rendering errors

- **Every error must be visually distinct** — color, border, or icon, never plain unstyled text.
- **Parse both `detail` shapes** — string or array of validation errors.
- **Loading state**: disable submit control and change label while pending.
