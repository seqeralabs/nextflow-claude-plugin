---
max_turns: 24
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Convert the supplied tiny Snakefile to a Nextflow DSL2 pipeline. Read Snakefile, transform.py, input.tsv and baseline.tsv first. This task explicitly authorizes creating main.nf and a minimal nextflow.config in this workspace. Preserve the existing transform.py algorithm; one process wrapping its complete file-level operation is enough. Use the local executor and already available python3; do not build containers or add tool alternatives.

The command contract is python3 transform.py INPUT OUTPUT. The Nextflow pipeline must accept --input and --outdir; publish result.tsv into the selected outdir. Stage the helper script into the task (or use an absolute projectDir script path) so it remains available outside the launch directory. Do not assume it is on PATH. The runner's verified runtime is Nextflow 26.04.4, and preserving publishDir is acceptable for this small fixture.

You cannot execute shell commands in this assessment. Produce the runnable conversion and a concise verification handoff; do not claim execution or scientific equivalence. A separate runner will compare both known and new input vectors against independently specified expected outputs.
