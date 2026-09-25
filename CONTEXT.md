# Context

Canonical terms for this skills repo. Use these consistently; avoid the listed alternatives.

## Pipeline

- **pipeline** — the gated `/spec → /to-plan → /build → /test → /review → /ship` workflow.
- **step** — a single pipeline phase (spec, plan, build, test, review, ship). The unit of the
  cost breakdown in `/tally`. Prefer "step" over "phase" in user-facing skill output.
- **feature** — a unit of work tracked under `specs/<slug>/`. The thing whose total cost `/tally`
  measures. Identified by its kebab-case **slug**.
- **artifact** — a file a step writes under `specs/<slug>/` at the repo root, committed on
  the feature branch: `spec.md`, `plan.md` (approach + tasks), and `review.md` (Verification +
  Verdict). Used as the structural signal for attribution.

## Build loop

- **build orchestrator** — the `/build` session itself. It never implements a task
  directly. It dispatches **task subagents**, records each result, and commits each
  task. Keeping implementation work out of its own context is what bounds its
  growth to `O(tasks)` instead of `O(tasks²)`.
- **task subagent** — a disposable `task-builder` agent the build orchestrator spawns
  to implement and verify exactly one task in its own isolated context. It never
  touches git or `specs/`; it returns a fixed-shape report (`STATUS`, `FILES`,
  `SUMMARY`, `VERIFIED`, …) for the orchestrator to record.
- **wave** — the set of task subagents the orchestrator dispatches together in one
  message. A wave is either a single task, or several ready `[P]` tasks with
  disjoint `files:`.
- **`[P]`** — `/to-plan`'s marking that a task is safe to run in a wave alongside
  other `[P]` tasks. Unmarked tasks always run alone.
  _Avoid_: "concurrent-safe", "parallelizable" as the marker name — the marker is `[P]`.
- **done-line** — the single `done:` line the orchestrator adds under a checked task
  in `plan.md`.
- **task note** — the optional longer write-up for a task (a deviation's reasoning,
  a non-obvious decision), persisted as `specs/<slug>/tasks/T<n>-slug.md` only when
  it won't fit in a done-line.
  _Avoid_: "handoff" — that term is reserved for the `handoff` skill's whole-session
  compaction document, a different mechanism.

## Cost tracking (`/tally`)

- **tally** — the read-only per-step + total token/USD report produced by `/tally`. Not "cost
  report" or "usage report" (those collide with `/cost`, `/usage`, `/stats`).
- **session** — one Claude Code session = one transcript `.jsonl` under
  `~/.claude/projects/<encoded-cwd>/`. The established practice is **one session per step**, which
  is what makes per-step attribution clean.
- **attribution** — mapping a session to a `(feature, step)` pair. Feature comes from which
  `specs/<slug>/` artifacts the session references (writes preferred over reads); step comes from
  the session's `attributionSkill`, falling back to which artifact it wrote.
- **price table** — the bundled per-model, per-token-type USD rate table `/tally` uses to convert
  tokens to dollars. Carries an **as-of date** shown in output so stale pricing is visible.
