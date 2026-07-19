---
name: build
description: Implements tasks from an approved plan, one at a time. Only runs when the user explicitly types /build.
disable-model-invocation: true
model: sonnet
---

# Build

## Overview

Implement the tasks in `specs/<slug>/tasks.md`, one at a time, in thin vertical slices. Each task should leave the codebase in a working, verifiable state — no half-finished slices spanning multiple tasks.

## When to Use

Explicit invocation only (`/build`). Requires `specs/<slug>/plan.md` and `specs/<slug>/tasks.md`.

## Where artifacts live

Every `specs/<slug>/…` path below resolves under the repo's **shared git dir**, not the working tree:

```sh
SPECS="$(git rev-parse --path-format=absolute --git-common-dir)/specs"   # e.g. …/.git/specs
```

Storing artifacts there keeps them visible across every session and worktree — including the background-isolated steps Claude Code may switch into automatically — while making them impossible to accidentally commit. Outside a git repo, fall back to `./specs`.

`tasks.md` stays a lean checklist — it does **not** hold the full per-task write-up. Each task's detail (what changed, decisions/deviations, verification evidence) goes in its own file under `specs/<slug>/tasks/`, named `NN-slug.md` from the task's number (2-digit, zero-padded) and a short kebab-case slug of its title (e.g. task `3. Persistence layer.` → `tasks/03-persistence-layer.md`) — mirroring the `NNNN-slug.md` convention this pipeline already uses for ADRs in `docs/adr/`. This keeps `tasks.md` itself at roughly one line per task regardless of how much detail a task generates, so a fresh `/build` (or `/where`, `/ship`, `/review`) session reads a short file instead of one that grows into thousands of lines over a long build.

A worktree-isolated session's `Edit`/`Write` tools may refuse the shared specs path since it sits outside the worktree root. That's expected, not a blocker: fall back to `Bash` (e.g. `python3` or a heredoc) to update `tasks.md` and write task-note files when this happens. This path is deliberately untracked and shared across every worktree, so writing to it doesn't touch anything the isolation guard is protecting — it's the one sanctioned exception to the Red Flag below about routing around blocked writes, and it does not extend to source files.

This session is a **build orchestrator**: it never implements a task itself. It dispatches one disposable **task subagent** per unchecked task, waits for it to return, and repeats — keeping its own context to `O(tasks)` instead of growing with every file read and edit across the whole feature.

## Process

1. Find `specs/<slug>/tasks.md` and `specs/<slug>/plan.md`. If either doesn't exist, stop and tell the user to run `/plan` first. Read `plan.md`'s Approach and Files/modules touched sections, `CONTEXT.md`, and any ADRs relevant to the area being touched — this is context to hand to each task subagent, not something to act on yourself.
2. Take the first unchecked task in `tasks.md` order. Dispatch it to a task subagent via the `Agent` tool, foreground/blocking — never `run_in_background: true`, never the `Workflow` tool, never `/loop`. Use `subagent_type: general-purpose` so it has full tool access and normal skill auto-triggering (e.g. `tdd`). If the task carries a trailing `` `[model: X]` `` hint, pass `model: X` to the `Agent` call; otherwise omit `model` so the subagent inherits this session's default (`sonnet`).
3. Give the subagent a self-contained brief: the task's exact text, `plan.md`'s Approach and Files/modules touched sections, `CONTEXT.md`, relevant ADRs, and the previous task's note file (`specs/<slug>/tasks/NN-slug.md`) if one exists — read just that one file, never the whole `tasks.md` history or a prior subagent's transcript.
4. Instruct the subagent to implement just that task, verify it (run it, run relevant tests, check the behavior), check it off in `tasks.md`, and record what it did in two places (falling back to `Bash` for both writes if `Edit`/`Write` refuses the shared specs path — see "Where artifacts live"):
   - **`tasks.md`** — flip the checkbox and append a short one-line summary to that task's line, plus a pointer to its note file, e.g. `— see tasks/03-persistence-layer.md`. Nothing longer than a line goes here.
   - **`specs/<slug>/tasks/NN-slug.md`** (new file) — the full task note: what changed, any decisions or deviations from the plan, and verification evidence. This is where the detail lives; a later session opens it only if it needs that detail.

   If it hits something the plan didn't anticipate — including a tool refusing to edit a **source file** (e.g. a worktree-isolation guard blocking `Edit`/`Write` on a tracked file) — it should stop without working around the refusal or reconciling `plan.md`/`spec.md` itself, and report the blocker back instead.
5. Wait for the subagent to return before doing anything else — the next task is never dispatched until the current one's subagent has returned.
6. If the subagent reports a blocker, halt the loop entirely — dispatch no further tasks. Surface the blocker to the user rather than improvising a design decision. If resolving it means the `plan.md` (or `spec.md`) is now wrong, fix the artifact — don't just resume dispatching against a plan that's silently wrong. Make the change through the owning step, reconcile downstream per [where/RECONCILE.md](../where/RECONCILE.md), and only then resume the loop. If it's a hard-to-reverse decision made on the fly, use `domain-modeling` to decide whether it needs an ADR.
7. Otherwise, repeat from step 2 with the next unchecked task.
8. Once every task in `tasks.md` is checked off, tell the user: "All tasks complete. Run `/test` to verify against the spec's acceptance criteria."

Because all state lives in `tasks.md` (checkboxes + one-line pointers) and `specs/<slug>/tasks/` (the full per-task notes it points to), a fresh `/build` session started after an interrupted run just re-reads `tasks.md` and resumes at the first unchecked task — no separate recovery step, and no already-completed task gets redone.

## Red Flags

- Implementing a task yourself instead of dispatching a task subagent — this session is the orchestrator; keep implementation-level tool calls (`Edit`/`Write`/`Bash`/`Read` against source files) out of its own context.
- Dispatching more than one task subagent at a time, or out of `tasks.md` order — dispatch is strictly sequential; wait for each subagent to return before the next.
- Letting a task subagent reconcile `plan.md`/`spec.md` itself when it hits something the plan didn't anticipate — it reports the blocker back; reconciliation is the orchestrator's/user's call, not the disposable subagent's.
- A task subagent routing around a blocked `Edit`/`Write` call on a **source file** (e.g. a worktree-isolation guard) via `Bash` heredocs, `python3`, or similar, instead of stopping and reporting the refusal as a blocker — a tool refusal on a tracked file is exactly the kind of thing step 4 means by "something the plan didn't anticipate"; silently working around it can leave the tree in an inconsistent, partially-isolated state that later tasks then collide with. This does not apply to the `tasks.md`/`tasks/*.md` writes under the shared specs path, where a `Bash` fallback is expected — see "Where artifacts live".
- Marking a task done without the subagent actually verifying it.
- Writing the full task note (decisions, deviations, verification evidence) into `tasks.md` itself instead of `tasks/NN-slug.md` — this is exactly the bloat the split exists to avoid; `tasks.md` gets a one-line summary and a pointer, nothing more.
- Introducing a new term for something `CONTEXT.md` already names, or quietly contradicting a recorded ADR.
- Resuming the loop against a plan that's been silently revised without updating `plan.md` and reconciling the affected tasks — the code and the plan drift apart and `/review` will catch it later, more expensively. See `where/RECONCILE.md`.
