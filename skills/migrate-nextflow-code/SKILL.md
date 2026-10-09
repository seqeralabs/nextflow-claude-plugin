---
name: migrate-nextflow-code
description: Migrate Nextflow pipeline code while preserving behavior. Use for version upgrades including 25.04 compatibility, strict syntax errors, boolean CLI parameter types, topic channels, workflow outputs, and static typing (typed processes/workflows, records, typed params).
---
<!-- Modified for the Nextflow plugin: generic host tools and companion guidance. -->

## Using this skill

Use the tools and runtimes available in the user's session. Establish the
pipeline, input data and execution environment from their request or current
context. Use user-selected locations for files and results. Consult companion
skills, bundled references and optional helpers by name when available.

For Seqera operations, read the [MCP connection](../launch-workflow/references/seqera-mcp/README.md) connection reference. Any `platform_*` examples
describe API operations. Discover their exact names and parameter schemas with
`search_seqera_api`, then invoke `call_seqera_api` using those schemas. The host
manages OAuth for the connected MCP server.


# Migrate Nextflow Code

Migrate Nextflow pipeline code to satisfy newer language requirements. Each migration is detection-driven: a tool reports what must change, you apply behavior-preserving fixes, then re-run the tool until it is clean.

**Resolve the installed and target Nextflow versions first.** The modern examples target 26.04+, where strict syntax is the default. For a 25.04 target, read [25.04 compatibility](references/nf-migrate-25-04/README.md) and its scanners; do not silently upgrade the runtime or apply newer syntax. Check installed help/current official migration notes before using version-dependent features.

**nf-core pipelines — check the template version before starting.** If the pipeline has a `.nf-core.yml`, check which version of nf-core/tools last generated its template. If `nf_core_version` is unspecified or less than 3.0.0, **stop**. Tell the user to upgrade their template first (`nf-core pipelines sync`) before attempting any code migrations. This will resolve syntax errors in the template code and provide a cleaner baseline.

## How to use this skill

This SKILL.md is an **index**. Identify which migration the user needs from the table below, then **read the matching reference file** for the full detect → fix → verify procedure before doing any work. Each reference file is self-contained.

| Migration | Use when the user… | Read this file |
|-----------|--------------------|----------------|
| **25.04 compatibility** | …targets 25.04 or crosses that release | [25.04 compatibility](references/nf-migrate-25-04/README.md) |
| **Boolean CLI params** | …has a string/boolean type mismatch or a flag that does not toggle | [boolean parameter compatibility](references/nf-v2-boolean-params/README.md) |
| **Strict syntax** | …has parser errors or asks to run `nextflow lint` | `strict-syntax.md`, plus [version-specific rules](references/nextflow-26-syntax/README.md) |
| **Topic channels** | …wants to replace the `ch_versions` plumbing (or another channel threaded through every workflow) with a topic channel | `topic-channels.md` |
| **Static typing** | …wants to add static types — typed process/workflow inputs and outputs, records (replacing tuples), or typed params | `static-typing.md` |
| **Workflow outputs** | …wants to replace `publishDir` directives with workflow outputs — a top-level `output {}` block and a `publish:` section in the entry workflow | `workflow-outputs.md` |

If the request matches no row, tell the user which migrations are currently supported rather than improvising.

For multiple requested migrations, agree a staged plan based on the target release and project dependencies. Establish a working baseline first, then complete one stage at a time with lint, representative tests and output comparisons. Strict syntax normally comes first; topic channels, types and workflow outputs need only be adopted when requested and supported. A green stage is the stopping point if the next cannot be verified.

## Critical Rules

These hold regardless of which reference file you load. Each reference file adds its own migration-specific rules.

1. **Detect before editing** — follow the reference guidelines to determine what needs changing. Never guess.
2. **Preserve behavior** — a migration adapts code to new language requirements; it is not a refactor. Apply the smallest change that resolves each issue and leave unrelated logic alone.
3. **Verify** — run the project's tests (`nf-test test`, or `nextflow run <pipeline> -profile test,docker -resume`) to confirm behavior is unchanged before declaring the migration done.

## Strict syntax compatibility reference

When fixing v2 parser errors or planning staged modernization, consult the version-specific syntax rules and preserve a tested output baseline. Read [strict syntax compatibility](references/nextflow-26-syntax/README.md) before proceeding.

## Boolean parameter compatibility reference

When CLI boolean flags arrive with the wrong type or do not toggle under strict syntax, check the typed-parameter and schema contract. Read [boolean parameter compatibility](references/nf-v2-boolean-params/README.md) before proceeding.

## Nextflow 25.04 compatibility reference

When targeting 25.04 or diagnosing compatibility across that release, use its changelog and scanners without assuming 26.x features. Read [25.04 compatibility](references/nf-migrate-25-04/README.md) before proceeding.


## Optional specialist work

For infrastructure setup, nf-core maintenance/analysis, plugin development or broad provenance work, read [optional pack handoffs](../build-nextflow-pipeline/references/optional-packs.md). Check available namespaced skills first; if the pack is absent, explain how to explicitly install/enable it and stop that specialist task. Ordinary debugging and launch/resume remain in core.

When editing an nf-core project, read [nf-core safety](../build-nextflow-pipeline/references/nf-core-safety.md); basic safe edits do not require the optional maintenance pack.
