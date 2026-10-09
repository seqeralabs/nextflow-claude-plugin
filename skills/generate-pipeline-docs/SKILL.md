---
name: generate-pipeline-docs
description: >
  Generate publishable pipeline documentation by analyzing a Nextflow pipeline
  and (optionally) its run patterns on Seqera Platform. Produces
  publishable documents that describe what the pipeline is, how it's used, and the resource
  / config patterns observed in practice. Output is safe to commit and
  publish. Use when the user asks to "document this pipeline", "generate
  pipeline docs", "create public context", "initialize pipeline docs", or
  wants to build a shareable pipeline reference.
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


# Generate Pipeline Documentation

Create publishable documentation describing the pipeline's purpose, inputs,
parameters, configuration, outputs, and observed resource patterns. Use locations
and document names selected by the user or already established for their project.
If file access is unavailable, provide the content in the conversation and state
that no files were written.

Run-specific history and failure evidence belong in private pipeline notes,
handled by `generate-pipeline-memory`.

## Procedure

1. Establish whether the user wants source-only documentation or optional
   aggregate resource patterns from Seqera Platform.
2. Inspect the pipeline files the user provided, including `main.nf`,
   `nextflow.config`, `nextflow_schema.json`, the README, and relevant modules
   when available. Use `nf-pipeline-structure` for complex pipelines.
3. Identify any existing documentation and read it before making updates.
   Preserve useful content and the user's organization.
4. Derive scientific purpose, supported inputs, parameter defaults, profiles,
   container requirements, reference requirements, and output expectations from
   the actual source. Do not infer a fixed project layout.
5. If Platform access is requested, discover workflow and task-list operations
   with `search_seqera_api`, then invoke them through `call_seqera_api` using
   the discovered schemas and the user's workspace.
6. Draft or update the documentation in the user's selected location. Report
   the actual result and any sections that remain unverified.

## Pipeline documentation content

Include only sections supported by evidence:

- Overview: a concise description of the scientific purpose.
- Usage: how to select the pipeline, profile, inputs, reference data, and output
  destination using user-provided values.
- Inputs: supported formats, sample-sheet columns, and reference requirements.
- Key parameters: name, description, default, constraints, and useful notes,
  grouped according to the schema where available.
- Workflow structure: entry point and important steps or modules, described by
  function without prescribing their filesystem organization.
- Profiles: supported execution settings and when to use each.
- Outputs: the kinds of results produced and how the user identifies them.
- Requirements: Nextflow version, container runtime, and reference data.

Use neutral language similar to nf-core or
[bactopia documentation](https://bactopia.github.io/latest/).
Describe scientific behavior rather than unnecessary implementation details.

## Resource-pattern content

Aggregate optional Platform observations into:

- Success and failure counts, duration distributions, and supported revisions.
- Per-process requested CPUs versus actual CPU utilization.
- Requested memory versus observed peak memory and headroom.
- Runtime mean and p95 where the sample supports them.
- Configuration conventions such as profiles and resource labels.

Retain only aggregate statistics. Do not publish run names, IDs, individual run
dates, user identities, sample tags, parameter snapshots, input locations,
bucket names, stderr, or error messages. Avoid retrieving those fields for this
purpose when the API permits narrower requests.

Resource recommendations must cite the aggregate evidence supporting them.
Without utilization data, document configuration conventions and explicitly
state that efficiency estimates are unavailable.

## Privacy and quality

Keep specific failure evidence, known-bad runs, and private organizational
details out of publishable documentation. Do not hardcode data locations that
vary by user or project. Explain location requirements using user-selected
inputs and destinations.

Never invent missing values, runtime statistics, or recommendations. Shorten or
omit unsupported sections. Mark uncertainty and the scope of analyzed data.

## Updates and handoff

Read existing documents before updating them. Merge newly supported parameters,
refresh requested aggregate statistics, preserve still-valid content, and update
the revision date. Do not claim that future chats will load the documents.

Tell the user what was created or updated, where they chose to keep it, why the
content is suitable for publication, what stayed private, and any remaining
data or validation gaps.
