# Jenby — Security Checklist & Vulnerability Review Process

This file is the concrete "how do we check for vulnerabilities" companion to `ROADMAP.md`. Each category below maps to real Jenby architecture (not generic OWASP boilerplate), names the skill that owns it, and says exactly how to check it — a tool, a command, or a specific test pattern.

**When to run this:** at minimum, before marking any `security-hardening`/`payments-workflow`/`container-security`-tagged `ROADMAP.md` step as tested (see `TESTING.md`), and again as a full pass at the end of each Phase. Amend this file the same way we amend `ROADMAP.md` — if a category turns out to be missing or wrong, fix it here and note why, don't just work around it silently.

---

## Code Review Process

Four tools are already available in this environment. Use the right one for the question being asked — they're not interchangeable:

| Tool | Answers | When to run it |
|---|---|---|
| `sonatype-guide` MCP | "Is this dependency safe to add?" (CVEs, license risk, malicious packages, Developer Trust Score) | **Before** every `pip install`/`npm install`/`uv add` — this is mandatory per that skill's own trigger rule, not optional |
| `semgrep` plugin (SAST + secrets + supply chain) | "Does this code have a known-bad pattern, a hardcoded secret, or a risky dependency graph?" | After implementing any `security-hardening`/`payments-workflow` step, before marking it tested; also reasonable to run periodically across the whole repo once there's real code |
| `code-review` / `security-review` skills | "Is this diff correct, well-scoped, and free of logic bugs a reviewer would catch?" | Before considering any `ROADMAP.md` step's implementation finished — this is the human-equivalent review pass, run it on the diff for that step |
| `claude-security` orchestrator (user-triggered, billed) | Full-repo multi-agent scan with verified findings and generated patches | Not per-step — reserve for a milestone check (e.g., end of a Phase, or before the first real production deploy in Phase 12) |

**Minimum bar for any step touching auth, payments, PII, or containers:** run `security-review` (or `code-review`) on the diff, and if a new dependency was added, confirm `sonatype-guide` was actually consulted (not just "probably fine"). For anything in the checklist below tagged 🔴, that's non-negotiable before `test-tracker` records the step as done.

---

## A. Tenant Isolation

| Check | How |
|---|---|
| 🔴 Every tenant-scoped query goes through the `SET LOCAL app.current_tenant` session dependency | Grep for raw `get_session`/engine usage that bypasses `app/db/session.py`; any hit is a finding |
| 🔴 Cross-tenant reads are structurally impossible, not just filtered in application code | `scripts/verify_tenant_isolation.py` (Phase 1.2) — two sessions, two tenants, assert zero cross-visibility |
| New tables added after Phase 1.2 inherit the same isolation | Check the migration touches the per-tenant schema template, not a shared table without a `tenant_id` discriminator (if a deliberately shared/control table, confirm it's meant to be — e.g. `platform_settings`) |

Owning skill: `saas-architect`, `fastapi-pro`.

## B. Authentication & Session

| Check | How |
|---|---|
| 🔴 Passwords hashed with Argon2id, never a weaker scheme | Inspect `app/security/passwords.py`; grep for `bcrypt`/`md5`/`sha256` used for password storage — any hit is wrong |
| 🔴 New account/password write enforces 12+ chars, mixed case, digit, symbol | `pytest backend/tests/security/test_password_policy.py` — weak password rejected server-side, not just in frontend copy |
| 🔴 Account locks after 5 failed logins for 15 minutes | Same test file — 6th attempt with the *correct* password still fails during lockout |
| Staff accounts created by Owner/SuperAdmin force a password change on first login | Manual: create a staff account, log in with the temp password, confirm redirect to `set-password` before reaching the dashboard |
| JWTs carry `tenant_id` + `role` and are verified on every protected route | `pytest backend/tests/api/test_auth.py` — 401/403/200 matrix |

Owning skill: `security-hardening`, `fastapi-pro`.

## C. Authorization (RBAC)

| Check | How |
|---|---|
| 🔴 Every role-gated action has a Casbin policy entry, not an inline `if role ==` check | Grep route handlers for inline role comparisons outside the `get_current_user`/Casbin chain |
| 🔴 Every new protected action has a negative test (role below is denied) before the positive test | `pytest backend/tests/security/test_casbin_enforcer.py` |
| A tenant with `status != "active"` cannot reach any dashboard route regardless of valid credentials | `pytest backend/tests/api/test_tenant_access_lock.py` |
| **Not yet built — track when it lands:** Step 2.4's admin subscription approve/reject endpoints (deferred to Phase 3.2, see `ROADMAP.md`) must be `require_role(SuperAdmin)`-gated from the moment they're written, including the pending-proofs listing which exposes phone numbers/transaction IDs — no interim unauthenticated version, not even read-only | When Step 2.4/3.2 is implemented, confirm both the list and approve/reject routes return 401/403 without a valid SuperAdmin session before marking either step tested |
| 🔴 Manager's permission set is genuinely smaller than Owner's, not identical (Step 4.5) — staff/location management is Owner-only; Manager retains inventory/CRM/POS write but is location-scoped | Full matrix in [docs/security.md § Permission Matrix](docs/security.md#permission-matrix) — that table is the single source of truth, don't duplicate it here or in code comments |
| 🔴 A Manager/Employee assigned to location A cannot read or write location B's inventory/CRM/sales data, even within their own tenant | `pytest backend/tests/api/test_locations.py` |

Owning skill: `security-hardening`.

## D. PII & Data Protection

| Check | How |
|---|---|
| 🔴 Customer PII (name, phone, address) is Fernet-encrypted at the application layer before write | Inspect raw DB row via `psql` directly (not the API) — ciphertext, not plaintext |
| pgcrypto is also applied at the DB layer (defense in depth) | `pytest backend/tests/security/test_pii_encryption.py` |
| 🔴 CSV export (Phase 9.1) is gated to a role at least as strict as raw CRM reads | Attempt export as Employee, confirm denial; confirm Owner succeeds |
| CSV export never includes payment-proof screenshots or MinIO object references | Inspect exported CSV headers/columns against the documented schema |
| Analytics endpoints (Phase 9.3) are gated to Owner/Manager, never Employee; the SuperAdmin aggregate endpoint reads the `tenant_daily_stats` rollup only, never other tenants' rows directly | Attempt `/analytics` as Employee → denied; attempt a cross-tenant join/query against another tenant's schema → impossible (no cross-schema access path exists in the API) |
| 🔴 Audit log (Phase 9.4) is append-only at the DB layer, not by convention | Attempt `UPDATE`/`DELETE` on an `audit_log` row via `psql` → the trigger rejects it; `pytest backend/tests/api/test_audit.py` asserts the DB raises |

Owning skill: `security-hardening`.

## E. Payment & Order-Access-Code Fraud

Jenby has no payment webhooks — every check here assumes a human-reviewed proof, not a provider callback (`payments-workflow`).

| Check | How |
|---|---|
| 🔴 `(tenant_id, phone, transaction_id)` uniqueness is a real DB constraint, not an application-level `if exists` | Inspect the migration for a `UNIQUE` index; attempt a concurrent duplicate submission in a test and confirm the DB — not application logic — is what rejects the second one |
| 🔴 Rejecting a payment proof releases the reservation **immediately**, never waiting out the 45-minute timer | `pytest backend/tests/services/test_order_payment_validation.py` |
| 🔴 Order access codes (Phase 5.3) are cryptographically random, not derived from order ID or any sequential value | Inspect the generator in `app/services/stock_escrow.py`; a code that's `order_id` base64'd or similar is a finding |
| 🔴 Order lookup (Phase 6.4) rate-limits attempts and returns an identical response for wrong-code vs. expired/nonexistent order | `pytest backend/tests/api/test_order_lookup.py` — diff the response bodies byte-for-byte between the two failure cases |

Owning skill: `payments-workflow`, `security-hardening`.

## F. Injection

| Check | How |
|---|---|
| All DB queries use parameterized queries via the ORM, never string-formatted SQL | `semgrep` SAST pass catches most of this; also grep for `f"SELECT` / `.format(` / `%` near any `execute(` call |
| CSV import (Phase 9.2) doesn't execute formulas from spreadsheet-crafted cells | A cell starting with `=`, `+`, `-`, or `@` is treated as literal text on both import and any re-export, never evaluated — this is "CSV/Excel formula injection," a real and common attack against import features |
| Next.js pages don't render unescaped user input as HTML | Grep for `dangerouslySetInnerHTML` — any use needs explicit justification and sanitization, not a default |
| Email/PDF templates (invoices, notifications) escape user-supplied fields (tenant name, customer name, product names) | Manual: create a product/customer with `<script>` or template-syntax-looking characters in the name, confirm it renders literally in the invoice PDF and email |

Owning skill: `fastapi-pro`, `nextjs-enterprise`, `notifications-workflow`.

## G. Secrets Management

| Check | How |
|---|---|
| 🔴 `.env` is never committed | `git log --all --full-history -- .env` should return nothing; confirmed gitignored |
| Local dev secrets are never reused in production | Fresh secrets generated for Phase 12.3, not copy-pasted from a developer's `.env` |
| Production secrets live in Docker Swarm secrets, not env vars or baked into an image | Inspect `infra/swarm/docker-compose.prod.yml`'s `secrets:` block; `container-security`'s "never bake secrets into a layer" check on the Dockerfiles |
| No secret appears in application logs | Grep `app/core/logging.py` usage sites for anything logging a full request/response body that could contain a password or token |

Owning skill: `security-hardening`, `container-security`.

## H. Network & Infrastructure Exposure

| Check | How |
|---|---|
| 🔴 In production, only Traefik publishes a port (80/443) | Inspect `infra/swarm/docker-compose.prod.yml` (Phase 12.2) — `postgres`, `redis`, `minio` must have no `ports:` key. **This cannot be checked until Phase 12.2 exists** — track it there, don't assume it's already true. |
| Local dev exposing DB/Redis/MinIO ports to `localhost` is intentional, not a leftover to "fix" | `docker-compose.yml` (Phase 1.1) — confirmed acceptable; don't flag this as a finding in local-only review |
| Traefik's ModSecurity WAF rules are actually active, not just present in config | Manual: send a known-bad request pattern (e.g. a SQLi-shaped query string) through local Traefik and confirm it's blocked, once Phase 1.5 lands |
| TLS/auto-SSL is functioning, not falling back to plaintext | `curl -v` against the production endpoint, confirm certificate details once Phase 12 is live |
| 🔴 API docs (`/docs`, `/redoc`, `/openapi.json`) are never publicly readable without authentication | `curl -o /dev/null -w '%{http_code}' https://<prod-host>/docs` — must **not** return 200 for an unauthenticated request. As of Phase 3.2, any `ENVIRONMENT != local` mounts SuperAdmin-gated replacements (`app.main.configure_docs`) — `401` unauthenticated, `403` non-SuperAdmin, `200` SuperAdmin only. Automated: `pytest backend/tests/api/test_docs_gating.py`. |

Owning skill: `deployment-orchestrator`, `security-hardening`.

## I. Container & Image Security

| Check | How |
|---|---|
| 🔴 Base images are version-pinned, not `:latest` | Inspect `backend/Dockerfile` / `frontend/Dockerfile` (Phase 12.1) |
| 🔴 Final image runs as a non-root user | `docker run --rm <image> whoami` — must not print `root` |
| 🔴 No secret in any layer | `docker history <image>` and inspect each layer; also covered by G above |
| 🔴 Built image scanned (Trivy or Grype), no unaddressed critical/high CVEs | Run the scanner against the built image as part of Phase 12.1's verification, and again in CI (Phase 13.1) on every build |
| Multi-stage build — final image has no build-only tooling | `docker run --rm <image> which gcc` (or equivalent) should fail |

Owning skill: `container-security`.

## J. Dependency & Supply Chain

| Check | How |
|---|---|
| 🔴 Every new dependency was checked with `sonatype-guide` before being added | Check the conversation/PR history for evidence the skill was actually invoked, not assumed |
| Lockfiles (`uv.lock` / `package-lock.json` or equivalent) are committed | `git status` shows no untracked/ignored lockfile |
| `semgrep`'s supply-chain check has been run at least once per Phase | Note the run in the Phase's review pass |
| **Accepted risk (Step 1.4):** 3 high-severity `npm audit` findings in frontend transitive deps (`postcss` XSS-in-CSS-stringify, `sharp`/libvips CVEs) — bundled inside Next.js 15 itself, fully fixed only in Next 16 | Re-run `npm audit` in `frontend/` whenever `next/image` optimization or CSS processing starts handling untrusted input (Phase 6/7) — re-evaluate then, don't let this stay "accepted" indefinitely once the exposure becomes real |
| **Pending re-check (Step 2.3):** `minio` (7.2.20) and `python-multipart` (0.0.32) were added without a `sonatype-guide` check — its MCP auth was unavailable at add-time (same known issue as before). Version confirmed current via direct PyPI lookup instead, not a full vulnerability/license check | Re-run `sonatype-guide` on both packages once its auth is available again; update this row once done |
| **Pending re-check (Step 3.1):** `casbin` (1.43.0) and `casbin-async-sqlalchemy-adapter` (1.17.0) were added without a `sonatype-guide` check — same recurring MCP auth issue. Versions confirmed current via direct PyPI lookup only | Re-run `sonatype-guide` on both packages once its auth is available again; update this row once done |
| **Pending re-check (Step 3.2):** `pyjwt` (2.13.0) and `argon2-cffi` (25.1.0) were added without a `sonatype-guide` check — same recurring MCP auth issue. Versions confirmed current via direct PyPI lookup only | Re-run `sonatype-guide` on both packages once its auth is available again; update this row once done |
| **Pending re-check (Step 3.4):** `cryptography` (50.0.0) was added without a `sonatype-guide` check — same recurring MCP auth issue. Version confirmed current via direct PyPI lookup only | Re-run `sonatype-guide` once its auth is available again; update this row once done |
| **Pending re-check (Step 5.2):** `arq` (0.28.0, pulling in `redis` 5.3.1 and `hiredis` as transitive deps) was added without a `sonatype-guide` check — same recurring MCP auth issue. Version confirmed current via direct PyPI lookup only | Re-run `sonatype-guide` on all three once its auth is available again; update this row once done |

Owning skill: `current-versions-only` (the standing policy), `fastapi-pro`/`nextjs-enterprise`/`container-security` (where versions actually get chosen), enforced via `sonatype-guide`/`semgrep`/`npm audit`.

## K. Rate Limiting & Abuse

| Check | How |
|---|---|
| 🔴 Login endpoint rate-limits/lockout per B above | Covered in section B |
| 🔴 Order lookup (Phase 6.4) rate-limits per section E above | Covered in section E |
| Tenant signup (Phase 2.1) isn't trivially spammable | Consider whether repeated signup attempts from one source need throttling before Phase 2.1 ships — flag to the user if this needs a decision, don't assume a specific limit |
| **Accepted gap (Step 3.3):** `POST /api/auth/password-reset/request` has no per-identifier or per-IP throttle — unlike login (account lockout after 5 failures), there's no equivalent brake on repeated reset requests for the same account. Response is always 202 regardless (no enumeration leak), but nothing stops a source from hammering the endpoint to spam the (stubbed) email pipeline or generate log noise. No general-purpose rate-limiting infrastructure exists yet (needs Redis, Phase 5.2) | Add a per-identifier throttle once Phase 5.2's Redis is available — don't build a one-off in-memory limiter now, it wouldn't survive a multi-process deploy anyway |

Owning skill: `security-hardening`, `payments-workflow`.

## L. File Uploads

| Check | How |
|---|---|
| ✅ Payment-proof screenshots (Phase 2.3 / 5.4) are validated for type and size before storage | Reject anything that isn't an image MIME type; enforce a max file size server-side, not just in the frontend `<input accept>`. Done in Step 2.3: `submit_subscription_payment` rejects >5MB and non-JPEG/PNG/WebP content types server-side, independent of the frontend `<input accept>` hint |
| Uploaded files are stored in MinIO and served via signed/expiring URLs, never made a public bucket | Inspect the MinIO bucket policy — no anonymous public read. Step 2.3 only writes (`make_bucket` defaults to private, no policy set); nothing reads a screenshot back yet — signed-URL generation is Step 2.4's concern (admin review screen) and must be checked again there |
| ✅ Uploaded filenames are never used as-is for storage paths | Generate a server-side object key (e.g. UUID), don't trust the client-supplied filename for path construction (path traversal risk). Done in Step 2.3: object key is `subscription-payments/{tenant_id}/{uuid4()}.{ext}`, extension derived from the validated content-type allowlist, not the client filename |

**Not yet built — track when it lands:** the click & collect / order receipt PDFs (`ROADMAP.md` Step 5.7) embed a QR code and barcode encoding a real order access code — the same credential Step 6.4's lookup relies on. A PDF meant for one customer must never be retrievable by guessing/incrementing an order ID; the retrieval endpoint needs the same "no real ID enumeration" discipline as the order-lookup-by-code pattern, not a sequential `/orders/{id}/receipt` anyone can walk. Confirm this before marking 5.7 tested.

Owning skill: `security-hardening`, `fastapi-pro`.

## M. Logging & Observability

| Check | How |
|---|---|
| No PII, password, token, or payment-proof detail appears in logs shipped to Loki | Review `app/core/logging.py` (Phase 8.3/10.3) log statements near auth/payment code paths |
| Alertmanager rules don't leak sensitive payloads into alert notifications | Inspect `infra/alertmanager/alertmanager.yml` templates (Phase 10.4) |

Owning skill: `deployment-orchestrator`, `notifications-workflow`.

---

## Amendment

If implementing a step reveals a vulnerability class not covered above, add a row here in the same change — following the same amendment discipline as `ROADMAP.md` Phase 13.4. This file should grow as real code surfaces real risks, not stay frozen at today's guess.
