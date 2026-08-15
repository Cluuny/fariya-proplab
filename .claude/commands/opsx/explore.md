---
name: "OPSX: Explore"
description: "Read-only thinking partner - investigate, debug, brainstorm, review, clarify"
allowed-tools: Bash(openspec:*)
category: "Workflow"
tags: ["workflow", "explore", "thinking", "experimental"]
---

Invoke the **`openspec-explore`** skill with the argument after `/opsx:explore` (a vague idea, a specific problem, a change name, a comparison, or nothing).

It enters read-only explore mode: investigate the real codebase (following the dependency chain), classify the question (bug / understanding / brainstorm / review / impact) and answer in the matching structured format, visualize with ASCII diagrams, and — only if asked — capture thinking into OpenSpec artifacts. Never implements code; hands off to `/opsx:propose` or `/opsx:ship` when the user is ready to build.
