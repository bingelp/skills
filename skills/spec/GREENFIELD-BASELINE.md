# Greenfield Baseline

Use this only when the project is new or technical foundations are not already established.
Capture this as "Delivery Constraints" in `spec.md` so `/plan` does not need to guess baseline facts.

This is intentionally lightweight: record constraints and defaults, not deep architecture.

## Capture in spec

- Platform targets: web, mobile, backend, CLI, worker, etc.
- Language/runtime/framework defaults.
- Data/storage baseline: primary database, cache, file/object storage (if any).
- Integration boundaries: upstream/downstream systems and contract assumptions.
- Deployment/runtime environment: cloud/on-prem, container/serverless, regions.
- Observability baseline: logs, metrics, tracing, error reporting expectations.
- Delivery constraints: compliance, privacy, latency, availability, cost ceilings.

## Prompt style

- Ask one unknown at a time.
- If likely true, propose as an assumption and ask for correction.
- If multiple choices are viable, recommend one with a short rationale.

## Keep out of spec

- Deep implementation design and detailed architecture diagrams.
- Irreversible technical decisions that need trade-off analysis.

Those belong in `/plan`, with ADRs when the decision meets the ADR test.
