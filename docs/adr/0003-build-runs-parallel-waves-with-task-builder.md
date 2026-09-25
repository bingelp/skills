# `/build` runs tasks in parallel waves via a dedicated `task-builder` agent

`/to-plan` now annotates each task with `after:` (dependencies), `files:` (what it claims), and an explicit `[P]` when it's safe to run alongside others. `/build` dispatches ready `[P]` tasks with disjoint files together (up to 4 per wave), as concurrent `Agent` calls in one message, then waits for every report. Unmarked tasks still run alone. Every task subagent is a `task-builder` agent, whose standing contract is: stay inside your own `files:`, run no state-changing git, verify narrowly, and return a fixed-shape report. The orchestrator stays the only writer of git and `specs/`. This supersedes the "strictly sequential" part of ADR-0001. The orchestrator/subagent split and the `Agent` mechanism stand. (`Agent` calls may now complete asynchronously via notifications rather than blocking, so the orchestrator waits for the wave's reports instead of relying on a blocking call for ordering.)

## Considered options

- **Sequential only (status quo)**: safe, but independent slices wait on each other for no reason.
- **One worktree per parallel task, merged back**: the strongest isolation, but it costs merge conflicts and a per-worktree `npm install`/`dotnet restore`, and it cuts against `docs/worktrees.md`'s rule that the pipeline never isolates on its own initiative.
- **Shared tree, `/build` infers safety from file overlap alone**: file overlap misses shared hotspots and contending verification (e.g. two `dotnet test` runs locking the same `obj/`). So the judgement lives in `/to-plan`, where the user reviews it.
- **Shared tree, planner-marked `[P]` + disjoint `files:` + orchestrator-owned git (chosen)**: spec-kit's `[P]` convention. Collisions are detectable after the fact (`git status` against each report's `FILES`), per-task commits stay clean because the files are disjoint, and a `Check:` run after each wave catches slices that disagree with each other.

## Consequences

- The `task-builder` definition ships inside the `build` skill (`skills/build/agents/task-builder.md`) and is symlinked into `~/.claude/agents/`. `npx skills` installs skills, not agents. If it's missing, `/build` falls back to `general-purpose` with the same contract pasted into the brief.
- A wrong `[P]` is caught as a collision (the wave is halted and nothing is committed), not silently merged.
