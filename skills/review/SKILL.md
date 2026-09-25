---
name: review
description: Final spec-conformance review comparing the implementation against specs/<slug>/spec.md and plan.md. Only runs when the user explicitly types /review.
disable-model-invocation: true
model: opus
---

# Review

## Overview

A spec-conformance review: did the finished work actually match what `/spec` promised and `/to-plan` designed? This is not a code-quality or security review — use existing code-review/security-review skills for that. This is the closing gate on the pipeline.

## When to Use

Explicit invocation only (`/review`). Requires `specs/<slug>/spec.md`, `specs/<slug>/plan.md`, and a `specs/<slug>/review.md` whose Verification section `/test` wrote.

## Where artifacts live

`specs/<slug>/` at the repo root, committed on the feature branch. This step adds its verdict to
`specs/<slug>/review.md`, below the Verification section `/test` wrote, and commits it.

## Process

1. Find `specs/<slug>/spec.md` and `specs/<slug>/plan.md`. If either doesn't exist, stop and tell the user to run `/spec` or `/to-plan` first. If `/test` hasn't been run (no Verification section in `specs/<slug>/review.md`), stop and tell the user to run `/test` first.
2. Diff the actual implementation (the feature branch against its base, `git diff <default-branch>...HEAD`; each task is its own `T<n>` commit, so you can walk it task by task) against `specs/<slug>/plan.md`'s stated approach. Note any deviations and whether they were justified. `plan.md`'s **Deviations** section, the tasks' done-lines, and any `specs/<slug>/tasks/T<n>-slug.md` note files often already record a deviation flagged during `/build`. Check there before assuming a mismatch is undocumented.
3. Walk every acceptance criterion in `specs/<slug>/spec.md` one more time against the real diff (not the `/test` output — independently confirm). Reference each by its `AC<n>` ID so your verdict lines up one-to-one with `/test`'s Verification section and any ID present in `spec.md` but absent from that section is caught as a gap.
4. Check for domain drift: did the build introduce terminology that contradicts `CONTEXT.md`, or make a hard-to-reverse call that should have an ADR but doesn't? Flag both — use `domain-modeling` to fix drift or write the missing ADR before closing out.
5. Check for **chain drift** — the closing backstop for the loop-back protocol. Does every `spec.md` `AC<n>` have a task in `plan.md` that cites it and a line in `review.md`'s Verification, or did the spec change after those were written? Did the build alter the spec's intent without the spec being updated to match? If the chain is inconsistent, flag it and reconcile per [where/RECONCILE.md](../where/RECONCILE.md) before closing out — a passing review over a drifted chain is a false green.
6. Add your verdict to `specs/<slug>/review.md`, below Verification (replace an earlier verdict if you're re-running). Keep it tight: one line per AC, and "none" is a complete answer for any of the other sections.
   - `## Verdict`: one line per criterion, `AC<n>`: met / not met / partially met, with a few words of why when it isn't simply "met"
   - `## Deviations from the plan`: what changed and whether it was justified
   - `## Chain drift`: any spec/plan/verification inconsistency found and how it was reconciled
   - `## Domain/ADR gaps`: glossary drift, or hard-to-reverse decisions with no ADR
   - `## Follow-ups`: anything explicitly out of scope but worth flagging
   Then commit: `git add specs/<slug>/review.md` and `git commit -m "review(<slug>): <verdict summary>" -- specs/<slug>/review.md` (plus any `CONTEXT.md`/ADR files you fixed in step 4).
7. Show the user the review. If this session is still worktree-isolated, ask the user whether to keep or remove the worktree before finishing, per [docs/worktrees.md](../../docs/worktrees.md). Stop. If every AC is met, tell them: "Run `/ship` to open the PR."

## Red Flags

- Rubber-stamping because `/test` already passed — this step exists to catch spec drift `/test` wouldn't notice (e.g. a criterion was quietly reinterpreted).
- Treating this as a code-style review — that's a different skill's job.
- Skipping straight to "looks good" without listing deviations from the plan.
- Letting a hard-to-reverse decision ship without an ADR because it wasn't caught during `/to-plan` or `/build`.
- Closing out a green review over a drifted chain — e.g. `spec.md` gained an `AC<n>` that was never planned, built, or tested. A false green is worse than an honest "not met." See `where/RECONCILE.md`.
