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

## Process

1. Find `specs/<slug>/spec.md` and `specs/<slug>/plan.md`. If either doesn't exist, stop and tell the user to run `/spec` or `/plan` first. If `/test` hasn't been run (no Verification section in `specs/<slug>/tasks.md`), stop and tell the user to run `/test` first.
2. Diff the actual implementation against `specs/<slug>/plan.md`'s stated approach. Note any deviations and whether they were justified.
3. Walk every acceptance criterion in `specs/<slug>/spec.md` one more time against the real diff (not the `/test` output — independently confirm).
4. Check for domain drift: did the build introduce terminology that contradicts `CONTEXT.md`, or make a hard-to-reverse call that should have an ADR but doesn't? Flag both — use `domain-modeling` to fix drift or write the missing ADR before closing out.
5. Write `specs/<slug>/review.md`:
   - **Verdict per acceptance criterion** — met / not met / partially met
   - **Deviations from the plan** — what changed and why
   - **Domain/ADR gaps** — glossary drift or undocumented hard-to-reverse decisions found
   - **Open follow-ups** — anything explicitly out of scope but worth flagging
6. Show the user the review. Stop — this is the end of the pipeline, no further auto-chaining.

## Red Flags

- Rubber-stamping because `/test` already passed — this step exists to catch spec drift `/test` wouldn't notice (e.g. a criterion was quietly reinterpreted).
- Treating this as a code-style review — that's a different skill's job.
- Skipping straight to "looks good" without listing deviations from the plan.
- Letting a hard-to-reverse decision ship without an ADR because it wasn't caught during `/plan` or `/build`.
