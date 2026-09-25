# Worktree Lifecycle

`EnterWorktree`/`ExitWorktree` give a session an isolated git worktree — its own working
directory, sharing the one `.git`. This pipeline never calls them itself; when a session *does*
end up worktree-isolated (by user request or project-level direction), these are the rules for
using that isolation without leaving a mess for the next session.

Referenced by `README.md` and by each pipeline skill's `SKILL.md`
(`spec`, `to-plan`, `build`, `test`, `review`, `ship`).

## Entry and exit are user-instruction-only

`EnterWorktree` and `ExitWorktree` are only ever invoked on explicit user instruction, or explicit
project-level direction (CLAUDE.md, memory). No skill in this pipeline calls either tool on its
own initiative as part of its normal process — this is also how both tools already constrain
themselves: `EnterWorktree`'s own description limits it to being used when a user or project
instruction explicitly asks for a worktree, and `ExitWorktree` says not to call it proactively,
only when asked.

Don't treat "this step is running as a background job" or "this looks like a good place to
isolate" as license to call either tool unprompted. If isolation is warranted, say so and let the
user (or CLAUDE.md) direct it.

## Never `cd` into the target directory before calling `EnterWorktree`

Always invoke `EnterWorktree` itself — via `name` for a new worktree, or `path` for an existing
one — from *outside* the target directory. Never manually `cd` into a worktree path via `Bash`
first, whether as a substitute for `EnterWorktree` or as a step before calling it.

Background: in the incident that prompted this doc, a session `cd`'d into a worktree path via
`Bash`, then called `EnterWorktree` on that same path. The tool errored "already the current
working directory" — which reads like a harmless no-op, but it means the tool never actually ran
and the session's isolation flag was never set. Everything downstream looked normal until task
subagents dispatched later hit inconsistent `Edit`/`Write` refusals, because the session was never
really isolated in the first place. The cwd-resolution behavior behind this is a Claude Code
harness internal, not something this doc can fix — the guidance is to never put yourself in a
position to hit it: call `EnterWorktree` first, from the original directory.

## Ask before ending a session that's still worktree-isolated

If a pipeline step's session is about to end while it's still worktree-isolated, don't let that
silently carry into the next step's session. Proactively ask the user whether to keep or remove
the worktree — `ExitWorktree`'s `keep` and `remove` actions — before the session ends.

Background: in the incident, a worktree created during `/plan` (now `/to-plan`) was left locked and unresolved
because nothing in the process asked what to do with it. It later collided with a `/build` run
that tried to use the same worktree. Asking before the session ends is what closes that gap.

## Artifacts committed in a worktree live on the worktree's branch

The pipeline commits its artifacts (and `/build` commits each task) on the current branch. A
worktree usually has its own branch, so a step that runs worktree-isolated commits there, not on
`feat/<slug>`. When asking the keep/remove question at the end of such a session, also tell the
user which pipeline commits exist only on the worktree's branch. Those commits need to reach the
feature branch (a fast-forward or merge) before the next step runs anywhere else, or that step
won't see them. Don't recommend `remove` until they have.

## A locked worktree is a stop, not a workaround

If a target worktree turns out to already be locked — for example `git worktree list` shows it
locked by another running session — don't silently branch off it, don't assume isolation
succeeded anyway, and don't route around the lock. Surface the lock to the user and let them
decide: create a fresh worktree, branch off the locked one's tip, or wait for the other session to
finish.

This is the same principle as the other three points: isolation state is never inferred or
assumed. When something about entering, holding, or leaving a worktree isn't unambiguous, that's a
question for the user, not a judgment call to make silently.
