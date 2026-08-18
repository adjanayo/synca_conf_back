---
name: git-push-workflow
description: Use every time a git commit or git push is about to run, whether the user says "commit", "push", "rtk git commit", "rtk git push", or "push this up". Encodes the Conventional Commits prefix convention and the graphify architecture graph refresh rule before push.
---

# Git Push Workflow

## Commit message prefixes

| Prefix | Use for |
|---|---|
| `feat:` | New feature or capability (endpoint, UI screen) |
| `fix:` | Bug fix — correcting wrong behavior |
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

- **Never commit straight to `staging` or `main`.**
- Default push target is `dev`.

## Sequence (mandatory order)

1. Stage and commit as normal (`rtk git add`, `rtk git commit`).
2. Run `scripts/graphify_update.sh` if graphify-out/ exists. Commit changes if any.
3. Push: `rtk git push`.

Do not reorder — pushing before the graph update means the remote has code without a matching graph.

## Promoting to staging (on "test done X")

```bash
git checkout staging
git merge dev --ff-only
git push origin staging
git checkout dev
```

## Promoting to main (only when explicitly asked)

```bash
git checkout main
git merge staging --ff-only
git push origin main
git checkout dev
```
