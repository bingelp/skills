# Context

Canonical terms for this skills repo. Use these consistently; avoid the listed alternatives.

## Pipeline

- **pipeline** — the gated `/spec → /plan → /build → /test → /review → /ship` workflow.
- **step** — a single pipeline phase (spec, plan, build, test, review, ship). The unit of the
  cost breakdown in `/tally`. Prefer "step" over "phase" in user-facing skill output.
- **feature** — a unit of work tracked under `specs/<slug>/`. The thing whose total cost `/tally`
  measures. Identified by its kebab-case **slug**.
- **artifact** — a file a step writes under `specs/<slug>/` (`spec.md`, `plan.md`, `tasks.md`,
  `review.md`). Used as the structural signal for attribution.

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
