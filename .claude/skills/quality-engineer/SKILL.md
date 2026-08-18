---
name: quality-engineer
description: Use when writing or fixing tests, wiring CI, or working on the regression gate — pytest/pytest-asyncio unit tests, E2E specs, GitHub Actions workflow. Trigger whenever the user asks to add/fix tests, set up or debug CI, verify a step's verification command passes, or asks "is this safe to merge."
---

# Quality Engineer

## Test layers

1. **Per-step verification** — whatever was specified for the step. Fastest feedback loop.
2. **Backend unit/integration** — `pytest` (+ `pytest-asyncio` for async) under `tests/`, mirroring `app/` structure.
3. **Cross-phase E2E** — Playwright specs covering flows that span phases.
4. **CI gate** — `.github/workflows/ci.yml` runs tests on every push/PR.

## Writing a good test

- Name for behavior, not function: `test_employee_denied_owner_action`, not `test_casbin_1`.
- For money/stock/PII: prove the *failure mode* is prevented, not just happy path.
- Concurrency-sensitive logic needs tests that actually exercise concurrent access.

## Security review is part of "done"

Before marking any security-tagged step as tested: run security-review on the diff, confirm sonatype-guide was consulted if a new dependency was added.

## Commands

- Backend: `rtk pytest tests/<path> -v`
- Everything: `make test-all`
