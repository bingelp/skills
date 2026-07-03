---
name: plan
description: Turns an approved spec into a technical plan and task breakdown. Only runs when the user explicitly types /plan.
disable-model-invocation: true
model: opus
---

# Plan

## Overview

Turn `spec.md` into a concrete technical approach and an atomic task list. The plan is where architectural decisions get made and reviewed — before code, not during.

## When to Use

Explicit invocation only (`/plan`). Requires an existing `specs/<slug>/spec.md`.

**Don't bother for:** trivial changes where `/spec` was already skipped — go straight to `/build`.

## Process

1. Find `specs/<slug>/spec.md`. If no slug is obvious from context, ask which feature this is for. If `spec.md` doesn't exist, stop and tell the user to run `/spec` first. Read `CONTEXT.md` (or `CONTEXT-MAP.md`) if it exists so the plan's vocabulary matches the project's.
2. Read the spec's requirements and acceptance criteria. Explore the codebase for existing utilities, patterns, and files this will touch — reuse over rewriting.
3. For any architectural fork (more than one reasonable way to build this), interview the user about it one decision at a time using the `grilling` skill rather than silently picking one. For UI-bearing features this includes visual style — theme, color palette, typography — if `spec.md` didn't already pin it down: don't silently reach for a stock framework theme (e.g. default Material 3) just because it's the path of least resistance, especially when reference screenshots exist that were never actually asked about beyond layout.
4. Write `specs/<slug>/plan.md`:
   - **Approach** — the technical strategy, in plain language
   - **Files/modules touched** — with brief reasoning
   - **Key decisions & trade-offs** — anything non-obvious, alternatives you rejected and why
5. For each key decision, apply the `domain-modeling` skill's ADR test (hard to reverse + surprising without context + real trade-off). If all three hold, record it as an ADR rather than only noting it in `plan.md` — `plan.md` is feature-scoped and disposable, ADRs are permanent project memory.
6. Write `specs/<slug>/tasks.md` as a checklist of atomic, independently-verifiable tasks (thin vertical slices, not "write all the models" then "write all the views"). Each task should be small enough to implement and verify in one sitting.
7. Show the user both files (and any new ADRs). Stop. Tell them: "Review this, and run `/build` once you're happy with it."

## Red Flags

- Skipping straight to task-writing without an Approach section — the plan needs a narrative, not just a checklist.
- Tasks that bundle multiple unrelated changes — split them.
- Introducing a new dependency or pattern not justified by the spec — flag it as a decision, don't silently do it.
- Defaulting to a stock theme/style for a UI-bearing feature without confirming it with the user, particularly when reference screenshots or mockups exist and weren't asked about beyond layout.
- Making a hard-to-reverse architectural call without offering an ADR, or writing an ADR for something trivial or easily reversed — see `domain-modeling`'s three-part test.
