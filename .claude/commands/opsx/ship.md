---
name: "OPSX: Ship"
description: "Implement + verify a change, then offer to sync specs and archive (with confirmation)"
category: "Workflow"
tags: ["workflow", "ship", "apply", "archive", "experimental"]
---

Invoke the **`openspec-ship`** skill for the change named in the argument after `/opsx:ship` (infer from context or ask if omitted).

It runs the full flow for one change: implement + verify via `openspec-apply-change`, then — only after an explicit confirmation — sync the delta specs into the living main specs and archive via `openspec-archive-change`. Never auto-archive.
