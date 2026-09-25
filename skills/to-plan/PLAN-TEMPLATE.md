# Plan Template

Use this template for `specs/<slug>/plan.md`. `/to-plan` writes everything down to and including
**Tasks**. `/build` checks tasks off in place and adds **Deviations** only if a task departed from
the plan.

**Keep it short.** A reader should get through the whole file in a couple of minutes. The Approach
explains the shape once; tasks point at it instead of restating it. Tasks carry no code blocks. If
a signature or data shape matters, put it once in Approach. The implementing agent reads the
code; it doesn't need the plan to pre-write it.

## Approach

The technical strategy in plain language: what changes, in roughly what order, and why this way.
A few short paragraphs, not an essay.

## Files touched

- `path/to/file.ts` — why it changes (one line each; group by area when there are many)

## Key decisions

- **Decision** — the option chosen; the alternative rejected and why. Link the ADR if one was written.

## Tasks

Check: `npm run lint && npm test`

- [ ] **T1** Make `getApplicationHeader()` rethrow instead of swallowing errors — AC4
      files: `src/app/shared/data-services/applications.data-service.ts`, `src/app/shared/data-services/applications.data-service.spec.ts` · [P]
- [ ] **T2** Abort the transfer action when the header fetch fails — AC1
      files: `src/app/…/request-transfer-program-action.component.ts`, `src/app/…/request-transfer-program-action.component.spec.ts` · after: T1
- [ ] **T3** Add `FormsServiceActionModalBaseComponent` — AC2, AC3
      files: `src/app/shared/common/action-modals/forms-service-action-modal-base.component.ts`, `…/forms-service-action-modal-base.component.spec.ts` · [P]
- [ ] **T4** Register the new base in the shared module and export it — AC2
      files: `src/app/shared/shared.module.ts` · after: T3

## Deviations

- T2 — kept the `appHeader?.` guard because the header can legitimately be absent for drafts; see `tasks/T2-abort-transfer.md`

---

## Field reference

**`Check:`** is the one command that verifies the whole feature (build + lint + tests, as this
project runs them). `/build` runs it after every wave that ran tasks in parallel, and once at the end.

**Task line.** `**T<n>**`, a one-line imperative title, and the `AC<n>` IDs it serves. Then one
indented metadata line:

| Field | Meaning |
|---|---|
| `files:` | Every file the task expects to create or edit, as repo-relative paths. `/build` treats the list as the task's claim: two tasks whose lists overlap never run at the same time. Use exact paths, not globs. A glob hides overlaps. |
| `after: T1, T3` | Tasks that must be finished first. Leave it out when there are none. |
| `[P]` | This task is safe to run at the same time as other `[P]` tasks, as long as their `files:` don't overlap. A task without `[P]` runs alone. |
| `` `[model: X]` `` | Optional hint for which model the task's subagent should use. Only add it with a concrete reason. |

**Stable IDs.** Once written, `T<n>` IDs are append-only, like `AC<n>`. Never renumber or reuse
one. A dropped task's line is deleted and its number retired. That's what lets done-lines,
`after:` references, and `tasks/T<n>-slug.md` note files stay valid across re-plans.

**After `/build`.** A finished task gets one `done:` line and nothing more:

```
- [x] **T1** Make `getApplicationHeader()` rethrow instead of swallowing errors — AC4
      files: `…/applications.data-service.ts`, `…/applications.data-service.spec.ts` · [P]
      done: rethrows case-normalized error; spec rewritten to assert rethrow (8/8 pass)
```

If a task has more worth keeping than fits on that line (a deviation, a non-obvious decision,
verification evidence beyond "tests pass"), the detail goes in `specs/<slug>/tasks/T<n>-slug.md`
and the done-line ends with `— see tasks/T<n>-slug.md`. Most tasks shouldn't need a note file.
