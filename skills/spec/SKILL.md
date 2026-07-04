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

**Don't bother for:** one-line fixes, typo corrections, or anything where `/plan` alone would be overkill — tell the user so and skip straight to implementing if they insist.

## Process

1. If `CONTEXT.md` (or `CONTEXT-MAP.md`) exists, read it first so your interview and spec use established terms.
2. Interview one question at a time using `grilling`. Use [INTERVIEW-CHECKLIST.md](INTERVIEW-CHECKLIST.md) so coverage is complete without turning this file into a giant script.
3. Use `domain-modeling` during the interview, not after it:
   - If terms are vague or conflicting, sharpen them immediately.
   - The moment a domain term is confirmed, capture it in `CONTEXT.md` right away.
4. If this is greenfield or the technical baseline is still unclear, capture it in the spec using [GREENFIELD-BASELINE.md](GREENFIELD-BASELINE.md). Treat these as delivery constraints, not deep architecture; keep hard technical trade-offs for `/plan` + ADRs.
5. If the feature has a UI, treat visual style (color, type, spacing, theme, tone) as unknown by default. Ask explicitly whether to match references stylistically, use framework defaults, or define a new style direction.
6. If a key product question is still ambiguous after interview (for example, unclear interaction model or uncertain state behavior), run `prototype` to answer that question before finalizing the spec. Capture the outcome as assumptions or requirements.
7. For reasonable inferences, state assumptions explicitly and give the user a chance to correct before writing the spec, for example:
   ```
   ASSUMPTIONS:
   1. This only affects the web app, not the mobile client
   2. No new external dependency needed
   → Correct me now or I'll proceed.
   ```
8. Pick a kebab-case slug for the feature. Create `specs/<slug>/spec.md` using [SPEC-TEMPLATE.md](SPEC-TEMPLATE.md).

   Do not add a "Domain Vocabulary" (or similarly-named) section to `spec.md` — canonical term definitions live in `CONTEXT.md` (via step 2), not here. `spec.md` should just use the established terms; if a definition would help a reader, reference `CONTEXT.md` rather than restating it.
9. If this feature already has downstream artifacts (`plan.md`, `tasks.md`, `review.md`) — i.e. you're revising a spec mid-pipeline, not writing a fresh one — reconcile them per [where/RECONCILE.md](../where/RECONCILE.md) before handing back. An added/removed/reworded requirement or `AC<n>` invalidates the plan, tasks, and any verification derived from the old spec; don't leave them silently stale. Tell the user which downstream artifacts your change touched and what needs re-running.
10. Show the user the spec (and any new/updated `CONTEXT.md`). Stop. Tell them: "Review this, and run `/plan` once you're happy with it."

## Red Flags

- Writing the spec before requirements are concrete — go back to asking questions.
- Using a term inconsistent with `CONTEXT.md` without flagging it — that's exactly the drift `domain-modeling` exists to catch.
- Writing domain term definitions into `spec.md` (e.g. a "Domain Vocabulary" section) instead of `CONTEXT.md` — this is easy to do by default on greenfield work where no `CONTEXT.md` exists yet to prompt the habit, but it's exactly the case `domain-modeling` needs to run for.
- For greenfield work, skipping technical baseline constraints (stack/runtime/deploy/data/observability) and leaving `/plan` to guess.
- Forcing a spec through while a central product question is still unresolved, when a quick `prototype` would de-risk it.
- Acceptance criteria that are vague ("works well", "is fast") — make them checkable.
- Writing acceptance criteria without stable `AC<n>` IDs, or renumbering existing ones when editing the spec — downstream `/test` and `/review` cite these IDs; renumbering silently breaks traceability. Append new IDs, never reuse or shift old ones.
- Proceeding to `/plan` yourself instead of stopping for approval.
- Revising an existing `spec.md` without reconciling the plan, tasks, and review that were derived from the old one — that silent drift is exactly the loop-back failure `where/RECONCILE.md` exists to prevent.
- Silently assuming a visual style (a default framework theme, or "matching the reference" without confirming how much of the reference) for a UI-bearing feature instead of asking.
