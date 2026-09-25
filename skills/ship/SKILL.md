---
name: ship
description: Turns spec-conformant, reviewed work into a draft PR (deciding whether the spec artifacts ride along), then hands off to code-review/security-review. Only runs when the user explicitly types /ship.
disable-model-invocation: true
model: sonnet
---

# Ship

## Overview

The operational end of the pipeline. `/review` confirms the work matches the spec. `/ship`
turns it into a reviewable draft PR whose narrative comes straight from `spec.md` and
`review.md`, then points you at the code-quality and security gates this pipeline deliberately
leaves to dedicated tooling. By this point the feature branch (from `/spec`) and the per-task
commits (from `/build`) already exist, so `/ship` is mostly verification, one decision about
the spec artifacts, and the outward-facing steps. It does **not** itself review code.

## When to Use

Explicit invocation only (`/ship`). Requires a passing `/review`: a `specs/<slug>/review.md`
with every acceptance criterion met. Don't ship a feature whose review found unmet criteria.

## Where artifacts live

`specs/<slug>/` at the repo root, committed on the feature branch. This step writes no new
artifact. It decides with the user whether `specs/<slug>/` stays in the PR or is removed before it.

## Process

1. **Preconditions.** Find `specs/<slug>/`. Require `review.md`; if it's missing, stop and
   tell the user to run `/review` first. Read its per-`AC<n>` verdicts: if any criterion is
   "not met" (or only "partially met" without explicit user sign-off), stop and surface which
   — don't ship a feature that failed its own conformance gate. Read `spec.md` (Problem/Goals)
   and `review.md` (verdict, deviations, follow-ups) for the PR narrative.
2. **Branch.** You should already be on `feat/<slug>` (created by `/spec`). If you're on the
   default branch (`main`/`master`), stop: the feature's commits aren't where the pipeline
   expects them. Surface that rather than committing anything onto the default branch.
3. **Commits.** `/build` committed each task as `T<n>(<slug>): …`, and each step committed its
   artifact. Leave those commits alone; don't rewrite or squash them without a reason.
   - Run `git status --porcelain`. If anything is uncommitted, show it and ask. It may be a
     late fix that deserves its own honest commit, or stray work that doesn't belong in this PR.
   - End any commit you make with the co-author trailer this environment requires.
   - **Decide on the spec artifacts.** Ask the user whether `specs/<slug>/` should ship in the
     PR (useful context for reviewers; it lands on the default branch as feature documentation)
     or be removed first. If removing, commit it as its own step:
     `git rm -r specs/<slug>` then `git commit -m "chore(<slug>): drop spec artifacts"`. The
     artifacts stay reachable in the branch history (`git show <sha>:specs/<slug>/spec.md`).
     Mention that a squash merge will drop them from the default branch's history.
4. **Draft the PR body — don't create it yet.** Compose it from the artifacts, not from memory:
   - **What & why** — Problem/Goals from `spec.md`.
   - **Changes** — high level, from `plan.md` (its Approach and task list).
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
7. **Worktree.** If this session is still worktree-isolated when this step ends, ask the user
   whether to keep or remove the worktree before finishing, per
   [docs/worktrees.md](../../docs/worktrees.md).

## Red Flags

- Shipping a feature whose `/review` left an acceptance criterion unmet — stop and surface it.
- Committing anything onto `main`/`master`, or deciding for the user whether `specs/<slug>/`
  ships in the PR.
- Pushing or opening a PR without showing the user the commits and PR body and getting a
  go-ahead — these are public, outward-facing, hard-to-unsend actions.
- Running `/code-review` / `/security-review` yourself and calling them done, or merging the
  PR — `/ship` delegates and stops; those are separate, deliberate gates.
- Rewriting or squashing `/build`'s existing per-task commits without a reason to.
