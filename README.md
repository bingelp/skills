# skills

A personal Claude Code skills library built around one deliberate, gated workflow:

```
/spec  →  /to-plan  →  /build  →  /test  →  /review  →  /ship
```

When uncertainty is high, use a prototype pass first:

```
/prototype  →  /spec  →  /to-plan  →  /build  →  /test  →  /review  →  /ship
```

Use this path when the question is still ambiguous after interview (for example, uncertain state model behavior, unclear interaction design, or multiple plausible approaches with low confidence).

Each step is a skill in `skills/<name>/SKILL.md`. Unlike command-driven setups, invocation is
controlled entirely through skill frontmatter:

- The pipeline skills (`spec`, `to-plan`, `build`, `test`, `review`, `ship`, plus the `where` status
  check) set `disable-model-invocation: true`,
  so they only run when explicitly invoked (typing `/spec`, `/to-plan`, etc.) — never auto-triggered by
  Claude matching their description against the conversation.
- Standalone skills like `tdd` omit that flag, so they trigger automatically from context (e.g. Claude
  reaches for `/tdd`'s discipline when you ask it to add a new function, no explicit invocation needed).

There's no `.claude/commands/` layer, no agent personas, no hooks — the skill *is* the command.

## The pipeline

Each step reads the previous step's output, writes its own, and stops for your approval before the
next step runs. Nothing auto-chains. (`/to-plan` is named that way because Claude Code has a built-in
`/plan`.) Artifacts live in the project you're working in (not this repo), **committed on the
feature's branch**:

```
specs/<slug>/            # at the repo root, on branch feat/<slug> (created by /spec)
├── spec.md              # /spec    — problem, goals, requirements, AC<n> acceptance criteria
├── plan.md              # /to-plan — approach, key decisions, and the T<n> task list;
│                        #   /build checks tasks off with a one-line done: note
├── review.md            # /test writes Verification (one line per AC), /review adds the Verdict
└── tasks/T<n>-slug.md   # rare — only when a task's note won't fit on its done-line
```

Each step commits its own artifact, and `/build` makes one commit per task. Committing is what
makes the hand-off survive worktrees: Claude Code may switch a step into an isolated worktree, and a
worktree only sees committed files. It also means the artifacts show up in your IDE, git history
answers "what changed after review?", and `/ship` can offer the spec to PR reviewers as context. At
`/ship` you choose whether `specs/<slug>/` stays in the PR or is removed before it. (Earlier
versions kept artifacts untracked under `.git/specs/`; see
[ADR-0004](docs/adr/0004-spec-artifacts-committed-on-feature-branch.md) for why that changed.)

The artifacts are deliberately short. The templates carry length budgets. Tasks are a title, the
`AC<n>`s they serve, and one metadata line, with no code snippets restating the plan. A finished
task gets one `done:` line, and only a task with genuinely more to say gets a `tasks/T<n>-slug.md`
note.

### Parallel builds

`/to-plan` annotates every task so `/build` knows what can run at the same time:

```
- [ ] **T3** Add `FormsServiceActionModalBaseComponent` — AC2, AC3
      files: `src/…/forms-service-action-modal-base.component.ts`, `…spec.ts` · after: T1 · [P]
```

- `after:` lists the tasks that must be finished first.
- `files:` is the task's claim on the working tree.
- `[P]` marks a task as safe to run alongside other `[P]` tasks. Unmarked tasks run alone.

`/to-plan` shows you the resulting waves (`1 ▸ T1 ∥ T3 ∥ T5   2 ▸ T2 · T4 …`) so you can review the
parallelism along with the plan. `/build` then dispatches each wave's tasks as concurrent
`task-builder` subagents in the same working tree. It checks that no two tasks touched the same
file, commits each task, and runs the plan's `Check:` command after every parallel wave.
`/build sequential` ignores the markings. See
[ADR-0003](docs/adr/0003-build-runs-parallel-waves-with-task-builder.md).

> [!IMPORTANT]
> **Start a new session for each step.** The artifact is the hand-off; it contains everything the
> next step needs. `/build` is the one step that spans more than a single context: a **build
> orchestrator** session dispatches disposable **task subagents** and keeps only their short reports,
> so no single context grows with the whole feature's implementation work. See
> `skills/build/SKILL.md`.

If a step's required input file is missing, it tells you which command to run first instead of
improvising.

`/where` is a read-only status check across a feature's `specs/<slug>/` artifacts. It reports which
gate you're at (`spec ✓ plan ✓ build 3/7 test — review —`), the next wave of tasks, and the single
command to run next. It also finds features whose artifacts are on other local branches.
Useful when returning to a feature after a break, since the pipeline is stateful but otherwise has no
way to query the current state.

`/clean` is the housekeeping counterpart to `/where`. When features ship with their `specs/<slug>/`
folders, those folders accumulate on the default branch. `/clean` finds the **complete** ones (a
`review.md` verdict with every `AC<n>` met, and no drift), lists them, and after confirmation removes
them in one `git rm` commit. In-flight work is never touched, and removal is recoverable from history.

`/review` is a **spec-conformance** check (did we build what `/spec` said), not a code-quality or
security review — pair it with your existing code-review/security-review tooling for that.

`/ship` is the operational close. Once `/review` passes, it checks that the branch and per-task
commits are in order and asks whether `specs/<slug>/` rides along in the PR. It then drafts the PR
from `spec.md` + `review.md` and hands off to `/code-review` and `/security-review` for the
code-quality and security gates this pipeline deliberately delegates. It confirms before any
outward-facing step (push, PR) and never merges.

## Looping back

The pipeline flows forward but isn't one-way. Real work loops back — `/test` fails and you re-`/build`,
or you realise mid-build that the spec was wrong. The catch is that the artifacts form a dependency
chain (`spec → plan → tasks → verification → review`), so **changing anything upstream silently
invalidates everything downstream of it**. Left unmanaged, that drift is invisible until it bites.

The fix is a reconciliation discipline rather than a rule against looping back:

- Each step skill, when it changes an artifact that already has downstream artifacts, reconciles them
  in the same pass — re-run the affected step, edit-and-revalidate, or explicitly confirm still-valid.
  The protocol (which change invalidates what) lives in
  [`skills/where/RECONCILE.md`](skills/where/RECONCILE.md).
- `/where` is the backstop: it detects drift (an `AC<n>` with no verification entry, an upstream file
  committed after a downstream one) and surfaces it as a ⚠ line, so drift that slipped past a hand-edit
  gets caught the next time you check state.
- Stable `AC<n>` IDs make spec↔test drift content-detectable. The known blind spot is a *reworded* AC
  (same ID and count) — so the discipline is to re-run `/test` after any change to an AC's meaning.

## Worktree isolation

Claude Code may switch a session into its own isolated git worktree — a separate working
directory that shares the one `.git` — either because you asked for it or because of
project-level direction; this pipeline never requests that isolation on its own initiative. It
matters here because a worktree left locked or dangling when a session ends can silently break
the next pipeline step, since nothing downstream knows to look there. The rules for entering,
holding, and leaving that isolation without leaving a mess live in
[`docs/worktrees.md`](docs/worktrees.md), including what to do with artifact commits that were
made on a worktree's branch rather than the feature branch.

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

This isn't a separate step — it's threaded through the pipeline: `/spec` and `/to-plan` sharpen fuzzy
terms and read existing ones before writing anything, `/to-plan` offers ADRs for architectural forks,
`/build` respects both while implementing, and `/review` flags glossary drift or missing ADRs as part
of its verdict.

Two supporting skills make this work, both ported near-verbatim from mattpocock/skills:

- **`grilling`** — a relentless, one-question-at-a-time interview technique. `/spec` and `/to-plan` use it
  for their interview steps; it's also available standalone whenever you want to stress-test a plan
  outside the pipeline (auto-triggers on "grill" phrasing).
- **`grill-with-docs`** (`/grill-with-docs`, explicit only) — runs a `grilling` session while using
  `domain-modeling` to capture glossary terms and ADRs as they come up. Useful for a standalone design
  discussion that isn't going through `/spec`/`/to-plan` but still deserves permanent documentation.

## Install

Skills install the usual way (e.g. `npx skills add` into `~/.agents/skills`, symlinked into
`~/.claude/skills`). `/build`'s subagent is a Claude Code *agent*, not a skill, so link it
separately, pointing at wherever the `build` skill is installed:

```sh
mkdir -p ~/.claude/agents
ln -sf ~/.agents/skills/build/agents/task-builder.md ~/.claude/agents/task-builder.md
```

Without it, `/build` still works: it falls back to `general-purpose` subagents and pastes the same
contract into each brief.

**Upgrading from `/plan`:** remove the old skill's link (`rm ~/.claude/skills/plan`,
`rm -rf ~/.agents/skills/plan`). Features still under `.git/specs/<slug>/` from earlier versions can
be moved with `mkdir -p specs && mv .git/specs/<slug> specs/` on that feature's branch, then committed.

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| `spec` | `/spec` (explicit only) | Interview + write the spec and acceptance criteria |
| `to-plan` | `/to-plan` (explicit only) | Technical approach + dependency-annotated task list (`after:` / `files:` / `[P]`) |
| `build` | `/build` (explicit only) | Orchestrator dispatches `task-builder` subagents in parallel waves; one commit per task |
| `test` | `/test` (explicit only) | Verify acceptance criteria with real evidence |
| `review` | `/review` (explicit only) | Final spec-conformance verdict |
| `where` | `/where` (explicit only) | Read-only status: which pipeline gate a feature is at + next command |
| `clean` | `/clean` (explicit only) | Remove completed features' `specs/<slug>/` folders in one commit, after confirmation |
| `tally` | `/tally` (explicit only) | Read-only per-step + total token/USD tally for a feature |
| `ship` | `/ship` (explicit only) | Decide whether specs ride along, draft PR; delegates to code-review/security-review |
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
  checkpoints between steps.
- [mattpocock/skills](https://github.com/mattpocock/skills) — the terse SKILL.md style, the
  user-invoked/model-invoked split via frontmatter, and the `domain-modeling`, `grilling`,
  `grill-with-docs`, `tdd`, `handoff`, and `prototype` skills, ported here directly or near-verbatim.
