---
name: "OPSX: Apply"
description: "Implement tasks from an OpenSpec change, with per-section tests, optional E2E, and a branch offer"
category: "Workflow"
tags: ["workflow", "apply", "artifacts", "verification", "experimental"]
---

Invoke the **`openspec-apply-change`** skill for the change named in the argument after `/opsx:apply` (infer from context or ask if omitted).

It implements the change's tasks in order, runs the configured test runner after each `tasks.md` section, optionally verifies UI sections with Playwright, offers a feature branch on the first task, and follows a terse output protocol.
