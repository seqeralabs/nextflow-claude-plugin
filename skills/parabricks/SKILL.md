---
name: parabricks
description: >-
  Route NVIDIA Parabricks pbrun tools, assess GPU/runtime readiness, and provide
  version-aware command guidance for FASTQ/BAM processing, RNA-seq, variant
  calling, BAM QC, and GVCF workflows. Do NOT use for inspecting or accelerating
  whole pipelines — use genomics-workflow-acceleration.
license: Apache-2.0
metadata:
  author: "Angel Pizarro <apizarro@nvidia.com>"
  tags:
    - parabricks
    - genomics
    - nvidia
---
<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->

## Using this skill

Use the tools and runtimes available in the user's session. Establish the
pipeline, input data and execution environment from their request or current
context. Use user-selected locations for files and results. Consult companion
skills, bundled references and optional helpers by name when available.

For Seqera operations, use the `seqera-mcp` skill. Any `platform_*` examples
describe API operations. Discover their exact names and parameter schemas with
`search_seqera_api`, then invoke `call_seqera_api` using those schemas. The host
manages OAuth for the connected MCP server.


# Parabricks

## Purpose

Use this skill to discover the right NVIDIA Parabricks `pbrun` command, assess
runtime readiness, and generate version-aware command guidance for individual
tools and pipelines.

Do **not** use this skill for whole-workflow inspection, acceleration planning,
or wiring optional GPU branches. For pipeline-level work, use
`genomics-workflow-acceleration`.

## When to Use This Skill

- Which `pbrun` tool fits the user's data and goal
- GPU, driver, Docker, container, storage, or installation readiness
- Command shape, flags, and validation for a specific Parabricks tool
- Troubleshooting a single Parabricks command or tool family

## Prerequisites

Ask for input data type, sequencing technology, reference build, sample
structure, desired output, target Parabricks version/container tag, and runtime
target before recommending commands.

If the user is unsure which tool applies, read
tool-index.md first, then load the matching
`pbrun-<tool>.md` file.

## Limitations

This skill routes and guides Parabricks commands. It does not install
Parabricks, infer missing sample metadata, guarantee output parity, provide
clinical interpretation, or promise exact runtime without benchmark data.

## Workflow

1. Confirm the Parabricks version or container tag. Verify the current NVIDIA
   docs when the user asks for the latest tool list or version-sensitive flags.
2. Classify the request:
   - **Runtime** → runtime-environment.md
   - **Tool discovery** → tool-index.md
   - **Specific command** → matching `pbrun-<tool>.md`
3. Collect missing biological and filesystem context before generating commands.
4. Generate conservative Docker commands with explicit mounts, workdir, and
   placeholders. Validate the supplied input references, indexes, and outputs after command generation.

## Tool Reference Index

Load only the reference file for the selected tool.

| Tool | Reference | Use when |
|------|-----------|----------|
| `applybqsr` | pbrun-applybqsr.md | Apply BQSR table to aligned BAM |
| `bam2fq` | pbrun-bam2fq.md | BAM → FASTQ conversion |
| `bamsort` | pbrun-bamsort.md | Standalone BAM sort |
| `bqsr` | pbrun-bqsr.md | Generate BQSR recalibration table |
| `fq2bam` | pbrun-fq2bam.md | Short-read DNA paired FASTQ → BAM/CRAM |
| `fq2bam_meth` | pbrun-fq2bam_meth.md | Bisulfite/methylation FASTQ → BAM/CRAM |
| `giraffe` | pbrun-giraffe.md | Pangenome graph alignment |
| `markdup` | pbrun-markdup.md | Standalone duplicate marking |
| `minimap2` | pbrun-minimap2.md | Long-read FASTQ alignment |
| `rna_fq2bam` | pbrun-rna_fq2bam.md | RNA-seq FASTQ → splice-aware BAM |
| `starfusion` | pbrun-starfusion.md | Fusion detection from chimeric junctions |
| `germline` | pbrun-germline.md | GATK-style germline pipeline from FASTQ |
| `deepvariant_germline` | pbrun-deepvariant_germline.md | DeepVariant germline pipeline from FASTQ |
| `haplotypecaller` | pbrun-haplotypecaller.md | Standalone HaplotypeCaller from BAM/CRAM |
| `deepvariant` | pbrun-deepvariant.md | Standalone DeepVariant from BAM/CRAM |
| `somatic` | pbrun-somatic.md | Tumor-normal somatic pipeline |
| `mutectcaller` | pbrun-mutectcaller.md | Mutect2-compatible somatic calling |
| `deepsomatic` | pbrun-deepsomatic.md | DeepSomatic-based somatic calling |
| `pacbio_germline` | pbrun-pacbio_germline.md | PacBio long-read germline |
| `ont_germline` | pbrun-ont_germline.md | Oxford Nanopore long-read germline |
| `pangenome_germline` | pbrun-pangenome_germline.md | Pangenome-aware germline |
| `pangenome_aware_deepvariant` | pbrun-pangenome_aware_deepvariant.md | Pangenome-aware DeepVariant |
| `prepon` | pbrun-prepon.md | Pangenome-aware preprocessing |
| `postpon` | pbrun-postpon.md | Pangenome-aware post-processing |
| `bammetrics` | pbrun-bammetrics.md | Whole-genome coverage/depth metrics |
| `collectmultiplemetrics` | pbrun-collectmultiplemetrics.md | Multiple Picard/GATK-style alignment metrics |
| `genotypegvcf` | pbrun-genotypegvcf.md | Joint-genotype GVCF input(s) into VCF |
| `indexgvcf` | pbrun-indexgvcf.md | Index GVCF input |
| `dbsnp` | pbrun-dbsnp.md | dbSNP annotation on variant files |

For routing heuristics when multiple tools could apply, see
tool-index.md.

## Runtime Readiness

For GPU, driver, Docker, container, storage, or installation questions, consult
runtime-environment.md. Use the bundled check_parabricks_runtime.py helper only
when the host can make it available. Ask for the user's input, output, and
temporary storage choices when storage checks are needed. Run container probes
only with user consent.

## Command Shape

Derive commands from the selected version's help and the user's actual inputs,
container/runtime, and output choices. Do not prescribe mount locations or
output folders. Check the tool reference before finalizing flags.

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Multiple plausible tools | Data type or goal underspecified | Ask for assay, inputs, caller preference, desired output; use tool-index |
| Exact flag requested | Options are version-sensitive | Check the selected tool reference and NVIDIA docs |
| Runtime question | GPU, Docker, drivers, or storage | Use runtime-environment reference and diagnostic script |
| Wrong tool family | Assay or input type unclear | Confirm DNA/RNA/methylation/long-read/pangenome before routing |
| CUDA or memory failure | Runtime not ready or GPU memory constrained | Assess runtime before tuning command flags |

## Guardrails

- Treat command availability and options as version-sensitive.
- Do not infer exact flags from command names alone.
- Do not collapse standalone tools and full pipelines when explaining tradeoffs.
- Do not substitute DNA `fq2bam` for RNA, or germline for somatic callers.
- Do not invent sample names, read groups, reference builds, known-sites files,
  model files, graph resources, container tags, or output paths.
- Do not install, upgrade, or modify packages. Label setup commands as user-run.
- Do not claim CPU execution of Parabricks tools.
- Do not claim biological or VCF parity without a comparison run.
- Prefer official NVIDIA docs for exact command syntax and option defaults.

## Key References

- Parabricks tool index:
  <https://docs.nvidia.com/clara/parabricks/latest/toolreference.html>
- Getting started:
  <https://docs.nvidia.com/clara/parabricks/latest/gettingstarted.html>
- Overview:
  <https://docs.nvidia.com/clara/parabricks/latest/overview.html>
