---
name: spec
description: Writes a spec for a new feature or significant change. Only runs when the user explicitly types /spec.
disable-model-invocation: true
---

# Spec

## Overview

Write a short spec before any code gets written. The spec is the contract between you and the user: what's being built, why, and how you'll both know it's done. Skipping this step means guessing at requirements during `/build`.

## When to Use

Explicit invocation only (`/spec`). Typical trigger: the user wants to start a new feature or a change big enough that requirements aren't already obvious.

**Don't bother for:** one-line fixes, typo corrections, or anything where `/plan` alone would be overkill — tell the user so and skip straight to implementing if they insist.

## Process

1. If `CONTEXT.md` (or `CONTEXT-MAP.md`) exists, read it first so your questions and the spec use the project's established terms, not synonyms for them.
2. Ask clarifying questions **one at a time** (see the `grilling` skill) for anything genuinely unclear — real unknowns you can't confidently guess. Don't dump a questionnaire, and don't skip ahead to step 3 just to avoid the back-and-forth. If the user uses a term that's vague or conflicts with `CONTEXT.md`, sharpen it on the spot using the `domain-modeling` skill before moving on.
3. For everything else — reasonable inferences you're fairly confident about, not open questions — state them as assumptions instead of interviewing for them, and give the user a chance to correct before you proceed, e.g.:
   ```
   ASSUMPTIONS:
   1. This only affects the web app, not the mobile client
   2. No new external dependency needed
   → Correct me now or I'll proceed.
   ```
4. Pick a kebab-case slug for the feature. Create `specs/<slug>/spec.md` with:
   - **Problem** — what's wrong or missing today
   - **Goals / Non-goals**
   - **Requirements**
   - **Acceptance Criteria** — a checklist, specific enough that `/test` can verify each item mechanically
5. Show the user the spec. Stop. Tell them: "Review this, and run `/plan` once you're happy with it."

## Red Flags

- Writing the spec before requirements are concrete — go back to asking questions.
- Using a term inconsistent with `CONTEXT.md` without flagging it — that's exactly the drift `domain-modeling` exists to catch.
- Acceptance criteria that are vague ("works well", "is fast") — make them checkable.
- Proceeding to `/plan` yourself instead of stopping for approval.
