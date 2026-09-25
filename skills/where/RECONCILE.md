# Reconciliation Protocol

The pipeline's artifacts form a dependency chain. Changing one invalidates everything
downstream of it. When you edit an artifact that already has downstream artifacts, reconcile
them in the **same pass** — don't leave the chain silently drifted. This is what makes the
pipeline safe to loop back through instead of being strictly one-way.

Referenced by `/spec`, `/to-plan`, `/build`, `/test`, `/review` (when a change forces a loop-back)
and by `/where` (which detects drift and points here).

## The chain

```
spec.md  →  plan.md (Approach → Tasks)  →  build (T<n> commits)  →  review.md (Verification → Verdict)
```

Each arrow means "derived from." A change to any box may invalidate everything to its
**right**. Nothing to its **left** is affected.

## When you change an artifact, recheck downstream

| Changed | Recheck / re-derive downstream |
|---|---|
| **spec.md**: a requirement, an `AC<n>` added / removed / reworded, scope | `plan.md` Approach (does it still hold?) and Tasks (add tasks for new or changed ACs, drop tasks for removed ones), Verification (re-test any changed AC), Verdict (now stale; re-run after) |
| **plan.md Approach / Key decisions** | Tasks (do they still implement this approach?), any build already done against the old approach, Verdict |
| **plan.md Tasks**: added / removed / reshaped a task | build (implement or undo the delta), Verification (does the changed behavior still meet its AC?), and the `after:` / `files:` / `[P]` annotations of every task that depends on or runs alongside the changed one. A reshaped task can quietly turn a safe parallel pair into a collision. IDs are append-only, so done-lines and `tasks/T<n>-slug.md` pointers never need renaming. A removed task's note file is deleted with it. |
| **build**: deviated from the plan while implementing | `plan.md` Deviations (record it there, not only in the code), then `/review` will check it |

**Only cascade when meaning changes.** Fixing a typo in spec prose, or clarifying wording
that doesn't change what's required, invalidates nothing — don't manufacture reconciliation work.

## How to reconcile each downstream artifact

For every artifact to the right of the change, pick one — never leave one in an unknown state:

1. **Re-run its step** — the honest default when the change is substantive. Changed an AC?
   Re-run `/test` for it. Reshaped the approach? Re-run the affected part of `/to-plan`.
2. **Targeted edit + re-validate** — when the change is small and localised, edit the
   downstream artifact directly and confirm it still holds, rather than regenerating it whole.
3. **Explicitly confirm still-valid** — sometimes an upstream change genuinely doesn't touch a
   given downstream artifact. Say so out loud ("`plan.md` unaffected — the new `AC7` is covered
   by existing task 4") rather than silently assuming it.

## Acceptance-criteria changes are the sharp edge

Because ACs carry stable IDs (`AC<n>`), added and removed ones are easy to track: `/where`
catches an AC with no line in `review.md`'s Verification. But a **reworded** AC keeps its ID and count, so
drift detection can't see it structurally. After any change to an AC's *meaning*, re-run
`/test` for that AC and re-check it in `/review`. Don't rely on `/where` to catch a reword.

## Recording

Reconcile synchronously and there's nothing stale to record. The artifacts are the source of
truth, they're back in sync, and git history already shows what changed and when: commit the
reconciled artifacts together, with a message naming the upstream change. If a mid-pipeline change was significant enough that a future
reader would be confused ("why did the approach change?"), that's usually an ADR (see
`domain-modeling`), not a note in these disposable per-feature artifacts.
