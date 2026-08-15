---
name: openspec-apply-change
description: Implement tasks from an OpenSpec change, with per-section test verification, optional Playwright E2E, and a feature-branch offer. Use when the user wants to start implementing, continue implementation, or work through tasks.
license: MIT
compatibility: Requires openspec CLI. Optional test runner and Playwright for verification.
metadata:
  author: openspec + sdd.develop (merged)
  version: "2.0"
  generatedBy: "1.9.0"
---

Implement tasks from an OpenSpec change. The CLI (`openspec status` / `openspec instructions`) is the source of truth for state, tasks, and progress — never bypass it. This skill adds a verification loop and a terse output protocol on top of that authoritative state.

> **Permissions note:** this skill runs the test runner and `git` and edits code, so it is not restricted to `Bash(openspec:*)`. Keep code changes minimal and scoped to each task.

**Store selection:** If the user names a store (a standalone OpenSpec repo registered on this machine) or the work lives in one, run `openspec store list --json` to discover registered store ids, then pass `--store <id>` on the commands that read or write specs and changes (`new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, `schemas`, `view`). Once selected, treat `--store <id>` as sticky. Every unscoped example below is shorthand: append the flag before running. Without a store, commands act on the nearest local `openspec/` root.

**Input**: Optionally a change name (e.g., `/opsx:apply add-auth`). If omitted, infer from conversation context. If vague or ambiguous, you MUST prompt from `openspec list --json`.

---

## Output Protocol — MANDATORY

Keep output terse. Show ONLY:
- A progress line per task/section: `[N/M] <task>    done`
- Verification results: `Tests: PASS` / `Tests: BLOCK: <1-line reason>` / `E2E: PASS`
- Questions requiring user input (clarifications, added scope, approvals)
- The final status summary

Do NOT dump full file contents, internal reasoning, or verbose narration.

```
## Implementing: add-auth (schema: spec-driven)   3/7 tasks

[3/7] Add session middleware…                     done
[4/7] Wire login route…                           done
Section "Backend" complete → Tests: PASS
[5/7] Build login form…                            done
Section "UI" complete → Tests: PASS · E2E: PASS
```

---

## Steps

1. **Select the change.** If named, use it. Otherwise infer from context, or auto-select if only one active change exists, or ask from `openspec list --json`. Announce: *"Using change: `<name>`"* and how to override (`/opsx:apply <other>`).

2. **Read verification config (optional).** Read `openspec/config.yaml`. If it has a `verification` block, capture:
   - `verification.run_tests` — command run after each tasks section (omit ⇒ skip tests, warn once)
   - `verification.base_branch` — branch to offer branching from (default: `main`)
   - `verification.playwright.base_url` (+ optional `start_command`) — enables E2E on UI sections
   If there is no `verification` block and no obvious test command, warn once: *"No test runner configured; skipping test verification. Add a `verification` block to `openspec/config.yaml` to enable it."* Then continue without tests.

3. **Check status.** `openspec status --change "<name>" --json`. Parse `schemaName`, `planningHome`, `changeRoot`, `actionContext`, and which artifact holds the tasks (typically `tasks`).

4. **Get apply instructions.** `openspec instructions apply --change "<name>" --json`. This returns `contextFiles`, progress, the task list, a dynamic `instruction`, and optional `context` / `operationGuidance`.
   - `state: "blocked"` (missing artifacts) → report and suggest `/opsx:propose` or check `openspec status`. Do not proceed.
   - `state: "all_done"` → congratulate; suggest `/opsx:ship` or `/opsx:archive`.
   - Otherwise → proceed.
   Treat `context` as a required prompt-level input (apply relevant facts/conventions/constraints). Treat `operationGuidance` as optional advice (follow applicable, compatible entries). Neither is evidence a task is complete, neither replaces the built-in instruction, and neither permits bypassing a blocked state. On conflict with a CLI value or explicit user choice, report it and preserve the controlling value. Never copy either verbatim into code or artifacts.

5. **Read context files.** Read every path under `contextFiles` (spec-driven: proposal, specs, design, tasks).

6. **Offer a feature branch (first task only).** Run `git branch --show-current`. If it equals `base_branch` (from config, default `main`), ask: *"You are on `<base_branch>`. Create a feature branch?"* Do NOT create one without asking.
   - Yes → suggest `feat/<change-name>`, let the user confirm or rename, then `git checkout -b "<branch>"`.
   - No → continue on the current branch.
   If already on a feature branch, skip silently. Only before the first task.

7. **Show current progress** (per the Output Protocol): schema, `N/M` complete, the dynamic instruction.

8. **Implement (loop until done or blocked).** Work through pending tasks **in `tasks.md` order**, respecting its section (`##`) grouping:
   - For each task: make the minimal code changes, then mark it `- [ ]` → `- [x]` immediately.
   - **After completing each section** (a `##` group in `tasks.md`) — or once at the end if the list is flat — run **verification** (step 9). Sections keep the loop fast while still catching regressions early.

   **Pause and ask if:** a task is unclear; implementation reveals a design issue (suggest updating artifacts); a task needs work beyond what the spec/tasks describe (surface the added scope — never silently narrow, defer, or simplify away specified behavior); an error/blocker appears; or the user interrupts.

9. **Verification** (after each section):
   a. **Tests.** If `run_tests` is set, run it.
      - PASS → continue.
      - FAIL → analyze, fix, re-run. Repeat until green. If you can't get it green, `Tests: BLOCK: <reason>` and pause for guidance. Never mark remaining tasks complete over red tests.
   b. **E2E (optional).** Run ONLY if all hold: (1) `verification.playwright.base_url` is configured; (2) Playwright is available (MCP `mcp__playwright__*` tools or the `playwright` CLI); (3) the just-finished section touches UI/routes/visible components. Skip silently for backend-only, refactor, config, or docs sections.
      - Boot the app if `start_command` is set, navigate to `base_url`, drive the user flow described in the change's `specs`/`proposal`, and verify the result.
      - If E2E fails: fix the code **and** update tests, then re-run step 9a before continuing.

10. **On completion or pause, show status** (Output Protocol): tasks completed this session, overall `N/M`. If all done → suggest `/opsx:ship` (implements+verifies then offers archive) or `/opsx:archive`. If paused → state why and wait.

---

## Guardrails

- The CLI is authoritative for state, tasks, progress, and blocked/all-done — never fake or bypass it.
- Read `contextFiles` before starting; don't assume file names.
- Keep code changes minimal and scoped to each task; mark `- [x]` only when the task's specified behavior is fully implemented.
- Never mark tasks complete over failing tests; get green or `BLOCK` and pause.
- Run tests per section, not per task, unless a task is risky enough to warrant an immediate check.
- Only run E2E when its three conditions hold; skip silently otherwise.
- Surface added scope and pause — never silently narrow, defer, or simplify specified behavior.
- Do not use `context`/`operationGuidance` as proof of completion; never copy them into code or artifacts; report conflicts and preserve controlling values.
- Follow the Output Protocol — terse progress lines, PASS/BLOCK, no verbose dumps.

## Language

Write artifacts and code comments in the **same language the user used**; task/status field names stay in English.
