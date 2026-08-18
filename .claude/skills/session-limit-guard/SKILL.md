---
name: session-limit-guard
description: Use proactively during any long working session — check every ~10-15 turns of real work, and always before "let's stop here" or "continue this later." Manages conversation longevity by estimating context budget, writing a handoff note, and pointing the next session at it via CLAUDE.md.
---

# Session Limit Guard

A safety net for cross-session continuity — a handoff note surviving on disk beats hoping the next session's summary caught everything.

## 1. Track roughly

Keep an approximate running count of turns. Precision doesn't matter; trigger points are deliberately conservative.

## 2. Checkpoint at ~12-15 turns or when context feels tight

Pause before starting the *next* unrelated chunk of work (not mid-step) and run through steps 3-5. If mid-conversation, don't announce a hard halt — just write the handoff note quietly.

## 3. Write the handoff note

Create `.claude/session-notes/YYYY-MM-DD-<short-topic-slug>.md`:
- **Tech stack / stage**: which phase/step(s) this session touched.
- **Key decisions**: design tradeoffs, scope calls, deferred items.
- **Ongoing loops**: half-implemented steps, unanswered questions.
- **Exact next step**: specific enough that a fresh session can act on it.

## 4. Point the next session at it

Update `CLAUDE.md` with a `## Session Continuity` section linking to the note.

## 5. Re-align with TODO.md every checkpoint

Read `TODO.md`, act on pending items, update what got done.
