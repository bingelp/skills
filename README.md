# skills

A personal Claude Code skills library built around one deliberate, gated workflow:

```
/spec  →  /plan  →  /build  →  /test  →  /review  →  /ship
```

When uncertainty is high, use a prototype pass first:

```
/prototype  →  /spec  →  /plan  →  /build  →  /test  →  /review  →  /ship
```

Use this path when the question is still ambiguous after interview (for example, uncertain state model behavior, unclear interaction design, or multiple plausible approaches with low confidence).

Each phase is a skill in `skills/<name>/SKILL.md`. Unlike command-driven setups, invocation is
controlled entirely through skill frontmatter:

- The pipeline skills (`spec`, `plan`, `build`, `test`, `review`, `ship`, plus the `where` status
  check) set `disable-model-invocation: true`,
  so they only run when explicitly invoked (typing `/spec`, `/plan`, etc.) — never auto-triggered by
  Claude matching their description against the conversation.
- Standalone skills like `tdd` omit that flag, so they trigger automatically from context (e.g. Claude
  reaches for `/tdd`'s discipline when you ask it to add a new function, no explicit invocation needed).

There's no `.claude/commands/` layer, no agent personas, no hooks — the skill *is* the command.

## The pipeline

Each phase reads the previous phase's output, writes its own, and stops for your approval before the
next phase runs. Nothing auto-chains. Artifacts live in the project you're working in (not this repo),
under a per-feature folder:

```
specs/<slug>/
├── spec.md      # /spec   — problem, goals, requirements, acceptance criteria
├── plan.md      # /plan   — technical approach, files touched, key decisions
├── tasks.md     # /plan writes it, /build checks tasks off, /test appends verification
└── review.md    # /review — final spec-conformance verdict
```

If a phase's required input file is missing, it tells you which command to run first instead of
improvising.

`/where` is a read-only status check across a feature's `specs/<slug>/` artifacts — it reports which
gate you're at (`spec ✓ plan ✓ build 3/7 test — review —`) and the single command to run next.
Useful when returning to a feature after a break, since the pipeline is stateful but otherwise has no
way to query the current state.

`/review` is a **spec-conformance** check (did we build what `/spec` said), not a code-quality or
security review — pair it with your existing code-review/security-review tooling for that.

`/ship` is the operational close: once `/review` passes, it turns the work into git state — a feature
branch, atomic commits mapped to the tasks, and a draft PR built from `spec.md` + `review.md` — then
hands off to `/code-review` and `/security-review` for the code-quality/security gates this pipeline
deliberately delegates. It confirms before any outward-facing step (push, PR) and never merges. Unlike
the other phases it writes no `specs/<slug>/` artifact; its output is the branch, commits, and PR.

## Ubiquitous language & ADRs

`domain-modeling` maintains two project-level (not per-feature) files, ported from mattpocock's skills:

```
/
├── CONTEXT.md         # or CONTEXT-MAP.md for multi-context repos — the project's glossary
└── docs/
    └── adr/
        ├── 0001-slug.md
        └── 0002-slug.md
```

`CONTEXT.md` is a glossary only — canonical terms, what to avoid, nothing implementation-specific.
`docs/adr/` records decisions that are hard to reverse, surprising without context, and the result of
a real trade-off; see `domain-modeling/ADR-FORMAT.md` for the full test. Both are created lazily, the
moment there's a real term or decision to capture — not scaffolded up front.

This isn't a separate phase — it's threaded through the pipeline: `/spec` and `/plan` sharpen fuzzy
terms and read existing ones before writing anything, `/plan` offers ADRs for architectural forks,
`/build` respects both while implementing, and `/review` flags glossary drift or missing ADRs as part
of its verdict.

Two supporting skills make this work, both ported near-verbatim from mattpocock/skills:

- **`grilling`** — a relentless, one-question-at-a-time interview technique. `/spec` and `/plan` use it
  for their interview steps; it's also available standalone whenever you want to stress-test a plan
  outside the pipeline (auto-triggers on "grill" phrasing).
- **`grill-with-docs`** (`/grill-with-docs`, explicit only) — runs a `grilling` session while using
  `domain-modeling` to capture glossary terms and ADRs as they come up. Useful for a standalone design
  discussion that isn't going through `/spec`/`/plan` but still deserves permanent documentation.

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| `spec` | `/spec` (explicit only) | Interview + write the spec and acceptance criteria |
| `plan` | `/plan` (explicit only) | Technical approach + atomic task breakdown |
| `build` | `/build` (explicit only) | Implement tasks one at a time |
| `test` | `/test` (explicit only) | Verify acceptance criteria with real evidence |
| `review` | `/review` (explicit only) | Final spec-conformance verdict |
| `where` | `/where` (explicit only) | Read-only status: which pipeline gate a feature is at + next command |
| `ship` | `/ship` (explicit only) | Branch, commit per task, draft PR; delegates to code-review/security-review |
| `tdd` | automatic | Red-green-refactor nudge when writing new behavior |
| `domain-modeling` | automatic | Maintain `CONTEXT.md` glossary + `docs/adr/` decisions |
| `grilling` | automatic | Relentless one-question-at-a-time interview |
| `grill-with-docs` | `/grill-with-docs` (explicit only) | `grilling` + `domain-modeling` combined, for standalone design sessions |
| `handoff` | `/handoff` (explicit only) | Compact the current conversation into a handoff doc for another agent |
| `skill-gap-scan` | automatic | Detect repeated friction and recommend which workflow should become a new skill |
| `prototype` | automatic | Throwaway prototype (logic or UI) to answer a design question fast |

## Credits

This repo borrows ideas and, in several cases, ported content from two existing skills repos:

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — the shape of the gated
  `spec → plan → build → test → review` pipeline with persisted hand-off artifacts and human-approval
  checkpoints between phases.
- [mattpocock/skills](https://github.com/mattpocock/skills) — the terse SKILL.md style, the
  user-invoked/model-invoked split via frontmatter, and the `domain-modeling`, `grilling`,
  `grill-with-docs`, `tdd`, `handoff`, and `prototype` skills, ported here directly or near-verbatim.
