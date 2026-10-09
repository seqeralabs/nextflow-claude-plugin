---
max_turns: 12
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Review this Nextflow output aggregation pattern. Each input table has a header and downstream consumers require exactly one header. Is `tables.collectFile(name: 'merged.tsv')` enough? Explain the correct header/seed contract and what must be tested, without editing anything.
