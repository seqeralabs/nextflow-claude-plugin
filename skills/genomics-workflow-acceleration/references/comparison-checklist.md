<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->
# Toggle-off vs toggle-on comparison checklist

Compare the **same workflow** with the runtime toggle **off** (CPU path) vs **on**
(GPU path) using the **same** inputs.

## Run setup

- [ ] Same samplesheet, reference genome build, and interval lists
- [ ] Distinct user-selected output destinations — avoid overwriting
- [ ] Document workflow revision, container digests, Parabricks version (`pbrun version`), and **both run commands** in the user's acceleration record
- [ ] GPU run logged: device type, driver, and where it ran (local / HPC / cloud)

Use the user's actual entrypoint and execution configuration for both runs,
with acceleration respectively disabled and enabled. Record the real invocations
without inventing locations for the workflow, parameters, inputs, or outputs.

## Outputs to compare

| Stage | Suggested checks |
|-------|------------------|
| Alignment (fq2bam) | Flagstat, insert size, duplicate rate; spot-check chr depth |
| BQSR | Compare recalibration tables if emitted |
| Variants (HC / DeepVariant) | VCF concordance (e.g. bcftools `isec`); review indel-region differences |
| Runtime | Wall time, GPU utilization (informational, not sole correctness gate) |

## Acceptance

- Define tolerances **with the user** (VCF concordance %, etc.).
- Treat first GPU-enabled run as **validation**, not production cutover.
- File gaps in the user's acceleration record for steps with no Parabricks mapping.

## Reporting template

Record in the user's acceleration record (required). Optional HTML/markdown table if the user
requested automation — see SKILL.md §9.

```markdown
## A/B comparison — [date]

| Metric | Toggle off (CPU) | Toggle on (GPU) | Pass? |
|--------|------------------|-----------------|-------|
| Wall time | | | |
| VCF concordance | | | |
| Notes | | | |
```
