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

This session is a **build orchestrator**: it never implements a task itself. It dispatches one disposable **task subagent** per unchecked task, waits for it to return, and repeats — keeping its own context to `O(tasks)` instead of growing with every file read and edit across the whole feature.

## Process

1. Find `specs/<slug>/tasks.md` and `specs/<slug>/plan.md`. If either doesn't exist, stop and tell the user to run `/plan` first. Read `plan.md`'s Approach and Files/modules touched sections, `CONTEXT.md`, and any ADRs relevant to the area being touched — this is context to hand to each task subagent, not something to act on yourself.
2. Take the first unchecked task in `tasks.md` order. Dispatch it to a task subagent via the `Agent` tool, foreground/blocking — never `run_in_background: true`, never the `Workflow` tool, never `/loop`. Use `subagent_type: general-purpose` so it has full tool access and normal skill auto-triggering (e.g. `tdd`). If the task carries a trailing `` `[model: X]` `` hint, pass `model: X` to the `Agent` call; otherwise omit `model` so the subagent inherits this session's default (`sonnet`).
3. Give the subagent a self-contained brief: the task's exact text, `plan.md`'s Approach and Files/modules touched sections, `CONTEXT.md`, relevant ADRs, and the previous task's task note if one exists — never a prior subagent's transcript.
4. Instruct the subagent to implement just that task, verify it (run it, run relevant tests, check the behavior), check it off in `tasks.md`, and append a **task note** to that task's line: what changed, any decisions or deviations from the plan, and verification evidence. If it hits something the plan didn't anticipate, it should stop without reconciling `plan.md`/`spec.md` itself and report the blocker back instead.
5. Wait for the subagent to return before doing anything else — the next task is never dispatched until the current one's subagent has returned.
6. If the subagent reports a blocker, halt the loop entirely — dispatch no further tasks. Surface the blocker to the user rather than improvising a design decision. If resolving it means the `plan.md` (or `spec.md`) is now wrong, fix the artifact — don't just resume dispatching against a plan that's silently wrong. Make the change through the owning step, reconcile downstream per [where/RECONCILE.md](../where/RECONCILE.md), and only then resume the loop. If it's a hard-to-reverse decision made on the fly, use `domain-modeling` to decide whether it needs an ADR.
7. Otherwise, repeat from step 2 with the next unchecked task.
8. Once every task in `tasks.md` is checked off, tell the user: "All tasks complete. Run `/test` to verify against the spec's acceptance criteria."

Because all state lives in `tasks.md` (checkboxes + task notes), a fresh `/build` session started after an interrupted run just re-reads the file and resumes at the first unchecked task — no separate recovery step, and no already-completed task gets redone.

## Red Flags

- Implementing a task yourself instead of dispatching a task subagent — this session is the orchestrator; keep implementation-level tool calls (`Edit`/`Write`/`Bash`/`Read` against source files) out of its own context.
- Dispatching more than one task subagent at a time, or out of `tasks.md` order — dispatch is strictly sequential; wait for each subagent to return before the next.
- Letting a task subagent reconcile `plan.md`/`spec.md` itself when it hits something the plan didn't anticipate — it reports the blocker back; reconciliation is the orchestrator's/user's call, not the disposable subagent's.
- Marking a task done without the subagent actually verifying it.
- Introducing a new term for something `CONTEXT.md` already names, or quietly contradicting a recorded ADR.
- Resuming the loop against a plan that's been silently revised without updating `plan.md` and reconciling the affected tasks — the code and the plan drift apart and `/review` will catch it later, more expensively. See `where/RECONCILE.md`.
