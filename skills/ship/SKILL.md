---
name: ship
description: Turns spec-conformant, reviewed work into shippable git state — branch, commit per task, draft PR — then hands off to code-review/security-review. Only runs when the user explicitly types /ship.
disable-model-invocation: true
model: sonnet
---

# Ship

## Overview

The operational end of the pipeline. `/review` confirms the work matches the spec; `/ship`
turns it into reviewable git state — a feature branch, atomic commits mapped to the tasks,
and a draft PR whose narrative comes straight from `spec.md` and `review.md` — then points
you at the code-quality and security gates this pipeline deliberately leaves to dedicated
tooling. It does git mechanics and delegation; it does **not** itself review code.

## When to Use

Explicit invocation only (`/ship`). Requires a passing `/review`: a `specs/<slug>/review.md`
with every acceptance criterion met. Don't ship a feature whose review found unmet criteria.

## Where artifacts live

Every `specs/<slug>/…` path below resolves under the repo's **shared git dir**, not the working tree:

```sh
SPECS="$(git rev-parse --path-format=absolute --git-common-dir)/specs"   # e.g. …/.git/specs
```

Storing artifacts there keeps them visible across every session and worktree — including the background-isolated steps Claude Code may switch into automatically — while making them impossible to accidentally commit. Outside a git repo, fall back to `./specs`.

## Process

1. **Preconditions.** Find `specs/<slug>/`. Require `review.md`; if it's missing, stop and
   tell the user to run `/review` first. Read its per-`AC<n>` verdicts: if any criterion is
   "not met" (or only "partially met" without explicit user sign-off), stop and surface which
   — don't ship a feature that failed its own conformance gate. Read `spec.md` (Problem/Goals)
   and `review.md` (verdict, deviations, follow-ups) for the PR narrative.
2. **Branch.** Check the current branch. If it's the default branch (`main`/`master`), create
   a feature branch first — never commit the feature straight onto the default branch. Derive
   the name from the slug (e.g. `feat/<slug>`) and confirm it with the user. If already on a
   feature branch, use it.
3. **Commit.** Map the checked tasks in `tasks.md` to commits:
   - If `/build` already committed per task, leave those commits alone — skip to the PR.
   - If the work is sitting uncommitted, make one commit per task where the diff maps cleanly
     to that task's slice. Where it doesn't split cleanly, make honest, well-described commits
     and say so — don't fabricate per-task boundaries by chopping a single logical change
     across commits just to look tidy.
   - End each commit message with the co-author trailer this environment requires.
4. **Draft the PR body — don't create it yet.** Compose it from the artifacts, not from memory:
   - **What & why** — Problem/Goals from `spec.md`.
   - **Changes** — high level, from `plan.md` / `tasks.md`.
   - **Spec conformance** — the `/review` verdict (all `AC<n>` met).
   - **Follow-ups / out of scope** — from `review.md`'s open follow-ups.
   End the body with the Claude Code attribution line this environment requires.
5. **Confirm before anything outward-facing.** Show the user the branch, the commits, and the
   drafted PR body. Pushing and opening a PR are public, outward-facing actions — get an
   explicit go-ahead before each. Push and PR creation are separate capabilities; degrade by
   whichever is available rather than treating them as one step:
   - **Remote + `gh`** — push (confirm), then `gh pr create` with the drafted body (confirm).
   - **Remote, no `gh`** — push the branch (confirm), then hand the user the PR body to open the
     PR manually. Don't skip the push just because `gh` is absent.
   - **No remote** — stop after the local branch + commits and hand over the PR body as text.
6. **Hand off to the quality gates.** `/review` was spec-conformance only. Once the PR is up
   (or the commits are ready), recommend the passes this pipeline deliberately delegates:
   "Run `/code-review` and `/security-review` on the diff before merging." `/ship`'s job ends
   here — it does not run them itself, and it does not merge.

## Red Flags

- Shipping a feature whose `/review` left an acceptance criterion unmet — stop and surface it.
- Committing the feature directly onto `main`/`master` instead of branching first.
- Pushing or opening a PR without showing the user the commits and PR body and getting a
  go-ahead — these are public, outward-facing, hard-to-unsend actions.
- Fabricating artificial per-task commits by splitting one logical change across several —
  honest commits beat a fake-clean history.
- Running `/code-review` / `/security-review` yourself and calling them done, or merging the
  PR — `/ship` delegates and stops; those are separate, deliberate gates.
- Rewriting or squashing `/build`'s existing per-task commits without a reason to.
