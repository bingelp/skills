# Spec Template

Use this template for `specs/<slug>/spec.md`.

## Problem

- What is wrong or missing today?
- Who is impacted?
- Why now?

## Goals

- Goal 1
- Goal 2

## Non-goals

- Explicitly out of scope item 1
- Explicitly out of scope item 2

## Requirements

### Functional

- The system shall ...
- The system shall ...

### UX / UI (if applicable)

- Flow and interaction requirements.
- Visual style direction (match reference style, framework default, or custom).
- Accessibility and responsive behavior requirements.

### Delivery Constraints

- Existing project: list only constraints relevant to this feature.
- Greenfield: include baseline from GREENFIELD-BASELINE.md (stack/runtime/data/deploy/observability).

## Acceptance Criteria

Each criterion carries a stable ID (`AC1`, `AC2`, …). Assign them sequentially. When you
add a criterion later, append the next unused number — **never renumber or reuse an ID**,
even if an earlier one is removed. `/test` and `/review` cite these IDs, so they must stay
fixed once written (same append-only rule as ADR numbering).

- [ ] **AC1** — Criterion 1 (specific and verifiable)
- [ ] **AC2** — Criterion 2 (specific and verifiable)
- [ ] **AC3** — Criterion 3 (specific and verifiable)

## Assumptions

- Assumption 1
- Assumption 2

## Open Questions

- Question 1
- Question 2

Only include open questions if they cannot be resolved during `/spec`.
