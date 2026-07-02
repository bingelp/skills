---
name: tdd
description: Red-green-refactor discipline for writing new functionality. Use whenever adding new behavior, a new function, or a new feature that can be driven by a test — not just when the user says "TDD".
---

# TDD

## Overview

Write the failing test before the code that makes it pass. Keeps scope honest and gives you a working definition of "done" for free.

## When to Use

Any time you're about to add new behavior with a clear expected input/output — a new function, endpoint, component behavior, bug fix with a reproducible case.

**Don't force it for:** exploratory spikes, pure config/plumbing changes, or UI-only visual tweaks with nothing meaningful to assert on.

## Process

1. **Red** — write a test for the behavior that doesn't exist yet. Run it, confirm it fails for the expected reason (not a typo or import error).
2. **Green** — write the minimum code to make it pass. Resist adding anything the test doesn't require.
3. **Refactor** — clean up now that it's green, keeping the test passing. Don't skip this step just because green feels done.
4. Repeat per behavior, not per file — small cycles.

## Red Flags

- Writing the implementation first and backfilling a test — that's not TDD, note it explicitly if you do it out of necessity.
- A test that passes immediately without ever seeing it fail — you haven't verified it tests anything.
- Piling multiple behaviors into one red-green cycle — split them.
