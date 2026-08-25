---
name: direct-execution
description: Use for every implementation task on this project — scaffolding, Docker, migrations, endpoints, tests. Covers the standing rule to execute directly with tools (Bash/rtk, Read, Edit, Write) instead of delegating to subagents via the Agent tool.
---

# Direct Execution — No Subagents

The user wants this project's implementation work done directly, not delegated.

## The rule

Do not use the `Agent` tool to spawn subagents (general-purpose, fork, or otherwise) for scaffolding, coding, Docker, migrations, or endpoint work on this repo — even when the task is large, repetitive, or spans many files. Execute it inline with the tools already available: `Bash` (prefixed with `rtk` per this repo's `CLAUDE.md`), `Read`, `Edit`, `Write`.

**Why:** explicit user instruction — they want to see and control each step directly, not have it happen inside a subagent's isolated context.

## How to apply

- A multi-step roadmap phase (e.g. Phase 1's ten table migrations) is still done as a sequence of direct tool calls in the main thread, one step at a time, not farmed out.
- This does not restrict non-Agent tools (Bash, Docker, git) — only the Agent/subagent delegation path.
- Keep output terse per the project's low-token CLAUDE.md style while doing this — direct execution and compressed output are separate rules that both apply here.
