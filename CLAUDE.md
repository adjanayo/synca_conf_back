<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build
rtk cargo check
rtk cargo clippy
rtk tsc
rtk lint
rtk prettier --check
rtk next build
```

### Test (60-99% savings)
```bash
rtk pytest              # Python test failures only (90%)
rtk cargo test
rtk go test
rtk jest
rtk vitest
rtk playwright test
rtk rake test
rtk rspec
rtk test <cmd>
```

### Git (59-80% savings)
```bash
rtk git status
rtk git log
rtk git diff
rtk git show
rtk git add
rtk git commit
rtk git push
rtk git pull
rtk git branch
rtk git fetch
rtk git stash
rtk git worktree
```

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>
rtk gh pr checks
rtk gh run list
rtk gh issue list
rtk gh api
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list
rtk pnpm outdated
rtk pnpm install
rtk npm run <script>
rtk npx <cmd>
rtk uv run <cmd>
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>
rtk read <file>
rtk grep <pattern>
rtk find <pattern>
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>
rtk log <file>
rtk json <file>
rtk deps
rtk env
rtk summary <cmd>
rtk diff
```

### Infrastructure (85% savings)
```bash
rtk docker ps
rtk docker images
rtk docker logs <c>
rtk kubectl get
rtk kubectl logs
```

### Network (65-70% savings)
```bash
rtk curl <url>
rtk wget <url>
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history
rtk discover
rtk proxy <cmd>
rtk init
rtk init --global
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->

# Additional AI Agent Rules

## Context & Tools (Context7 & Graphify)
- **ALWAYS** use the Context7 MCP tool to fetch updated documentation before writing code for external libraries or frameworks (FastAPI, SQLAlchemy, Pydantic, etc.).
- **BEFORE** executing complex architectural or structural modifications, inspect the local `graphify-out/GRAPH_REPORT.md` file to prevent breaking connected components.
- **AUTO-UPDATE TRIGGER**: Whenever you detect a new dependency, library, framework, or tech stack being introduced in the codebase (e.g. in `requirements.txt`, `pyproject.toml`, or via new code imports), you **MUST** automatically update this `CLAUDE.md` file to explicitly force the use of official documentation for that new technology.
- **GIT PUSH AUTOMATION**: Whenever the user asks you to run a push command or whenever you run `rtk git push`, you **MUST** execute the graphify update right before sending the push, to ensure the committed architecture map is perfectly up to date.

## Behavior (Low-Token, High-Utility Output)

Strict output-style rules, enforced on every response in this project:

1. **Zero conversational filler.** No greetings, pleasantries, transitions, or closing remarks.
2. **Direct output first.** The requested code, config, or answer starts on the very first line.
3. **Concise explanations.** Short bulleted fragments, not full paragraphs.
4. **Token efficiency.** Favor information-dense code over prose; minimize text-based explanation.
5. **No narration of tool calls.** Never describe what a tool call is about to do — the tool call itself is the evidence.
6. **No restating tool output.** If a Read/Bash/grep result is already visible, don't re-paste or re-summarize it.
7. **One-line acks.** A confirmation gets one line, not a paragraph.
8. **Bundle, don't narrate serially.** Report the outcome once at the end, not a running commentary.

Exceptions:
- `test-tracker`'s mandatory resume headers still apply after implementing a step.
- Skill files under `.claude/skills/` are reference material — their explanatory "why" stays untouched.
- A genuine blocking question to the user stays a full sentence.

## Session Token Budget Discipline

1. **Targeted tests by default.** Run only the test file(s) covering the changed code, not the full suite.
2. **Never re-read a file you just edited or wrote.**
3. **Batch tool calls.** Independent Read/Bash/Grep calls go in one message.
4. **One rebuild per verification pass**, not one per file.
5. **Don't dump large tool output back into prose.** Use `rtk`'s filtering and reference results by name/line.

# CLAUDE SYSTEM BEHAVIOR INSTRUCTIONS (CRITICAL)

## 1. CODE GENERATION RULES
- **NEVER TRUNCATE CODE:** Write out every file completely. No placeholders.
- **PRODUCTION-READY:** Clean, typed, secure code. Proper error handling, async patterns, logging, input validation.
- **MODULAR ARCHITECTURE:** If a file becomes too large, split into smaller sub-modules.

## 2. CLI & COMMAND DELIVERY
- **EXPLICIT COMMANDS:** Every time you generate or modify code, provide exact terminal commands to build, run, test, and verify.
- **LOCAL VS PROD AWARENESS:** Separate instructions for local dev and production.

## 3. PROJECT PARADIGMS
- **CORE PRODUCT:** SaaS backend API with FastAPI.
- **SECURITY FIRST:** Schema isolation with `SET LOCAL app.current_tenant` in PostgreSQL. Secure PII with Fernet. Enforce RBAC.

## 4. INTERACTIVE PROCESS
- Work one step at a time.
- Provide a short validation checklist at the end of every response.
- Ask for explicit approval before moving to the next step.
