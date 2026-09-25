---
name: where
description: Reports where a feature stands in the spec → plan → build → test → review pipeline by inspecting specs/<slug>/. Only runs when the user explicitly types /where.
disable-model-invocation: true
model: sonnet
effort: low
---

# Where

## Overview

Read-only pipeline status. Inspect `specs/<slug>/` and report which gate a feature
is at, how far `/build` has gotten, whether `/test` passed, and the single command
to run next. This skill never writes — it only tells you where you are.

## When to Use

Explicit invocation only (`/where`). Typical trigger: returning to a feature after a
break, or checking progress before deciding whether to run the next step. If nothing
is in flight, it says so and points at `/spec`.

## Where artifacts live

`specs/<slug>/` at the repo root (`git rev-parse --show-toplevel`), committed on each feature's
branch. A feature is only on disk while its branch is checked out, so features on other branches
are found through git (step 1). The three artifacts are:

- `spec.md`
- `plan.md`: Approach, Tasks with checkboxes and done-lines, and Deviations
- `review.md`: `/test`'s Verification, then `/review`'s Verdict

Occasionally there's also a `tasks/T<n>-slug.md` note file.

## Process

1. Locate features. Look for `specs/*/` directories in the working tree.
   - A slug is given or obvious from context → detail that one.
   - Exactly one feature here → detail it.
   - Several → print the one-line roll-up (below) for each, then ask which to detail. Don't
     dump full detail for all of them.
   - None here → check the other local branches cheaply
     (`git for-each-ref --format='%(refname:short)' refs/heads` then
     `git ls-tree -d --name-only <branch> specs/`) and list any features found as
     `<slug> (on <branch>)`, with "switch to that branch to continue". If there are none
     anywhere, report "No features in flight. Run `/spec` to start one." and stop.
2. For the feature(s), derive each gate's state from the artifacts. Never guess from memory of
   the conversation; always read the files.

   | Gate | Done when | In progress | Pending |
   |---|---|---|---|
   | spec | `spec.md` exists | — | no `spec.md` |
   | plan | `plan.md` has a Tasks section | `plan.md` exists with no tasks (flag as interrupted) | no `plan.md` |
   | build | every `T<n>` in `plan.md` is `- [x]` | some checked: report `checked/total`, plus the next wave (ready tasks per `after:`/`[P]`) | zero checked |
   | test | `review.md` has a **Verification** section and every `AC<n>` is ✓ | Verification exists but some ACs are ✗ or absent: report `passed/total` and name them | no Verification section |
   | review | `review.md` has a **Verdict** section | — | no Verdict |

3. Determine the next command: the first gate that is not `✓ done`, in pipeline order.
   - If **test failed** (Verification present but a criterion failed), recommend going
     back to `/build` (or `/to-plan` if the failure is a planning gap) — not forward.
   - If **review is done but not yet shipped** (no branch/PR for the feature), recommend
     `/ship` to turn the reviewed work into git state.
   - If the work is **shipped** (or the user isn't using `/ship`), report the pipeline
     complete and recommend the code-quality follow-ups it deliberately delegates:
     "Spec-conformance complete. Run `/code-review` and `/security-review` for code quality."
4. Surface inconsistencies plainly rather than smoothing them over:
   - a `plan.md` with no tasks
   - a Verification section written before all tasks are checked
   - uncommitted changes to source files mid-build (`git status --porcelain`), which usually
     means a `/build` wave was interrupted before its tasks were recorded
   - a task whose `after:` names a `T<n>` that doesn't exist These usually mean a step was interrupted or an
   upstream artifact changed — say which, don't silently pick a "current" gate.
5. **Detect chain drift** — the pipeline is a dependency chain (`spec → plan → tasks →
   Verification → review`), and an upstream edit silently invalidates everything downstream.
   Report drift as a ⚠ line, using the signals available:
   - **AC coverage (reliable):** every `AC<n>` in `spec.md` should have a line in
     `review.md`'s Verification section once `/test` has run. An AC with no verification entry means the
     spec grew after testing — flag the specific `AC<n>` as untested/stale.
   - **Commit order (good hint):** artifacts are committed, so `git log -1 --format=%ct -- <file>`
     per artifact tells you cheaply whether an upstream file (e.g. `spec.md`) was committed after
     a downstream one (e.g. `review.md`). Flag it as possible drift. It's a hint to verify, **not**
     proof: a typo fix also moves the timestamp.
   - **Blind spot to name:** a *reworded* AC keeps its ID and count, so no structural signal
     catches it. If you can't rule it out, say drift detection can't see reworded ACs and the
     safe move is to re-run `/test` after any AC edit.
   When drift is found, don't just report the gate — point the user at the reconciliation
   protocol in `where/RECONCILE.md` and recommend reconciling before advancing.

## Output format

One-line roll-up (used when listing multiple features):

```
dark-mode      spec ✓  plan ✓  build 3/7  test —  review —   → next: /build
csv-export     spec ✓  plan ✓  build ✓    test ✓  review ✓   → complete
```

Detailed view (single feature):

```
specs/dark-mode/

  spec    ✓ done
  plan    ✓ done
  build   3/7 tasks
  test    — pending
  review  — pending

Next: /build — next wave ▸ T4 ∥ T5, then T6, T7
  - [ ] T4 Wire theme toggle to system preference
  - [ ] T5 Persist choice to localStorage
  - [ ] ...
```

Detailed view with drift (spec edited after downstream was built):

```
specs/csv-export/

  spec    ✓ done
  plan    ✓ done
  build   ✓ done
  test    ✓ done (5/5)
  review  ✓ done

⚠ Drift: spec.md has AC6, but the Verification section only covers AC1–AC5.
  The spec grew after /test ran — review.md is now stale too.
  Reconcile before trusting the ✓s: see where/RECONCILE.md
  (likely re-run /test for AC6, then /review).
```

Keep it to the status block plus the next-command line (and a ⚠ drift line only when there
is drift). This is a checkpoint, not a report.

## Red Flags

- Inferring a gate's state from the conversation instead of reading the artifacts — the
  files are the source of truth; the conversation may be stale or from another session.
- Reporting `test ✓` when tasks are still unchecked, or `review ✓` when `review.md` has only a
  Verification section. Read the actual markers; don't round up.
- Writing to any file. `/where` is read-only; if the state is inconsistent, report it and
  let the user decide which step to re-run.
- Auto-running the recommended next command — this skill reports and stops.
- Reporting all gates `✓` while ignoring drift — a green chain with a stale downstream
  artifact is worse than an obviously-incomplete one, because it reads as trustworthy. If an
  upstream artifact changed after a downstream one, the ⚠ drift line is the most important
  thing on screen.
