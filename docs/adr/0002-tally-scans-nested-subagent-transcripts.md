# `tally.py` scans nested subagent transcripts and fixes its path encoding

The `build-task-subagents` refactor moved `/build`'s implementation work into disposable
`Agent`-tool subagents. `/test` found this made that work's cost invisible to `/tally`:
subagent transcripts live in a nested `<session>/subagents/*.jsonl` that `tally.py`'s flat
scan never reaches, and separately, `tally.py`'s `transcript_dir()` path encoding didn't
match Claude Code's real on-disk scheme for any cwd containing a dotted segment (e.g.
`.claude/worktrees/<name>`, this repo's own isolation convention) — so `/tally` returned
zero sessions and $0.00 even for the orchestrator's own directly-attributed work. We
extended `iter_sessions()` to also glob `*/subagents/*.jsonl` and fixed the path-encoding
regex, leaving `resolve_feature`/`resolve_step`/the checkbox-flip fallback untouched.

## Considered options

- **Self-reported subagent usage** — the orchestrator records what each subagent reports
  about its own token spend. Rejected: new artifact, numbers a subagent could misreport,
  duplicates what the transcripts already contain.
- **Leave `tally.py` untouched, document `/build` cost as invisible to `/tally`** —
  honors the original Non-goal, but defeats `/tally`'s purpose for the one step this
  feature specifically restructured to move cost into subagents.
- **Extend session discovery only (chosen)** — smallest change; reuses the existing,
  unmodified attribution logic against sessions it was always intended to see.
