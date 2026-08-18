---
name: change-control
description: Use before editing ANY file that implements a step already marked "Test Done" — check this skill first, before writing the edit. Covers the standing rule that validated/working features are not to be changed except for a real bug or an explicit user request.
---

# Change Control

The user tests every step by hand and marks it `Test Done` once verified. That mark means: **this code is trusted and working, exactly as it stands.** It is not an invitation to refactor, "improve," restyle, or reshape it while working on something else nearby.

## The rule

Before editing a file that backs a `Test Done` step, one of exactly two things must be true:

1. **A real bug was found** — something actually broken, not stylistic preference. State what's broken before touching the code.
2. **The user explicitly asked for that feature to change** — a new requirement, correction, or design change they requested.

If neither is true, don't make the edit — even if it looks like an obvious improvement. A `Test Done` step is a promise that what the user verified is still what's running.

## How to check

`TESTING.md` is the source of truth. Before editing a file:
1. Identify which step the file belongs to.
2. Check that step's status. If `Not Started` or `In Progress`, edit freely.
3. If `Test Done`, confirm you have a bug or explicit change request before proceeding.
