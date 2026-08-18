# Git Push Workflow — Cross-Agent

Applies to ANY agent (opencode, Cursor, Codex, Gemini CLI, etc.).

## Golden rule: push to `dev` is automatic at step completion

- **Auto-push to `dev` at the end of every step implementation** — the moment a step's code is staged and committed, run the sequence below and push to `dev`.
- Do NOT push on every intermediate edit *within* a step — only when a step's implementation actually lands.
- `staging` is pushed only on **"test done X"**. `main` is pushed only on explicit instruction — never inferred.
- Read-only git operations never trigger a push.

## Commit message prefixes

| Prefix | Use for |
|---|---|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `docs:` | Documentation-only |
| `chore:` | Tooling, config, dependency, scaffolding |
| `refactor:` | Restructuring code with no behavior change |
| `test:` | Adding/fixing tests only |
| `ci:` | CI/CD pipeline changes specifically |

## Branch strategy: dev → staging → main

| Branch | What lands here | When |
|---|---|---|
| `dev` | Every commit from active work | Auto-pushed at step completion — default push target |
| `staging` | A snapshot of `dev` | When user marks step "test done" |
| `main` | A snapshot of `staging` | Only on explicit user instruction |

- Default push target is `dev`.
- **Never commit straight to `staging` or `main`.**

## Sequence (mandatory order)

1. Stage and commit as normal.
2. Run `scripts/graphify_update.sh` if graphify-out/ exists.
3. Push: `git push`.
