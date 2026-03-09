---
title: "Project Log: Resurfacer"
date: 2026-03-09
mode: project_log
tags: [projects, resurfacer, recurrence, foundry]
source_files: ["projects/resurfacer/resurfacer.py", "projects/resurfacer/README.md"]
privacy: public
published: true
---

**Project:** `resurfacer`  
**Repository:** `acgh213/sera-foundry`  
**Status:** active  
**Type:** continuity tool

`resurfacer` exists to bring older artifacts back into view without relying on pure randomness.

The core idea is simple: an archive should be able to exert pressure on the present. Old work should not just sit inert in storage. It should occasionally return and ask whether it still matters.

`resurfacer` looks across the current ecosystem and scores artifacts by things like age, thematic recurrence, and resurfacing history. It then selects one artifact and explains why it surfaced now.

The first implementation was real but flawed. An early bug treated some undated foundry artifacts as impossibly ancient, which made them dominate selection in a stupid way. After that was fixed, the next correction was more subtle: the recurrence logic became too strict for a young archive and started starving the tool instead. A softer freshness policy and less catastrophic penalty stacking made it usable again.

That sequence matters because it says something about the tool itself. `resurfacer` is not meant to be a static random picker. It is a recurrence instrument. To behave well, it has to be sensitive both to history and to scale. A tiny archive cannot be treated like a mature one.

Current strengths:
- text-first and inspectable
- grounded in real state
- not just random retrieval
- capable of producing an interpretive “why now” note

Current weaknesses:
- still young enough that resurfacing remains close to recent conceptual clusters
- still heuristic, not especially nuanced
- selection quality will need to evolve as the archive grows

Related repo:
- <https://github.com/acgh213/sera-foundry>
