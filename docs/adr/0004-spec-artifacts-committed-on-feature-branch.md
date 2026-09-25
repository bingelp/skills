# Spec artifacts are committed on the feature branch, not stored in `.git/specs`

Pipeline artifacts now live in `specs/<slug>/` at the repo root and are committed on `feat/<slug>`, which `/spec` creates. Each step commits its own artifact, `/build` commits once per task, and `/ship` asks whether the folder rides along in the PR or is removed first. This reverses the earlier choice (commit f31c17f) of an untracked `<git-common-dir>/specs/`.

## Considered options

- **`<git-common-dir>/specs` (previous)**: visible from every worktree and never committed. But it was invisible in the IDE and to teammates, lost on re-clone, and outside the worktree root. That made `Edit`/`Write` refuse and forced a sanctioned Bash-heredoc workaround, which cut against the pipeline's own "don't route around refusals" rule.
- **Gitignored working-tree `specs/`**: easy to browse, but invisible to any worktree, which was the reason for moving to `.git/specs` in the first place.
- **User-level `~/.claude/specs/<repo>/<slug>`**: never in diffs, but outside the project, so it triggers permission prompts and has no link to a branch.
- **Committed `specs/` on the feature branch (chosen)**: the spec-kit/Kiro norm. Committed files reach every worktree of the branch, edits hit no isolation guard, and git history replaces mtime guesswork for drift detection.

## Consequences

- A feature's artifacts exist on disk only while its branch is checked out. `/where` and `/tally` also look on other local branches.
- A worktree on a *different* branch doesn't see the feature's latest artifact commits until they're merged across. See `docs/worktrees.md`.
- `/clean` is now a `git rm` plus a commit, so removal is recoverable.
