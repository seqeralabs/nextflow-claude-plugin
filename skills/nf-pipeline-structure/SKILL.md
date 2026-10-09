---
name: nf-pipeline-structure
description: >
  Analyze the structure of a local Nextflow pipeline — processes, workflows,
  modules, subworkflows, channels, and how data flows between them. Use when the
  user asks how a pipeline is organized, what it does, or how components connect.
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


# Nextflow Pipeline Structure Analysis

Understand and explain how a Nextflow pipeline is organized and how data flows
through it.

## Companion skills

After analyzing structure, chain to a syntax-fix skill when the task is to migrate:

- `nextflow-26-syntax` — strict-syntax rules for typed processes / channels
- `nf-v2-boolean-params` — boolean-param migration (common v2 failure)
- `nf-schema-migration` — schema updates required by v2

## When to Use

Load this skill when the user wants to:
- Understand what a pipeline does and how it's structured
- See how processes and channels connect
- Navigate a large nf-core or custom pipeline codebase
- Understand the data flow from inputs to outputs
- Know which modules/subworkflows are used

## Pipeline Layout Conventions

### Standard Nextflow pipeline

Organize the entry workflow, reusable definitions, configuration, helper commands,
tests, and supporting data according to the user's existing project. Locate each
component from the files the user provides rather than assuming a directory layout.

### Key: not all pipelines follow this layout

Simple pipelines may be a single `main.nf`. Inspect what actually exists before
assuming nf-core conventions.

## Analysis Procedure

### Step 1: Identify the entry point and layout

Inspect the user-provided source files. Identify the entry workflow, configuration,
parameter schema, and any nf-core metadata from their content and relationships.

### Step 2: Read the main workflow

Read the selected entry-workflow source.

Look for:
- `include { ... } from '...'` — what modules/subworkflows are imported
- `workflow { ... }` — the main workflow block, showing execution order
- `params.*` — input parameters
- Channel factories (`Channel.fromFilePairs`, `Channel.of`, etc.)

### Step 3: Trace the module/subworkflow tree

Follow include declarations through the provided source files to map dependencies.
Exclude generated task files and runtime cache data from the source analysis.

### Step 4: Understand process definitions

For each key process:

Read each selected module or process definition from the sources the user provides.

Look for:
- `input:` — what channels feed into this process
- `output:` — what channels it produces (and `emit:` labels)
- `script:` / `shell:` — what command runs
- `container` / `conda` — execution environment
- `publishDir` — where results land

### Step 5: Map the data flow

Trace how channels connect processes. In Nextflow DSL2:

```groovy
// Channels connect via workflow block
workflow {
    reads = FASTQC(input_ch)           // process emits to 'reads'
    TRIM(reads.trimmed)                 // next process consumes it
    ALIGN(TRIM.out.reads, genome_ch)    // chaining
}
```

Key channel operators to watch for:
- `.mix()`, `.concat()` — combining channels
- `.map {}`, `.filter {}` — transforming
- `.join()`, `.combine()` — merging by key
- `.collect()` — gathering all items
- `.branch {}` — splitting by condition
- `.groupTuple()` — grouping by key (common with meta maps)

### Step 6: Check configuration context

Read the effective process configuration and any configuration files it includes.
Identify resource settings, per-process overrides, and publication settings.

## Response Guidelines

**Do:**
- Start with a high-level summary: "This is an RNA-seq pipeline with 12 processes
  organized in 3 phases: QC, alignment, and quantification"
- Describe the data flow as a narrative: inputs → processing stages → outputs
- Group related processes into logical phases/stages
- Note which tools/containers each process uses
- Mention where results end up (publishDir patterns)
- Highlight the main input parameters the user would typically set

**Don't:**
- Dump every line of every .nf file
- List processes without explaining how they connect
- Ignore the config — resource settings and module overrides matter
- Assume nf-core structure if the pipeline is custom
- Ignore helper commands — they may contain important analysis logic

## Example Response Style

> This is a variant calling pipeline with 8 processes in 3 stages:
>
> **Input**: Takes paired-end FASTQ files and a reference genome via `--input`
> sample sheet and `--genome` parameter.
>
> **Stage 1 — QC & Preprocessing**: `FASTQC` runs quality checks, then
> `TRIM_GALORE` removes adapters. Both run per-sample in parallel.
>
> **Stage 2 — Alignment**: `BWA_MEM` aligns reads to the reference. The aligned
> BAMs go through `SAMTOOLS_SORT` and `SAMTOOLS_INDEX`. These are nf-core modules
> from nf-core.
>
> **Stage 3 — Variant Calling**: `GATK_HAPLOTYPECALLER` calls variants per-sample,
> then `GATK_GENOTYPEGVCFS` does joint genotyping across all samples (uses
> `.collect()` to gather all gVCFs).
>
> **Output**: Final VCFs published to the user-selected output destination. A MultiQC
> report aggregates QC from all stages.
>
> The pipeline has `docker` and `singularity` profiles configured. Default
> resources are 4 CPUs / 8 GB per process, with GATK steps getting 16 GB.
