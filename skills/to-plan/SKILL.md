---
name: to-plan
description: Turns an approved spec into a technical plan with a dependency-annotated task list that /build can run in parallel waves. Only runs when the user explicitly types /to-plan.
disable-model-invocation: true
model: opus
---

# To-Plan

## Overview

Turn `spec.md` into a concrete technical approach and an atomic task list, both in one file,
`plan.md`. The plan is where architectural decisions get made and reviewed, before any code.
It is also where you decide **which tasks can safely run at the same time**. `/build` trusts
those markings to dispatch tasks concurrently, so they have to be right.

(Named `to-plan` because Claude Code has a built-in `/plan` command.)

## When to Use

Explicit invocation only (`/to-plan`). Requires an existing `specs/<slug>/spec.md`.

**Don't bother for:** trivial changes where `/spec` was already skipped. Go straight to `/build`.

## Where artifacts live

`specs/<slug>/` at the repo root (`git rev-parse --show-toplevel`), committed on the feature
branch that `/spec` created. This step writes `specs/<slug>/plan.md` and commits it, along with
any new ADRs or `CONTEXT.md` changes. Artifacts are committed so that every later session, in
any worktree of this branch, sees them.

## Process

1. Find `specs/<slug>/spec.md`. If no slug is obvious from context, ask which feature this is
   for. If `spec.md` doesn't exist, stop and tell the user to run `/spec` first. Read
   `CONTEXT.md` (or `CONTEXT-MAP.md`) if it exists so the plan's vocabulary matches the project's.
2. Read the spec's requirements and acceptance criteria. Explore the codebase for existing
   utilities, patterns, and files this will touch. Prefer reuse over rewriting.
3. For any architectural fork (more than one reasonable way to build this), interview the user
   about it one decision at a time using the `grilling` skill rather than silently picking one.
   If confidence is still low after the interview, run `prototype` to de-risk the decision
   before locking the plan.

   For UI-bearing features this includes visual style (theme, color palette, typography) if
   `spec.md` didn't already pin it down. Don't reach for a stock framework theme just because
   it's the path of least resistance, especially when reference screenshots exist that were
   only ever asked about for layout.
4. Write `specs/<slug>/plan.md` using [PLAN-TEMPLATE.md](PLAN-TEMPLATE.md): Approach, Files
   touched, Key decisions, Tasks. Respect the template's length guidance. The earlier version
   of this pipeline produced tasks that restated the plan with code snippets, and nobody read
   them.
5. For each key decision, apply the `domain-modeling` skill's ADR test (hard to reverse,
   surprising without context, and a real trade-off). If all three hold, record it as an ADR
   rather than only noting it in `plan.md`. `plan.md` is feature-scoped; ADRs are permanent
   project memory.
6. **Break the work into tasks.** Use thin vertical slices, not "all the models, then all the
   views". Each task should be small enough to implement and verify in one sitting. Give each
   one a stable `T<n>` ID, the `AC<n>` IDs it serves, and its `files:` list. Also write the
   plan-level `Check:` command. Use exactly this shape, because `/build` and `/where` parse it:
   ```
   Check: `npm test`

   - [ ] **T2** Add the Markdown table formatter — AC1
         files: `src/formatters/markdown.js`, `test/markdown.test.js` · after: T1 · [P]
   ```
   The title line carries only the ID, the title, and the ACs. Everything else goes on the one
   indented metadata line: `files:`, then `after:` (omitted when there are no dependencies),
   then `[P]` (omitted when the task must run alone).
7. **Annotate for parallelism.** This is the part `/build` depends on most. For each task:
   - **`after:`** lists every task whose output it needs: a function it calls, a type it
     imports, a schema it migrates, a component it extends. A missing edge means `/build` may
     start the task before its dependency exists.
   - **`files:`** must be complete. Include the test file, the module or DI registration, the
     barrel `index` export, the route table. A file the task edits but doesn't list is an
     overlap `/build` can't see.
   - **`[P]`** goes only on tasks you'd be comfortable seeing run next to any other `[P]` task
     with disjoint files. Leave it off when the task:
     - touches a shared hotspot (lockfile, package manifest, `.csproj`/`.sln`, shared DI
       module, global styles or config, migrations, generated code), or
     - has verification that would contend with a concurrent run. Examples: two .NET tasks in
       the same project both running `dotnet build`/`dotnet test` fight over `obj/`/`bin/` file
       locks; tests that bind a fixed port or reset a shared database; snapshot updates.

   When unsure, leave `[P]` off. An unmarked task just runs alone, which costs time; a wrong
   `[P]` costs a corrupted working tree. Parallelism is worth it when a feature splits into
   genuinely independent slices. Don't bend the task breakdown to manufacture it.
8. If you're revising an existing `plan.md`, reconcile downstream per
   [where/RECONCILE.md](../where/RECONCILE.md). A changed approach or key decision may
   invalidate tasks and any build already done against the old approach. Update the affected
   tasks and flag already-built work that needs revisiting. New tasks get new IDs; dropped
   tasks' IDs are retired, never reused. Re-check the `after:`/`files:`/`[P]` annotations of
   every task the change touches. If you're re-planning because the *spec* changed, reconcile
   from there first. Don't patch the plan around a spec you haven't caught up to.
9. Commit the artifacts, staging only this feature's files so unrelated work in the tree isn't
   swept in:
   ```sh
   git add specs/<slug>/plan.md <each ADR / CONTEXT.md file you wrote>
   git commit -m "plan(<slug>): <one-line summary>" -- specs/<slug>/plan.md <same paths>
   ```
10. Show the user the plan (and any new ADRs), followed by the wave preview: how `/build` will
    schedule the tasks given your annotations. For example:
    ```
    Waves:  1 ▸ T1 ∥ T3 ∥ T5    2 ▸ T2 · T4 (alone: touches shared.module.ts)    3 ▸ T6
    ```
    The preview is for the user's review. It isn't written into `plan.md`, where it would drift
    from the annotations it's derived from. If this session is still worktree-isolated, ask the
    user whether to keep or remove the worktree before finishing, per
    [docs/worktrees.md](../../docs/worktrees.md). Stop. Tell them: "Review this, especially the
    `[P]` markings, and run `/build` once you're happy with it."

## Red Flags

- Skipping straight to task-writing without an Approach section. The plan needs a narrative,
  not just a checklist.
- Tasks that bundle multiple unrelated changes. Split them.
- Tasks that restate the plan: code blocks, multi-paragraph instructions, or step-by-step
  edits. A task is a title, its ACs, and a metadata line.
- Marking `[P]` by default, or on two tasks that share a file or a hotspot.
- A `files:` list that leaves out the test file or a registration/barrel file the task will
  obviously have to touch.
- Renumbering or reusing `T<n>` IDs on a re-plan.
- Introducing a new dependency or pattern not justified by the spec. Flag it as a decision; don't
  just do it.
- Defaulting to a stock theme or style for a UI-bearing feature without confirming it with the
  user.
- Making a hard-to-reverse architectural call without offering an ADR, or writing an ADR for
  something trivial or easily reversed. See `domain-modeling`'s three-part test.
- Revising `plan.md` without reconciling the tasks and already-built work derived from the old
  approach. See `where/RECONCILE.md`.
