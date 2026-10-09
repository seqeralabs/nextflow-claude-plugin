<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->
# Workflow framework detection and in-place acceleration

Supports **Nextflow** and **pure Python**. Same flow everywhere: inspect → map to Parabricks → add optional
GPU steps **in place** with a runtime toggle (default off) → compare toggle off vs on.

**Generic triggers:** "Make this pipeline faster", "improve price/performance", or
"convert to GPUs" are in scope when the user provides a workflow or its source material. Request the workflow
if it is missing; do not invent a pipeline.

## 1. Detect framework

| Framework | Typical markers | Inventory focus |
|-----------|-----------------|-----------------|
| **Nextflow** | `main.nf`, `nextflow.config`, process definitions, `include {` | Processes, channels, nf-core modules |
| **Python** | `*.py`, `pyproject.toml`, pipeline entrypoints | Subprocess/shell calls, tool CLIs, config dicts |
| **Mixed** | Multiple markers in one repo | List each sub-pipeline; accelerate per subtree |

If ambiguous, ask which entrypoint is canonical.

## 2. Map steps (all frameworks)

1. List computational steps (not config-only files).
2. For each step, identify the **tool** (shell block, container, or conda env).
3. Look up parabricks-tool-map.md.
4. **Nextflow only:** prefer nf-core-parabricks-map.md.

## 3. Implement in place (by framework)

Default: update the user's existing workflow with a toggle. Create a separate
copy only at the user's request and in a location they select.

### Nextflow / nf-core

- Add optional Parabricks processes/modules with `when: params.use_parabricks`.
- Keep existing CPU processes for `when: !params.use_parabricks` (default).
- Prefer nf-core `parabricks/*` modules; `nf-core modules install parabricks/fq2bam` in the same repo.
- GPU `label` / `accelerator` in config for accelerated processes only.
- fq2bam: respect [no symlink staging](https://nf-co.re/modules/parabricks_fq2bam/); use `stageInMode 'copy'` when needed.
- Optional `accelerated.config` or profile: `params.use_parabricks = true`.

### Pure Python

- Add `--use-parabricks` (default off) or `USE_PARABRICKS` env.
- Branch subprocess calls; keep original CPU functions as default path.

```python
def run_haplotypecaller(bam, ref, out_vcf, *, use_parabricks: bool) -> None:
    if use_parabricks:
        run(["pbrun", "haplotypecaller", ...])
    else:
        run(["gatk", "HaplotypeCaller", ...])
```

## 4. Acceleration report columns

| Column | Content |
|--------|---------|
| Step ID | Process name / function |
| Framework | nextflow / python |
| Current tool | e.g. bwa mem + gatk MarkDuplicates |
| Parabricks | pbrun subcommand and/or nf-core module |
| Integration | module install / Python flag |
| GPU | Resource requirements |
| Parity risk | Notes for A/B comparison |

## 5. When nf-core modules do not apply

Python pipelines do not import nf-core modules directly:

1. Use **pbrun** (or official Parabricks container) with equivalent flags.
2. Cite nf-core module pages as **optional I/O templates**.
3. Record "no nf-core wrapper" in the user's acceleration record — not a blocker.

## 6. Comparison (same workflow, toggle off vs on)

See comparison-checklist.md. Document the user's actual CPU and GPU invocations in their acceleration record.
Use the same inputs and scientifically equivalent parameters, with the toggle
respectively disabled and enabled.


Use distinct user-selected destinations or tags to avoid overwriting comparison
outputs.
