---
name: spec
description: Writes a spec for a new feature or significant change. Only runs when the user explicitly types /spec.
disable-model-invocation: true
model: opus
---

# Spec

## Overview

Write a short spec before any code gets written. The spec is the contract between you and the user: what's being built, why, and how you'll both know it's done. Skipping this step means guessing at requirements during `/build`.

## When to Use

Explicit invocation only (`/spec`). Typical trigger: the user wants to start a new feature or a change big enough that requirements aren't already obvious.

**Don't bother for:** one-line fixes, typo corrections, or anything where `/plan` alone would be overkill — tell the user so and skip straight to implementing if they insist.

## Process

1. If `CONTEXT.md` (or `CONTEXT-MAP.md`) exists, read it first so your questions and the spec use the project's established terms, not synonyms for them. If it doesn't exist, this may be greenfield work — expect step 2 to create it.
2. Ask clarifying questions **one at a time** (see the `grilling` skill) for anything genuinely unclear — real unknowns you can't confidently guess. Don't dump a questionnaire, and don't skip ahead to step 3 just to avoid the back-and-forth. If the user uses a term that's vague or conflicts with `CONTEXT.md`, sharpen it on the spot using the `domain-modeling` skill before moving on. This applies unconditionally, not just when something's already wrong: the moment a domain noun (an entity, a status, a key action) gets defined or confirmed during the interview — including the *first* one on a greenfield project with no `CONTEXT.md` yet — capture it in `CONTEXT.md` via `domain-modeling` right then, the same way `/plan` unconditionally runs the ADR test on every key decision. Don't wait for a conflict to justify writing it down.
3. If the feature has a UI, treat visual style — colors, typography, spacing, light/dark theme, overall look — as genuinely unclear by default, not a reasonable inference to assume your way past. This holds even (especially) when the user hands you reference screenshots or mockups: screenshots settle *layout and behavior* but not automatically *style* — ask explicitly whether to also match the reference's visual style, follow the platform/framework default (e.g. stock Material 3), or something else. Don't let this quietly default the way "Material 3 theme" did on a past project with unused reference screenshots sitting right there.
4. For everything else — reasonable inferences you're fairly confident about, not open questions — state them as assumptions instead of interviewing for them, and give the user a chance to correct before you proceed, e.g.:
   ```
   ASSUMPTIONS:
   1. This only affects the web app, not the mobile client
   2. No new external dependency needed
   → Correct me now or I'll proceed.
   ```
5. Pick a kebab-case slug for the feature. Create `specs/<slug>/spec.md` with:
   - **Problem** — what's wrong or missing today
   - **Goals / Non-goals**
   - **Requirements** — for UI-bearing features, fold in whatever visual-style answers step 3 produced (or "no visual style requirements, use framework defaults" if the user explicitly said so) so `/plan` and `/build` aren't left guessing
   - **Acceptance Criteria** — a checklist, specific enough that `/test` can verify each item mechanically

   Do not add a "Domain Vocabulary" (or similarly-named) section to `spec.md` — canonical term definitions live in `CONTEXT.md` (via step 2), not here. `spec.md` should just use the established terms; if a definition would help a reader, reference `CONTEXT.md` rather than restating it.
6. Show the user the spec (and any new/updated `CONTEXT.md`). Stop. Tell them: "Review this, and run `/plan` once you're happy with it."

## Red Flags

- Writing the spec before requirements are concrete — go back to asking questions.
- Using a term inconsistent with `CONTEXT.md` without flagging it — that's exactly the drift `domain-modeling` exists to catch.
- Writing domain term definitions into `spec.md` (e.g. a "Domain Vocabulary" section) instead of `CONTEXT.md` — this is easy to do by default on greenfield work where no `CONTEXT.md` exists yet to prompt the habit, but it's exactly the case `domain-modeling` needs to run for.
- Acceptance criteria that are vague ("works well", "is fast") — make them checkable.
- Proceeding to `/plan` yourself instead of stopping for approval.
- Silently assuming a visual style (a default framework theme, or "matching the reference" without confirming *how much* of the reference) for a UI-bearing feature instead of asking — see step 3.
