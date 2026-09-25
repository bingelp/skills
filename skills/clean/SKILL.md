---
name: clean
description: Removes completed features' committed spec artifacts (git rm + one commit) after confirmation, leaving in-flight work untouched. Only runs when the user explicitly types /clean.
disable-model-invocation: true
model: sonnet
effort: low
---

# Clean

## Overview

Housekeeping for the pipeline. When `/ship` keeps a feature's `specs/<slug>/` in its PR, the
folder lands on the default branch and stays there. Over time `specs/` fills with finished
features. `/clean` finds the ones that are **done**, lists them, and, only after you confirm,
removes their folders in a single commit. It never touches work that's still in flight, and it
never removes anything without showing you the list first.

The artifacts are committed, so removal is recoverable from history. It's still
"propose, confirm, then remove", never "remove, then report": a surprise commit that deletes
documentation someone was relying on is its own kind of mess.

## When to Use

Explicit invocation only (`/clean`). Typical trigger: after shipping one or more features, when
`/where`'s roll-up is cluttered with completed work you no longer need to track. If you want to
*see* status without removing anything, use `/where` — `/clean` is the destructive counterpart.

## Where artifacts live

`specs/<slug>/` at the repo root (`git rev-parse --show-toplevel`), committed. `/clean` works on the
currently checked-out branch, usually the default branch after features have merged.

## Process

1. **Locate features.** List `specs/*/` directories at the repo root.
   - No `specs/` dir, or it's empty → report "Nothing to clean — no features on disk." and stop.
   - If the working tree has uncommitted changes under `specs/`, stop and ask. The removal is one commit, and it shouldn't sweep in someone's pending edits.
2. **Derive each feature's state** the same way `/where` does — read the artifacts, never guess
   from the conversation. A feature is a **deletion candidate** only when it is *complete*:
   - `review.md` has a Verdict section, **and**
   - its per-`AC<n>` verdicts are all met (no "not met" / unresolved "partially met").

   Everything else is **in-flight** and off-limits: anything with no `review.md`, a review with
   unmet criteria, or an inconsistent/interrupted state (e.g. unchecked tasks in `plan.md`).
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
5. **Confirm merged, when it matters.** `review ✓` is not proof the work is merged. If a feature's
   folder exists but its `feat/<slug>` branch is unmerged (`git branch --no-merged`), say so. The
   user may still want the artifacts in place. Let them decide; don't block, but don't hide it.
6. **Remove only what was confirmed**, in one commit:
   ```sh
   git rm -r -- specs/<slug-a> specs/<slug-b>
   git commit -m "chore(specs): remove completed features <slug-a>, <slug-b>"
   ```
   - Guard the paths: only ever remove confirmed `specs/<slug>` subdirectories, never `specs/`
     itself, a parent, or a glob that could match more than you listed.
   - Mention that the folders are recoverable (`git show <commit>^:specs/<slug>/spec.md`) and
     that the commit isn't pushed. Pushing is the user's call.
7. **Report.** State exactly which folders were removed, the commit, and what remains in flight, so the
   next `/where` matches expectations. If nothing was confirmed, say so and remove nothing.

## Red Flags

- Removing anything before showing the list and getting an explicit go-ahead. `/clean` is
  propose-confirm-remove, never remove-then-report.
- Treating a feature as complete from memory of the conversation instead of reading `review.md`
  and its `AC<n>` verdicts — the files are the source of truth.
- Sweeping up a **drifted** feature (green review but a changed/reworded spec) as "finished" —
  it looks done and isn't; exclude it by default and point at reconciliation.
- Deleting in-flight or inconsistent work because the folder was "in the way" — if it's not
  provably complete, it's off-limits.
- Removing anything other than a confirmed `specs/<slug>` folder: no parents, no globs that could
  escape, no `specs/` root. Also sweeping unrelated staged changes into the removal commit.
- Assuming `review ✓` means merged. Flag unmerged features so the user doesn't lose an artifact
  they still wanted.
