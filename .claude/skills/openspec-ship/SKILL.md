---
name: openspec-ship
description: End-to-end flow for a single OpenSpec change - implement + verify (apply), then offer to sync specs and archive with explicit confirmation. Use when the user says "ship this change", "finish this change", "implement and archive", or wants the full implement-to-archive flow in one entry point.
license: MIT
compatibility: Requires openspec CLI. Optional test runner and Playwright for verification.
metadata:
  author: openspec + sdd.develop (merged)
  version: "1.0"
  generatedBy: "1.9.0"
---

A thin orchestrator that runs one change from planned → implemented → archived, in a single session, **without** collapsing the destructive archive step into the flow. It delegates to the existing skills so their logic stays authoritative:

```
  /opsx:ship <change>
        │
        ├─▶  openspec-apply-change   implement tasks + verify (tests, optional E2E)
        │
        ├─▶  [ALL TASKS DONE + TESTS GREEN]
        │
        ├─▶  ⛏  CONFIRMATION GATE  ── "Sync specs & archive now?"  ── No ──▶ stop, tell how to archive later
        │           │ Yes
        │           ▼
        └─▶  openspec-archive-change   sync delta→main specs (living specs), validate, mv to archive
```

**Why archive is gated, not automatic:** archive performs an irreversible, semantic merge of the change's delta specs into the project's permanent *main* specs (it can even delete a spec that a removal leaves empty) and then moves the change directory. That is the one human checkpoint worth keeping. Never archive without the user's explicit "yes" in this session.

**Store selection:** honor the same `--store <id>` rules as the sub-skills; if a store is in play, keep it sticky across both phases.

**Input**: Optionally a change name (e.g., `/opsx:ship add-auth`). If omitted, infer from context, auto-select if only one active change exists, or ask from `openspec list --json`.

---

## Output Protocol — MANDATORY

Terse. One progress line per phase; sub-skills keep their own terse output.

```
## Shipping: add-auth

[1/2] Implement + verify…
  (apply runs: tasks + tests + E2E)          done → 7/7, Tests PASS, E2E PASS
[2/2] Sync specs & archive?
  → Delta touches: auth (2 added, 1 modified). Proceed? (yes/no)
```

---

## Steps

1. **Select the change.** Resolve as above. Announce: *"Shipping change: `<name>`"* and how to override (`/opsx:ship <other>`).

2. **Phase 1 — Implement + verify.** Invoke the **`openspec-apply-change`** skill for `<name>`. Let it run its full loop: branch offer, task implementation, per-section tests, optional Playwright E2E.
   - If apply pauses or `BLOCK`s (blocked artifacts, unclear task, red tests it can't fix, added scope) → stop here and surface it. Do NOT proceed to archive. Shipping resumes when the user resolves it and re-runs `/opsx:ship`.
   - If apply reports `all_done` at the start (already implemented) → skip straight to Phase 2.

3. **Confirm readiness for archive.** Re-check `openspec status --change "<name>" --json`. Only continue if every artifact is `done` or `skipped` and tasks are all `- [x]`. If not, list what's incomplete and ask whether to archive anyway (this mirrors archive's own warnings) — default to **no**.

4. **Preview the spec impact.** Before prompting, summarize what archive's sync would do to the *living* main specs: for each delta spec in `artifactPaths.specs.existingOutputPaths`, name the capability and the adds / modifications / removals / renames. Flag loudly any capability that would be **retired** (main `spec.md` deleted). This preview is read-only.

5. **Phase 2 — Confirmation gate.** Ask explicitly: *"Sync specs to main and archive `<name>` now?"*
   - **No** → stop. Tell the user: *"Nothing archived. Run `/opsx:archive <name>` when ready, or `/opsx:sync <name>` to update main specs without archiving."*
   - **Yes** → invoke the **`openspec-archive-change`** skill for `<name>`. It owns the sync + validate + move logic; do not reimplement it here. Pass through the store flags. Wait for it to finish.

6. **Final summary.** Report: change name, schema, tasks `N/M`, verification result, whether specs were synced, and the archive location — or, if the user declined the gate, that the change remains active and how to finish it later.

---

## Guardrails

- **Delegate, don't duplicate.** Phase 1 is `openspec-apply-change`; Phase 2 is `openspec-archive-change`. This skill only sequences them and owns the confirmation gate.
- **Never auto-archive.** The gate requires an explicit "yes" this session. No "yes" ⇒ stop with the change intact.
- **Stop on any apply pause/block.** Do not paper over failed verification by archiving.
- **Preview spec impact before the gate**, especially capability retirements — the user should see what the living specs will become before approving.
- **The CLI stays authoritative** for state, sync, validation, and the move. Report conflicts; preserve controlling values.
- Follow the Output Protocol — terse phase lines; let sub-skills speak for themselves.

## Language

Respond in the **same language the user used**; artifact/status field names stay in English.
