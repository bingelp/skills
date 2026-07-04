# Interview Checklist

Use this checklist to ensure coverage during `/spec` interviews. Do not dump it as a questionnaire.
Ask one question at a time (via `grilling`) and only where uncertainty is real.

## 1) Problem framing

- What pain exists today, for whom, and when does it happen?
- What outcome matters most if this succeeds?
- What is explicitly out of scope?

## 2) Users and scenarios

- Who are the actors (user types, systems, admins)?
- What are the top 1-3 user journeys that must work?
- What edge cases are likely to break trust?

## 3) Functional requirements

- What behaviors are required (inputs, actions, outputs)?
- What invariants or business rules must always hold?
- What events, state changes, or side effects are expected?

## 4) Data and integrations

- What entities and states are involved?
- Which external systems or APIs are in scope?
- What contract assumptions are being made about those dependencies?

## 5) UX and UI (if applicable)

- What user-visible flows must exist?
- What style direction is required: match reference style, framework defaults, or custom direction?
- What accessibility, responsiveness, and localization expectations apply?

## 6) Constraints and risks

- What compliance, policy, or security constraints apply?
- What performance or reliability expectations are non-negotiable?
- What known risks or unknowns need explicit assumptions?

## 7) Acceptance criteria quality gate

Each criterion should be:

- Observable: can be seen from behavior, not code internals.
- Testable: can be verified with a command, scenario, or check.
- Binary: clearly pass/fail (not "seems better").
- Traceable: maps back to one or more requirements.
- Identified: carries a stable `AC<n>` ID so `/test` and `/review` can cite it by name.
