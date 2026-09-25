---
name: spec
description: Writes a spec for a new feature or significant change. Only runs when the user explicitly types /spec.
disable-model-invocation: true
model: opus
---

# Spec

## Overview

Write a short spec before any code gets written. The spec is the contract between you and the user: what is being built, why, and how you will both know it is done.

Keep this file lean. Use the referenced resources for depth:

- [INTERVIEW-CHECKLIST.md](INTERVIEW-CHECKLIST.md) for coverage prompts
- [GREENFIELD-BASELINE.md](GREENFIELD-BASELINE.md) for new-project stack and environment details
- [SPEC-TEMPLATE.md](SPEC-TEMPLATE.md) for the spec structure

## When to Use

Explicit invocation only (`/spec`). Typical trigger: the user wants to start a new feature or a change big enough that requirements aren't already obvious.

**Don't bother for:** one-line fixes, typo corrections, or anything where `/to-plan` alone would be overkill — tell the user so and skip straight to implementing if they insist.

## Where artifacts live

`specs/<slug>/` at the repo root (`git rev-parse --show-toplevel`), committed on the feature branch
`feat/<slug>`, which this step creates. Every later step reads and commits its artifacts there, so any
session, including one in a worktree of that branch, sees the same files. This step writes
`specs/<slug>/spec.md` (plus any `CONTEXT.md` changes) and commits them.

## Process

1. Check that the project is under git (`git rev-parse --is-inside-work-tree`). If it isn't, stop and recommend `git init` plus an initial commit first. The pipeline commits each artifact on a feature branch, and later steps rely on that: `/build` commits per task, and a worktree only sees committed files. If the user wants to proceed without git anyway, honor it, but tell them the specs will be plain uncommitted files in `./specs/` and that worktree-isolated steps won't see them.
2. If `CONTEXT.md` (or `CONTEXT-MAP.md`) exists, read it first so your interview and spec use established terms.
3. Interview one question at a time using `grilling`. Use [INTERVIEW-CHECKLIST.md](INTERVIEW-CHECKLIST.md) so coverage is complete without turning this file into a giant script.
4. Use `domain-modeling` during the interview, not after it:
   - If terms are vague or conflicting, sharpen them immediately.
   - The moment a domain term is confirmed, capture it in `CONTEXT.md` right away.
5. If this is greenfield or the technical baseline is still unclear, capture it in the spec using [GREENFIELD-BASELINE.md](GREENFIELD-BASELINE.md). Treat these as delivery constraints, not deep architecture; keep hard technical trade-offs for `/to-plan` + ADRs.
6. If the feature has a UI, treat visual style (color, type, spacing, theme, tone) as unknown by default. Ask explicitly whether to match references stylistically, use framework defaults, or define a new style direction.
7. If a key product question is still ambiguous after interview (for example, unclear interaction model or uncertain state behavior), run `prototype` to answer that question before finalizing the spec. Capture the outcome as assumptions or requirements.
8. For reasonable inferences, state assumptions explicitly and give the user a chance to correct before writing the spec, for example:
   ```
   ASSUMPTIONS:
   1. This only affects the web app, not the mobile client
   2. No new external dependency needed
   → Correct me now or I'll proceed.
   ```
9. Pick a kebab-case slug for the feature and propose it to the user together with the branch name `feat/<slug>`. If you're on the default branch, create that branch (`git switch -c feat/<slug>`). If you're already on a feature branch, ask whether this feature belongs on it. Create `specs/<slug>/spec.md` using [SPEC-TEMPLATE.md](SPEC-TEMPLATE.md), including its length guidance.

   Do not add a "Domain Vocabulary" (or similarly-named) section to `spec.md` — canonical term definitions live in `CONTEXT.md` (via step 2), not here. `spec.md` should just use the established terms; if a definition would help a reader, reference `CONTEXT.md` rather than restating it.
10. If this feature already has downstream artifacts (`plan.md`, `review.md`) — i.e. you're revising a spec mid-pipeline, not writing a fresh one — reconcile them per [where/RECONCILE.md](../where/RECONCILE.md) before handing back. An added/removed/reworded requirement or `AC<n>` invalidates the plan, tasks, and any verification derived from the old spec; don't leave them silently stale. Tell the user which downstream artifacts your change touched and what needs re-running.
11. Commit the spec, staging only this feature's files: `git add specs/<slug>/spec.md [CONTEXT.md]` then `git commit -m "spec(<slug>): <one-line summary>" -- specs/<slug>/spec.md [CONTEXT.md]`. Revisions get their own commits the same way.
12. Show the user the spec (and any new or updated `CONTEXT.md`). If this session is still worktree-isolated, ask the user whether to keep or remove the worktree before finishing, per [docs/worktrees.md](../../docs/worktrees.md). Stop. Tell them: "Review this, and run `/to-plan` once you're happy with it."

## Red Flags

- Skipping the git check, or writing the spec straight onto the default branch instead of `feat/<slug>`.
- Leaving `spec.md` uncommitted. A worktree-isolated `/to-plan` or `/build` won't see it.
- Writing the spec before requirements are concrete — go back to asking questions.
- Using a term inconsistent with `CONTEXT.md` without flagging it — that's exactly the drift `domain-modeling` exists to catch.
- Writing domain term definitions into `spec.md` (e.g. a "Domain Vocabulary" section) instead of `CONTEXT.md` — this is easy to do by default on greenfield work where no `CONTEXT.md` exists yet to prompt the habit, but it's exactly the case `domain-modeling` needs to run for.
- For greenfield work, skipping technical baseline constraints (stack/runtime/deploy/data/observability) and leaving `/to-plan` to guess.
- Forcing a spec through while a central product question is still unresolved, when a quick `prototype` would de-risk it.
- Acceptance criteria that are vague ("works well", "is fast") — make them checkable.
- Writing acceptance criteria without stable `AC<n>` IDs, or renumbering existing ones when editing the spec — downstream `/test` and `/review` cite these IDs; renumbering silently breaks traceability. Append new IDs, never reuse or shift old ones.
- Proceeding to `/to-plan` yourself instead of stopping for approval.
- Revising an existing `spec.md` without reconciling the plan, tasks, and review that were derived from the old one — that silent drift is exactly the loop-back failure `where/RECONCILE.md` exists to prevent.
- Silently assuming a visual style (a default framework theme, or "matching the reference" without confirming how much of the reference) for a UI-bearing feature instead of asking.
