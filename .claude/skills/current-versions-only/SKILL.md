---
name: current-versions-only
description: Use whenever choosing, adding, upgrading, or defending the version of ANYTHING — a language runtime, a package/dependency, a Docker base image, a framework major version, a CI action. Standing policy — not tied to one phase. Trigger on "add this package," "which version," "is this outdated," "pin the version."
---

# Current Versions Only

**Standing rule: never intentionally run outdated software with known, patchable vulnerabilities.** This applies everywhere — language runtimes, package dependencies, Docker base images, CI actions, locally-installed tools.

## The rule, concretely

- **When choosing a new dependency**: default to the latest stable version. Check it (`sonatype-guide` for Python packages; `uv`'s own resolution for what's actually installed).
- **When a project paradigm names a specific version**: that's a starting point, not permission to ignore vulnerabilities discovered later. If a check reveals the named version is outdated/vulnerable, **say so and propose the amendment**.
- **Never fix a vulnerability by downgrading** — direction is always forward (upgrade) or documented accepted-risk.
- **A dependency that was fine when added can become vulnerable later.** Re-check at least once per phase and always before production deploy.
- **Container/OS-level versions matter too**: Docker base images, Python/Node runtime versions, locally-installed tools.

## When a check is unavailable

If the checking tool is broken or unauthenticated — say so explicitly, don't silently skip. Note as a follow-up to re-check once available.

## Accepted-risk exceptions are documented, not silent

Sometimes the only way to clear every advisory is a breaking major-version jump. That's a legitimate call — but it goes in `SECURITY_CHECKLIST.md` as an explicit accepted-risk row with a revisit trigger.
