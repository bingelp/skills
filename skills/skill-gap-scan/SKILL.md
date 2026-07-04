---
name: skill-gap-scan
description: Audits the current session for repeated manual instructions, corrections, or workarounds that aren't covered by an existing skill, and proposes concrete new skills to create. Use this at the end of a /review pass, right before /compact or /handoff, or whenever the user asks "should this be a skill", "are we repeating ourselves", "what should I turn into a skill", or wants a checkpoint on their skill/agent setup. Do NOT use this for writing or editing a skill directly — that's skill-creator's job. This skill only detects and recommends; it hands off to skill-creator for authoring.
model: sonnet
effort: low
---

# Skill Gap Scan

A checkpoint skill: look back over the current session (and optionally the
project's `.claude/skills/` directory) and decide whether anything that just
happened should become a durable skill instead of being re-explained next
time.

This is deliberately narrow. It does not write skills. It produces a short,
ranked report, and only hands off to `skill-creator` once the user picks a
candidate.

## When to run

Trigger this:
- Automatically at the tail end of a `/review` pass, once diffs are approved
- Right before `/compact` or `/handoff`, so nothing gets lost in the summary
- On explicit invocation ("scan for skill gaps", "should any of this be a skill")

Do not run this mid-task or on short sessions (< ~15 exchanges) — there's
rarely enough repetition yet to justify a scan, and running it too often
trains the user to ignore it.

## What counts as a signal

Scan the session transcript for these patterns specifically. A single
occurrence is not a signal — look for **repetition or correction**, which is
the actual tell that something should be codified:

1. **Repeated manual instructions** — the user explained the same
   convention, format, or constraint more than once, in different words,
   because it wasn't remembered from earlier in the pipeline stage.
2. **Corrections to skill output** — an existing skill (`/spec`,
   `/plan`, `/build`, `/test`, `/review`) produced something
   the user had to fix by hand, and the fix follows a pattern rather than
   being a one-off.
3. **Manual multi-step workarounds** — the user (or Claude) did a sequence
   of tool calls by hand that isn't captured anywhere, and it looks like
   the kind of thing that will recur (e.g., a specific way of verifying a
   migration, a specific lint/format pass before commit).
4. **Permission friction** — repeated approval prompts in `settings.json`
   for the same tool/command pattern, suggesting either a permission rule
   or a scoped skill with `allowed-tools` would remove the friction.
5. **Cross-stage glue** — something the user does by hand *between* two
   pipeline stages (e.g., translating `/plan` output into a specific
   `/build` scaffold shape) that could be folded into one of the existing
   skills or become a connector skill between them.

## What does NOT count

- A task done once with no sign it'll recur
- Something already covered by an existing skill, even if imperfectly used
  (that's a candidate for *editing* a skill, not creating one — say so, and
  route to `skill-creator`'s update flow instead of a new skill)
- Anything that's really a `settings.json` permission tweak rather than a
  skill (say so explicitly — don't inflate a permissions fix into a skill)
- Anything that only makes sense as a one-off script, not a reusable
  workflow

## Procedure

1. **Inventory existing skills first.** Read `.claude/skills/` (project)
   and `~/.claude/skills/` (personal) — name + description only, same as
   what Claude sees at session start. This is your dedup check: never
   propose a skill that substantially overlaps an existing one without
   naming the overlap.
2. **Walk the session** looking for the five signal types above. Note
   where each occurred (roughly — "when generating the plan for X" is
   enough, don't cite exact turn numbers).
3. **Filter to real candidates.** Drop anything that only happened once
   with no correction, and anything that's just a permissions fix.
4. **Rank by frequency × friction removed**, not by novelty. A boring skill
   that removes a repeated 3-step manual dance beats a clever one that
   saves a single sentence of typing.
5. **Report using the format below.** Keep it short — this is a checkpoint,
   not a deliverable.
6. **Wait for the user to pick one (or none).** Only then hand off to
   `skill-creator`, passing along the observed pattern, trigger phrases,
   and example input/output pulled from this session so the interview
   step in skill-creator starts pre-filled instead of from zero.

## Report format

```
## Skill gap scan — [session/date context]

Existing skills checked: spec, plan, build, test, review [+ any others found]

### Candidates

1. **[proposed-skill-name]** — [one-line description of what it'd do]
   - Observed: [what happened, how many times, in what stage]
   - Overlaps with: [existing skill name, or "none"]
   - Est. effort: [trivial / small / needs interview]

2. ...

### Not a new skill
- [thing that looked like a candidate but is actually a settings.json permission tweak, or an edit to an existing skill]
```

If there are zero real candidates, say so plainly — don't manufacture one
to justify having run. "Nothing repeated enough this session to warrant a
new skill" is a valid and useful result.

## Notes on this pipeline specifically

Since the existing pipeline is stage-based (`/spec` → `/plan` → `/build` →
`/test` → `/review`), the most valuable gaps are usually at the **seams
between stages**, not inside a single stage — that's where manual
translation work tends to hide. Weight cross-stage glue (signal type 5)
slightly higher than in-stage repetition when ranking.

If model/effort is already being hardcoded in frontmatter for the existing
skills, propose the same for any new candidate (e.g. lightweight glue
skills default to a cheaper model/lower effort; anything doing real
code generation defaults to whatever the `/build`/`/test` skills currently
use) so the recommendation is immediately actionable rather than requiring
a follow-up decision.