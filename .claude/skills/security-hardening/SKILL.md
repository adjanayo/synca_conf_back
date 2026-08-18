---
name: security-hardening
description: Use whenever code touches authentication, passwords, customer access codes, RBAC, customer PII, payment proof validation, network/port exposure, or infra secrets — Casbin policy/model changes, password hashing/complexity/lockout rules, Fernet/pgcrypto encryption, payment-proof anti-fraud checks, JWT handling, or Traefik/ModSecurity/Docker-secrets/port config. Trigger on any change touching customer records, login/password logic, payment or order-lookup code, auth routes, or secrets/WAF/port config.
---

# Security Hardening

Security is layered: don't treat any single layer as sufficient — each exists because a single layer has failed in comparable systems before.

## RBAC

- New protected actions get a policy rule, not an inline `if role == "owner"` check scattered in a route — the enforcer is the single source of truth.
- When adding a new role-gated action, write the negative test first: assert the role one level below is denied, then assert the intended role is allowed.

## PII

- Customer PII (name, phone, address) is encrypted at the application layer before write, pgcrypto at the database layer. Any new PII field follows the same pattern — don't add a plaintext column because "it's just a phone number."
- Verify by inspecting the raw DB row, not just the API response.

## Auth

- JWTs carry `tenant_id` + `role`. A route is only "protected" once it goes through the full `get_current_user` → tenant-context → RBAC chain.
- A tenant with `status != "active"` must be locked out of its entire dashboard.

### API docs are never publicly readable

`/docs`, `/redoc`, and `/openapi.json` are disabled whenever `ENVIRONMENT != "local"`. Phase 3.2 upgrades this to gated: re-enable in production, but wrap behind `require_role(SuperAdmin)` — not Owner, not Manager.

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

- Secrets go into Docker Swarm secrets in production — never into plain env vars or committed `.env` files.
- **Only Traefik is internet-facing in production** — backend API included. Postgres/Redis/MinIO must never be reachable from outside.

## When reviewing a change

Ask: (1) does this cross a tenant boundary without `SET LOCAL app.current_tenant`? (2) does this write PII without encryption? (3) does this touch a payment proof without the DB-level uniqueness check? (4) does this add a new role-gated action without a policy entry? (5) does this create/check a password without Argon2id + complexity + lockout? (6) does production compose publish a port for anything other than Traefik? A "yes" to any blocks the change.
