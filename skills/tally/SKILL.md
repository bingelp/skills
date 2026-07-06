---
name: tally
description: Reports the per-step and total token/USD cost of a feature by attributing past session transcripts to its spec → plan → build → test → review → ship steps. Only runs when the user explicitly types /tally.
disable-model-invocation: true
model: sonnet
effort: low
---

# Tally

## Overview

Read-only per-feature cost report. A bundled script scans the current project's
Claude Code transcripts, attributes each session to a `(feature, step)`, sums the
four token types per step, prices them, and prints a finished table. The script
does all the work so transcript contents never enter the conversation — `/tally`
must itself be cheap, since it is a cost tool.

## When to Use

Explicit invocation only (`/tally [slug]`). Typical trigger: judging whether the
pipeline's ceremony was worth its token cost for a given feature. It never writes
files — it only reports.

## Process

1. Run the aggregator and relay its output **verbatim**:

   ```
   python3 skills/tally/tally.py [slug]
   ```

   (Use the path to `tally.py` inside this skill's directory.) The script owns
   slug resolution, so pass the user's slug through unchanged, or nothing if they
   gave none.

2. Slug resolution, handled entirely by the script (mirrors `/where`):
   - **Explicit slug** → detail that feature.
   - **No slug, one feature** under `specs/*/` → auto-detail it.
   - **No slug, several features** → the script prints a one-line roll-up per
     feature followed by a line reading exactly `TALLY_MULTIPLE`. When you see
     that sentinel, **ask the user which feature to detail**, then re-run the
     script with that slug. Do not print the sentinel line to the user.
   - **No `specs/` at all** → the script prints a "run /spec" message; relay it.

3. Present the table as-is. Don't recompute, reformat, or annotate the numbers.
   If a `⚠ … unpriced` footnote is present, keep it — it means a model's tokens
   were counted but not converted to USD.

## Output format

```
specs/dark-mode/ — token & cost tally   (prices as of 2026-07-05)

  step    sessions  input  output  cache-w  cache-r     USD
  spec           1  12.3k    4.1k     8.0k      45k   $0.42
  plan           1   9.8k    6.0k     6.1k      52k   $0.55
  build          2  31.0k   18.4k    14.2k     210k   $3.10
  ──────────────────────────────────────────────────────────
  total          4  53.1k   28.5k    28.3k     307k   $4.07
```

## Red Flags

- **Reading transcripts into context.** The whole point is that the script emits
  only the summary. Never `cat`, `head`, or otherwise pull `.jsonl` transcript
  contents into the conversation to "double-check" the numbers.
- **Writing anything.** `/tally` is read-only. It creates no files and edits none.
- **Folding non-step usage into a step.** The feature total is the sum of its
  attributed steps; sessions that resolve to no step (status checks, ad-hoc work,
  other `/tally` runs) are simply not counted. There is no "untracked" line — don't
  invent one or reassign that usage to a step.
- **Auto-running anything.** This skill reports and stops. It never launches the
  next pipeline command.
