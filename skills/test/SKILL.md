---
name: test
description: Verifies a completed build against the spec's acceptance criteria. Only runs when the user explicitly types /test.
disable-model-invocation: true
---

# Test

## Overview

Check the implementation against `spec.md`'s acceptance criteria, one by one, with real evidence,
not a plausibility argument. This is behavioral verification, not code review. `/review` follows
this step with a final spec-conformance pass, and your existing code-review/security-review
tooling covers code quality separately.

## When to Use

Explicit invocation only (`/test`). Requires `specs/<slug>/spec.md` (for acceptance criteria) and a
`specs/<slug>/plan.md` whose tasks are all checked off.

## Where artifacts live

`specs/<slug>/` at the repo root, committed on the feature branch. This step writes the
**Verification** section of `specs/<slug>/review.md`, creating the file if needed, and commits it.
`/review` later adds its verdict to the same file.

## Process

1. Find `specs/<slug>/spec.md` and `specs/<slug>/plan.md`. If any task in `plan.md` is still
   unchecked, stop and tell the user to finish `/build` first.
2. For each acceptance criterion in the spec, actually exercise it. Run the test suite, run the
   feature, hit the endpoint, check the UI in a browser: whatever proves the behavior, not just
   reading the code.
3. Write the `## Verification` section of `specs/<slug>/review.md` (under a `# Review: <slug>`
   heading if you're creating the file). Give each criterion one line, **by its `AC<n>` ID**,
   with ✓/✗ and the evidence: a test name, a command and its result, or what you saw in the
   browser.
   ```
   - AC1 ✓ — `npx jest request-transfer-program` → 14/14 pass; header-fetch error aborts before modal opens
   - AC2 ✗ — modal still renders the raw error <div> on a 500
   ```
   - Cite each ID exactly as written in `spec.md`. If the spec has a criterion with no ID, flag
     it rather than inventing one.
   - Cover every `AC<n>`. A missing ID reads as untested.
   - Keep it to one line per AC. If a failure needs a longer explanation, give it in your reply
     to the user, not in the file.
   - If `review.md` already has a Verification section (a re-run), replace it rather than
     appending a second one.
   - If `review.md` also has a verdict from an earlier `/review`, that verdict is now stale.
     Remove it and say so; the verdict will be re-derived when `/review` runs.
4. Commit: `git add specs/<slug>/review.md` then
   `git commit -m "test(<slug>): verify ACs" -- specs/<slug>/review.md`.
5. If something fails, don't paper over it. Report it and tell the user to go back to `/build`
   (or `/to-plan` if the gap is a planning issue). If the failure reveals that the *spec itself*
   was wrong and an `AC<n>` should change, that's an upstream edit: change it via `/spec` and
   reconcile the chain per [where/RECONCILE.md](../where/RECONCILE.md). Never edit an AC from
   inside `/test` just to make it pass.
6. If everything passes, tell the user: "All acceptance criteria verified. Run `/review` for a
   final spec-conformance pass."
7. If this session is still worktree-isolated when this step ends, ask the user whether to keep
   or remove the worktree before finishing, per [docs/worktrees.md](../../docs/worktrees.md).

## Red Flags

- Marking a criterion as passing because the code "looks right", without running anything.
- Testing implementation details instead of the acceptance criteria as written in the spec.
- Quietly weakening an acceptance criterion to make it pass. Flag the mismatch to the user
  instead. A genuinely wrong AC is a `/spec` change plus reconciliation, not an in-place edit here.
- Pasting test logs or long explanations into `review.md`. One line of evidence per AC.
