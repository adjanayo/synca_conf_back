---
name: security-hardening
description: Use whenever code touches authentication, passwords, RBAC, registrant/participant PII, payment webhook validation, network/port exposure, or infra secrets — RBAC policy changes, password hashing/complexity/lockout rules, Fernet encryption, payment webhook signature/idempotence checks, JWT handling, or Caddy/Docker-Compose/port config. Trigger on any change touching registrant records, login/password logic, payment or promo-code logic, auth routes, or secrets/port config.
---

# Security Hardening

Security is layered: don't treat any single layer as sufficient — each exists because a single layer has failed in comparable systems before.

## RBAC

- New protected actions get a policy rule, not an inline `if role == "owner"` check scattered in a route — the enforcer is the single source of truth.
- When adding a new role-gated action, write the negative test first: assert the role one level below is denied, then assert the intended role is allowed.

## PII

- Customer/registrant PII (name, phone, address) is encrypted at the application layer (`cryptography.Fernet`) before write where it's genuinely sensitive. Any new PII field follows the same pattern — don't add a plaintext column because "it's just a phone number."
- Verify by inspecting the raw DB row, not just the API response.

## Auth

- JWTs carry `admin_user_id` + `role`. A route is only "protected" once it goes through the full `get_current_user` → RBAC (`require_permission`) chain — this project is mono-tenant, there is no tenant context to thread through.

### API docs are never publicly readable

`/docs`, `/redoc`, and `/openapi.json` are disabled whenever `ENVIRONMENT != "local"` (see `ROADMAP.md` §7.4). If the team needs prod access, gate a non-standard path (`/internal/docs`) behind Caddy Basic Auth — never re-open the default paths publicly.

### Password policy

- **Hash with Argon2id**, not bcrypt or a raw hash.
- **Minimum 12 characters, mixed case + digit + symbol.** Enforce at account creation and password reset, not just frontend.
- **Lock the account for 15 minutes after 5 consecutive failed attempts**, then double on each further failure, capped at 4 hours.
- **No forced periodic rotation** — NIST guidance says it pushes toward weak passwords.
- **Staff accounts start with a system-generated temp password**, forced to set own on first login.

### Customer access codes are bearer credentials

- Generate with cryptographically secure random source, long enough to resist guessing.
- Rate-limit lookup attempts per IP/code.
- Wrong code and expired/nonexistent order return the **identical** generic response.

## Infra

- Secrets live in `.env` on the VPS (never committed, permissions locked down) — no Docker Swarm, this is a single-VPS Docker Compose deployment.
- **Only Caddy is internet-facing in production** — backend API included. MySQL must never be reachable from outside the Compose network (no published port).

## When reviewing a change

Ask: (1) does this write PII without encryption where it's genuinely sensitive? (2) does this touch a payment webhook without signature verification + idempotence? (3) does this add a new role-gated action without a `role_permissions` entry? (4) does this create/check a password without Argon2id + complexity + lockout? (5) does the production compose publish a port for anything other than Caddy? (6) does this touch a `campaign_windows`-gated endpoint without the `require_open_campaign` dependency? A "yes" to any blocks the change.
