---
name: clean
description: Deletes completed features' spec artifacts from the shared git dir after confirmation, leaving in-flight work untouched. Only runs when the user explicitly types /clean.
disable-model-invocation: true
model: sonnet
effort: low
---

# Clean

## Overview

Housekeeping for the pipeline. Over time `<git-common-dir>/specs/` accumulates a folder per
feature, and finished ones just sit there. `/clean` finds the features that are **done**,
lists them, and — only after you confirm — removes their `specs/<slug>/` folders. It never
touches work that's still in flight, and it never deletes without showing you the list first.

This is the one pipeline skill that deletes. Deletion is irreversible (the artifacts are the
hand-off record and live inside `.git`, so there's no commit to revert), so the whole design
is "propose, confirm, then delete" — never "delete, then report."

## When to Use

Explicit invocation only (`/clean`). Typical trigger: after shipping one or more features, when
`/where`'s roll-up is cluttered with completed work you no longer need to track. If you want to
*see* status without removing anything, use `/where` — `/clean` is the destructive counterpart.

## Where artifacts live

Every `specs/<slug>/…` path below resolves under the repo's **shared git dir**, not the working tree:

```sh
SPECS="$(git rev-parse --path-format=absolute --git-common-dir)/specs"   # e.g. …/.git/specs
```

Storing artifacts there keeps them visible across every session and worktree — including the background-isolated steps Claude Code may switch into automatically — while making them impossible to accidentally commit. Outside a git repo, fall back to `./specs`.

## Process

1. **Locate features.** Resolve `SPECS` (above) and list `specs/*/` directories.
   - No `specs/` dir, or it's empty → report "Nothing to clean — no features on disk." and stop.
2. **Derive each feature's state** the same way `/where` does — read the artifacts, never guess
   from the conversation. A feature is a **deletion candidate** only when it is *complete*:
   - `review.md` exists, **and**
   - its per-`AC<n>` verdicts are all met (no "not met" / unresolved "partially met").

   Everything else is **in-flight** and off-limits: anything with no `review.md`, a review with
   unmet criteria, or an inconsistent/interrupted state (e.g. `plan.md` with no `tasks.md`).
3. **Check for drift before calling anything complete.** A green `review.md` can be stale — if
   `spec.md` grew or an AC was reworded after `/test`/`/review` ran, the feature only *looks*
   done (see `where/RECONCILE.md` for the signals). A drifted feature is **not** a clean
   deletion candidate: list it separately under a ⚠ and exclude it from the default selection,
   so a spec that quietly changed after review doesn't get swept away as "finished."
4. **Present the candidates and confirm.** Show two groups and stop for the user's choice:
   ```
   Complete — safe to delete:
     dark-mode     review ✓ (5/5 ACs met)
     csv-export    review ✓ (3/3 ACs met)

   ⚠ Complete but drifted (excluded by default — reconcile first):
     export-v2     review ✓ but spec.md has AC6 with no verification entry

   In flight — will NOT be touched:
     onboarding    build 3/7
   ```
   Ask which to delete. Default proposal: the "safe to delete" group only. Never preselect an
   in-flight or drifted feature; the user can override explicitly, but you must not.
5. **Confirm shipped, when it matters.** Deletion is irreversible and `review ✓` is not proof
   the work is merged. If you can cheaply tell a feature isn't shipped (no merged branch/PR for
   the slug), say so — the user may still want the artifacts as a reference. Let them decide;
   don't block, but don't hide it either.
6. **Delete only what was confirmed.** For each chosen slug, remove its `specs/<slug>/` folder
   (e.g. `rm -rf "$SPECS/<slug>"`). These live inside `.git` and aren't tracked, so there's no
   commit and no `.gitignore` to update — the removal is complete once the folder is gone.
   - Guard the path: only ever delete a `<slug>` subdirectory *inside* the resolved `SPECS`
     dir. Never `rm` `SPECS` itself, a parent, or anything outside it.
7. **Report.** State exactly which folders were deleted and what remains in flight, so the next
   `/where` matches expectations. If nothing was confirmed, say so and delete nothing.

## Red Flags

- Deleting anything before showing the list and getting an explicit go-ahead — `/clean` is
  propose-confirm-delete, never delete-then-report.
- Treating a feature as complete from memory of the conversation instead of reading `review.md`
  and its `AC<n>` verdicts — the files are the source of truth.
- Sweeping up a **drifted** feature (green review but a changed/reworded spec) as "finished" —
  it looks done and isn't; exclude it by default and point at reconciliation.
- Deleting in-flight or inconsistent work because the folder was "in the way" — if it's not
  provably complete, it's off-limits.
- `rm`-ing anything other than a confirmed `<slug>` folder inside the resolved `SPECS` dir —
  no parents, no globs that could escape, no `SPECS` root.
- Assuming `review ✓` means shipped and merged — flag unshipped features so the user doesn't
  lose an artifact they still wanted.
