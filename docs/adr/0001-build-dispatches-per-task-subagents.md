# `/build` dispatches per-task subagents instead of looping inline

`/build` was the only pipeline step that reused one session across every unit of work, so its context grew ~quadratically with task count. We changed it to a **build orchestrator** that dispatches one disposable **task subagent** per task (via the `Agent` tool, foreground and sequential), bounding the orchestrator's own context to `O(tasks)`.

## Considered options

- **Inline loop (status quo)** — simplest, but `O(tasks²)` context growth; the problem being fixed.
- **`Workflow` tool** — built for fan-out orchestration, but gated behind explicit user opt-in, so it's the wrong default for a pipeline step.
- **`/loop` skill** — its `ScheduleWakeup` resumes the *same* session, so it wouldn't reduce the orchestrator's context growth at all.
- **`Agent` tool, foreground/blocking (chosen)** — each task runs in its own throwaway context; blocking on the call enforces strict sequential order with no scheduler.
