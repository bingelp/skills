---
name: build
description: Implements tasks from an approved plan, one at a time. Only runs when the user explicitly types /build.
disable-model-invocation: true
---

# Build

## Overview

Implement the tasks in `specs/<slug>/tasks.md`, one at a time, in thin vertical slices. Each task should leave the codebase in a working, verifiable state — no half-finished slices spanning multiple tasks.

## When to Use

Explicit invocation only (`/build`). Requires `specs/<slug>/plan.md` and `specs/<slug>/tasks.md`.

## Process

1. Find `specs/<slug>/tasks.md` and `specs/<slug>/plan.md`. If either doesn't exist, stop and tell the user to run `/plan` first. Read `plan.md`'s Approach and Files/modules touched sections so you're working from its reasoning instead of re-exploring the codebase from scratch. Also read `CONTEXT.md` and any ADRs in the area you're touching — name things per the glossary and don't casually contradict a recorded decision.
2. Take the first unchecked task. Implement just that task — don't jump ahead to later tasks even if it'd be convenient.
3. Verify the task works (run it, run relevant tests, check the behavior) before checking it off.
4. Check the task off in `specs/<slug>/tasks.md` and briefly note what changed.
5. Repeat until all tasks are checked, or until you hit something the plan didn't anticipate — in that case, stop and surface it rather than improvising a design decision. If it's a hard-to-reverse decision made on the fly, use `domain-modeling` to decide whether it needs an ADR.
6. Once every task is checked, tell the user: "All tasks complete. Run `/test` to verify against the spec's acceptance criteria."

## Red Flags

- Implementing multiple tasks in one pass "for efficiency" — defeats the point of independently-verifiable slices.
- Silently deviating from `plan.md` because it turned out to be wrong — stop and tell the user, don't just improvise.
- Marking a task done without actually verifying it.
- Introducing a new term for something `CONTEXT.md` already names, or quietly contradicting a recorded ADR.
