---
name: test
description: Verifies a completed build against the spec's acceptance criteria. Only runs when the user explicitly types /test.
disable-model-invocation: true
---

# Test

## Overview

Check the implementation against `spec.md`'s acceptance criteria, one by one, with real evidence — not a plausibility argument. This is behavioral verification, not code review: `/review` follows this step for a final spec-conformance pass, and your existing code-review/security-review tooling covers code quality separately.

## When to Use

Explicit invocation only (`/test`). Requires `specs/<slug>/spec.md` (for acceptance criteria) and a `specs/<slug>/tasks.md` with all tasks checked off.

## Where artifacts live

Every `specs/<slug>/…` path below resolves under the repo's **shared git dir**, not the working tree:

```sh
SPECS="$(git rev-parse --path-format=absolute --git-common-dir)/specs"   # e.g. …/.git/specs
```

Storing artifacts there keeps them visible across every session and worktree — including the background-isolated steps Claude Code may switch into automatically — while making them impossible to accidentally commit. Outside a git repo, fall back to `./specs`.

## Process

1. Find `specs/<slug>/spec.md` and `specs/<slug>/tasks.md`. If tasks aren't all checked off, stop and tell the user to finish `/build` first.
2. For each acceptance criterion in the spec, actually exercise it: run the test suite, run the feature, hit the endpoint, check the UI in a browser — whatever proves the behavior, not just reading the code.
3. Append a **Verification** section to `specs/<slug>/tasks.md` listing each acceptance criterion **by its `AC<n>` ID** with a pass/fail and the evidence (test name, command output, screenshot description). Cite the ID exactly as written in `spec.md`; if the spec has a criterion with no ID, flag it rather than inventing one. Cover every `AC<n>` in the spec — a missing ID in your Verification section reads as untested.
4. If something fails, don't paper over it — report it and tell the user to go back to `/build` (or `/plan` if the gap is a planning issue). If the failure reveals the *spec itself* was wrong and an `AC<n>` should change, that's an upstream edit: change it via `/spec` and reconcile the chain per [where/RECONCILE.md](../where/RECONCILE.md) — re-plan/re-build/re-test as the change requires. Never edit an AC from inside `/test` just to make it pass.
5. If everything passes, tell the user: "All acceptance criteria verified. Run `/review` for a final spec-conformance pass."

## Red Flags

- Marking a criterion as passing because the code "looks right" without running anything.
- Testing implementation details instead of the acceptance criteria as written in the spec.
- Quietly weakening an acceptance criterion to make it pass — flag the mismatch to the user instead. A genuinely wrong AC is a `/spec` change plus reconciliation (`where/RECONCILE.md`), not an in-place edit here.
