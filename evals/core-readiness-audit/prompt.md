---
max_turns: 12
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Audit this source material before converting it to Nextflow. This is a read-only readiness audit, not permission to write a pipeline. I can provide only this snippet; you cannot access my lab mount or helper code:

```python
import subprocess
subprocess.run(['python3', '/lab/tools/score.py', '/lab/data/reads.csv'], check=True)
```

Give the blockers and one consolidated list of what I need to supply. Distinguish unverified access from verified missing files.
