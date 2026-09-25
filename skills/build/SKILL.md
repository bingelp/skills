---
name: build
description: Implements an approved plan's tasks by dispatching task-builder subagents, in parallel waves where /to-plan marked it safe, and commits each task. Only runs when the user explicitly types /build.
disable-model-invocation: true
model: sonnet
---

# Build

## Overview

This session is the **build orchestrator**. It never implements a task itself. It reads the Tasks
in `specs/<slug>/plan.md` and hands each one to a disposable **task subagent**, several at once
when the plan says that's safe. It then checks what each subagent touched, records a done-line,
and commits the task. Implementation work happens in the subagents' contexts, so this session's
context grows with the number of tasks, not with every file read and edit across the feature.

## When to Use

Explicit invocation only: `/build`, or `/build sequential` to run one task at a time regardless of
`[P]` markings. Requires `specs/<slug>/plan.md` with a Tasks section.

## Where artifacts live

`specs/<slug>/` at the repo root, committed on the feature branch. This step edits `plan.md` (done-lines,
Deviations), occasionally writes `specs/<slug>/tasks/T<n>-slug.md`, and makes **one commit per task**,
containing the task's code and its done-line together. A checked task is always a committed task,
which is what makes an interrupted build safe to resume.

## The task subagent

Dispatch tasks with `subagent_type: task-builder`. The definition lives in
[agents/task-builder.md](agents/task-builder.md) and is installed by symlinking it into
`~/.claude/agents/` (see the README). It carries the standing rules, so your brief only has to
carry the task-specific context:

- stay inside its own `files:`
- never touch git
- verify narrowly
- stop and report on blockers
- return a fixed-shape report

If `task-builder` isn't among the available agent types, use `general-purpose` instead and paste
the body of `agents/task-builder.md` (everything below its frontmatter) at the top of each brief.
It's the same contract, just not preinstalled. Mention once to the user that the agent isn't
installed.

## Process

1. **Preconditions.**
   - Find `specs/<slug>/plan.md`. If it's missing, stop and tell the user to run `/to-plan` first.
   - Read its Approach, Key decisions, Tasks, and `Check:` line, plus `CONTEXT.md` and any ADRs
     relevant to the area. This is context for the briefs, not something to act on yourself.
   - If you're on the default branch (`main`/`master`), stop and ask. `/spec` should have
     created `feat/<slug>`, and per-task commits must never land on the default branch.
   - Run `git status --porcelain`. If anything is uncommitted outside `specs/<slug>/`, stop and
     ask the user to commit or stash it. Per-task commits and the file-claim check in step 4
     both need a clean baseline. This is usually leftover work from an interrupted wave: list
     those files and let the user decide.
2. **Pick the next wave.** A task is *ready* when it's unchecked and every task in its `after:`
   is checked.
   - Take the lowest-ID ready task. If it isn't `[P]`, it runs alone.
   - If it is `[P]`, add the other ready `[P]` tasks in ID order, skipping any whose `files:`
     overlap a task already in the wave. Stop at 4 tasks. More than that tends to thrash
     shared machines and makes a failing `Check:` harder to attribute.
   - Run everything one task at a time if the user passed `sequential`, or if the plan has no
     `files:`/`[P]` annotations (an older plan). Unannotated means unknown, not safe.
   - If tasks remain unchecked but none is ready, the `after:` graph has a cycle or points at a
     task that doesn't exist. Stop and report it.

   Before dispatching, tell the user the wave in one line: `Wave 2 ▸ T2 ∥ T5`.
3. **Dispatch.** Make one `Agent` call per task in the wave, all in the **same message**, so
   they run concurrently. Don't use the `Workflow` tool or `/loop` (see ADRs 0001 and 0003).
   - **Then wait for the whole wave.** Subagents may run asynchronously. Each one's report
     arrives as a completion notification, and you're re-invoked when it does. Don't poll, sleep,
     or schedule wakeups. Acknowledge each report briefly, and move to step 4 only once every task
     in the wave has reported.
   - Pass `model: X` when the task has a `` `[model: X]` `` tag. Otherwise omit it.
   - Each brief contains:
     - the task's lines from `plan.md`, verbatim: ID, title, ACs, and metadata
     - `plan.md`'s Approach and Key decisions, verbatim rather than summarized, plus the
       `Check:` command
     - paths to `CONTEXT.md` and the relevant ADRs, for the subagent to read itself
     - the done-lines (and note-file paths, if any) of the tasks in its `after:`, so it knows
       what it builds on without reading their transcripts
     - in a parallel wave, the sibling tasks' IDs and `files:` lists, marked off-limits
4. **Check the reports.** After the wave returns, run `git status --porcelain` and compare it
   with the `FILES` each subagent reported.
   - Every changed path must be claimed by exactly one task in this wave. An unclaimed change,
     or a path two tasks both changed, is a **collision**. Commit neither task involved. Stop
     and show the user the paths. The plan's annotations were wrong, and that's worth knowing
     before the next wave.
   - A task that changed a file outside its planned `files:` without colliding is fine. If the
     file is a hotspot the plan didn't anticipate (manifest, lockfile, shared module), record
     it as a Deviation so `/review` sees it.
5. **Record and commit**, one finished task at a time in ID order:
   - Flip its checkbox to `[x]` and add one `done:` line under it, indented like the metadata
     line: `done: <what changed, in about a dozen words> · <verification command> → <result>`.
     For example: `done: rethrows case-normalized error; spec asserts rethrow · npx jest applications → 8/8 pass`.
     Trim the report's `SUMMARY`/`VERIFIED` to fit. The done-line is a pointer, not a changelog;
     the commit holds the diff.
   - Write a note file only if the report's `NOTE` holds more than would fit in about two lines
     of `plan.md`: a deviation's reasoning, a non-obvious decision, or evidence beyond "tests
     pass". Put it in `specs/<slug>/tasks/T<n>-slug.md` and end the done-line with
     `— see tasks/T<n>-slug.md`. Most tasks get no note file. The point is that `plan.md` stays
     readable no matter how much a single task has to say.
   - If the report has a `DEVIATION`, add one line for it under `## Deviations` in `plan.md`
     (create the section if it's absent).
   - Commit the task:
     ```sh
     git add <the task's reported FILES> specs/<slug>/plan.md [specs/<slug>/tasks/T<n>-slug.md]
     git commit -m "T<n>(<slug>): <summary>"
     ```
     You edit `plan.md` for one task, then commit, then move to the next, so each commit
     carries exactly that task's done-line.
6. **Integration check.** After any wave that ran more than one task, run the plan's `Check:`
   command with its output trimmed (e.g. `… 2>&1 | tail -40`), so a long test log doesn't land
   in this context. Each subagent verified its own slice; this catches the slices disagreeing
   with each other. If it fails:
   - Don't start the next wave.
   - Report the failing output and which tasks ran together.
   - Ask the user whether to dispatch a fix task or re-plan.
7. **Blockers.** If a subagent reports `STATUS: blocked`, still record and commit its finished
   wave-mates, since their work is independent. Then halt: dispatch nothing further and surface
   the blocker to the user rather than improvising a design decision.
   - If resolving the blocker means `plan.md` (or `spec.md`) is now wrong, fix the artifact
     through the owning step and reconcile downstream per
     [where/RECONCILE.md](../where/RECONCILE.md) before resuming.
   - If the blocker was resolved by a hard-to-reverse decision made on the fly, use
     `domain-modeling` to decide whether it needs an ADR.
8. Otherwise, go back to step 2.
9. When every task is checked, run `Check:` once more (unless the last wave just ran it). Then
   tell the user: "All tasks complete. Run `/test` to verify against the spec's acceptance
   criteria."
10. If this session is still worktree-isolated when it ends, whether because the build finished
    or because it halted on a blocker, ask the user whether to keep or remove the worktree
    before finishing, per [docs/worktrees.md](../../docs/worktrees.md).

## Red Flags

- Implementing a task yourself instead of dispatching it. Keep source-file `Read`/`Edit`/`Bash`
  work out of this session's context.
- Putting two tasks in the same wave when either lacks `[P]` or their `files:` overlap, or
  inferring parallel-safety yourself when the plan didn't mark it. `/to-plan` owns that
  judgement, and the user reviewed it there.
- Dispatching a wave's tasks in separate messages (they'd run one after another), or checking
  and committing a wave before every one of its subagents has reported.
- Polling for subagents with `sleep`, `ScheduleWakeup`, or repeated status checks. Their reports
  arrive on their own.
- Committing a task whose changed files collide with a sibling's, or sweeping unclaimed changes
  into some task's commit.
- Starting the next wave after a failed `Check:` or a collision.
- Checking a task off without a commit, or committing without checking it off. The two have to
  move together for resume to work.
- Writing a task's full story into `plan.md`. It gets one done-line; anything longer goes in
  `tasks/T<n>-slug.md`.
- Creating a note file for a task that has nothing to say beyond "done, tests pass".
- Letting a subagent reconcile `plan.md`/`spec.md` itself. It reports the blocker; the
  reconciliation is your call and the user's.
- Introducing a term for something `CONTEXT.md` already names, or quietly contradicting a
  recorded ADR.
- Resuming against a plan that's been silently revised without reconciling it. See
  `where/RECONCILE.md`.
