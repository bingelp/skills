---
name: review
description: Final spec-conformance review comparing the implementation against specs/<slug>/spec.md and plan.md. Only runs when the user explicitly types /review.
disable-model-invocation: true
model: opus
---

# Review

## Overview

A spec-conformance review: did the finished work actually match what `/spec` promised and `/plan` designed? This is not a code-quality or security review — use existing code-review/security-review skills for that. This is the closing gate on the pipeline.

## When to Use

Explicit invocation only (`/review`). Requires `specs/<slug>/spec.md`, `specs/<slug>/plan.md`, and a passing `/test` pass.

## Where artifacts live

Every `specs/<slug>/…` path below resolves under the repo's **shared git dir**, not the working tree:

```sh
SPECS="$(git rev-parse --path-format=absolute --git-common-dir)/specs"   # e.g. …/.git/specs
```

Storing artifacts there keeps them visible across every session and worktree — including the background-isolated steps Claude Code may switch into automatically — while making them impossible to accidentally commit. Outside a git repo, fall back to `./specs`.

## Process

1. Find `specs/<slug>/spec.md` and `specs/<slug>/plan.md`. If either doesn't exist, stop and tell the user to run `/spec` or `/plan` first. If `/test` hasn't been run (no Verification section in `specs/<slug>/tasks.md`), stop and tell the user to run `/test` first.
2. Diff the actual implementation against `specs/<slug>/plan.md`'s stated approach. Note any deviations and whether they were justified.
3. Walk every acceptance criterion in `specs/<slug>/spec.md` one more time against the real diff (not the `/test` output — independently confirm). Reference each by its `AC<n>` ID so your verdict lines up one-to-one with `/test`'s Verification section and any ID present in `spec.md` but absent from that section is caught as a gap.
4. Check for domain drift: did the build introduce terminology that contradicts `CONTEXT.md`, or make a hard-to-reverse call that should have an ADR but doesn't? Flag both — use `domain-modeling` to fix drift or write the missing ADR before closing out.
5. Check for **chain drift** — the closing backstop for the loop-back protocol. Does every `spec.md` `AC<n>` have a lineage through `plan.md`/`tasks.md` and a verification entry, or did the spec change after those were written? Did the build alter the spec's intent without the spec being updated to match? If the chain is inconsistent, flag it and reconcile per [where/RECONCILE.md](../where/RECONCILE.md) before closing out — a passing review over a drifted chain is a false green.
6. Write `specs/<slug>/review.md`:
   - **Verdict per acceptance criterion** — `AC<n>`: met / not met / partially met
   - **Deviations from the plan** — what changed and why
   - **Chain drift** — any spec/plan/tasks/verification inconsistency found and how it was reconciled (or "none")
   - **Domain/ADR gaps** — glossary drift or undocumented hard-to-reverse decisions found
   - **Open follow-ups** — anything explicitly out of scope but worth flagging
7. Show the user the review. Stop — this is the end of the pipeline, no further auto-chaining.

## Red Flags

- Rubber-stamping because `/test` already passed — this step exists to catch spec drift `/test` wouldn't notice (e.g. a criterion was quietly reinterpreted).
- Treating this as a code-style review — that's a different skill's job.
- Skipping straight to "looks good" without listing deviations from the plan.
- Letting a hard-to-reverse decision ship without an ADR because it wasn't caught during `/plan` or `/build`.
- Closing out a green review over a drifted chain — e.g. `spec.md` gained an `AC<n>` that was never planned, built, or tested. A false green is worse than an honest "not met." See `where/RECONCILE.md`.
