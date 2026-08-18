---
name: saas-architect
description: Use when designing, extending, or reasoning about the multi-tenant SaaS architecture — schema-per-tenant PostgreSQL isolation, feature flipping / subscription-tier gating, tenant provisioning, or sequencing/amending phases. Trigger on tenant isolation, subscription tiers, feature flags, new SaaS module, cross-cutting architecture decisions, or roadmap/phase planning.
---

# SaaS Architect

## Source of truth

Before proposing any architecture change, read:
- `CLAUDE.md` — the non-negotiable constraints.
- `ROADMAP.md` — the phased build order and what's already been decided.

## Multi-tenancy model

- **Schema-per-tenant** in PostgreSQL. Each tenant gets its own schema; a `public` control schema holds the tenant registry.
- Every DB session **must** issue `SET LOCAL app.current_tenant` before any tenant-scoped query.
- Migrations: control-schema migrations run once; per-tenant migrations run against the schema template and replayed per tenant.

## Feature flipping / subscription tiering

- Premium modules gated by **server-side feature flag resolved from the tenant's subscription tier**. Never gate purely in frontend — API must also refuse.
- **Two-state check**: tier eligibility AND tenant activation.
- When adding a new premium feature: (1) add flag/tier check, (2) gate API route, (3) gate UI. API first.

## Roadmap stewardship

`ROADMAP.md` is a living document. Two situations call for editing it:
1. **New scope**: add step to roadmap first, then implement.
2. **Amendment**: if implementation reveals earlier design was wrong, correct ROADMAP.md in place, then resume.
