---
name: nf-aggregate
description: >
  Aggregate metrics from Nextflow runs on Seqera Platform using the nf-aggregate
  pipeline. Use for "aggregate runs", "combine run metrics", "run nf-aggregate",
  "aggregate my last N runs", or a MultiQC report comparing multiple runs.
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


# nf-aggregate on Seqera Platform

Run `https://github.com/seqeralabs/nf-aggregate` to combine metrics from multiple
Nextflow runs into a MultiQC report and comparison artifacts. Use the user's
existing selected workspace and pin the pipeline to a verified release tag or
commit before launch.

## Platform connection and API discovery

All workspace, workflow, dataset, compute environment, and launch operations use
the production Seqera MCP connection. The client completes OAuth; the server
handles Platform authentication. Never request or print tokens, bearer headers,
cloud keys, or credential contents. Do not use Platform curl or `tw` as a fallback.

Before every type of operation:

1. Call `search_seqera_api` with the intended operation.
2. Inspect the selected result's complete parameter schema, including optional
   launch fields and nested objects.
3. Invoke only `call_seqera_api(service="platform", api_name=<returned name>,
   parameters=<schema-matching arguments>)` to execute the Platform operation.

An operation name such as `platform_create_dataset` is an API name obtained from
search, not a separately callable tool. Use the returned field casing, nesting,
and types. Broaden discovery or report a missing capability if an operation is
unavailable; do not invent endpoint names or arguments. See `seqera-mcp` and
`launch-workflow` for the shared discovery and launch guidance.

## 1. Select the workspace and source runs

Use the workspace the user has selected. Discover accessible-workspace listing
and resolve its ID and organization/workspace slug from the actual response.
If the workspace is unspecified or ambiguous, obtain the user's selection before
creating a dataset or launching a run. Do not choose an internal or default
workspace on the user's behalf.

Discover workflow listing or lookup and retrieve the runs the user requested.
For "last N runs", apply the user's pipeline, date, and status constraints,
check ordering, and paginate as needed. Include only the selected source runs;
do not accidentally include a previous aggregation run. Check the actual
workflow metadata and relevant run artifacts for suitability before launch.
If a requested run has insufficient metrics or inaccessible outputs, identify
the gap instead of silently replacing it.

## 2. Prepare the run manifest

Create CSV content with the pipeline's expected columns:

```csv
id,workspace
<source-run-id-1>,<organization>/<workspace>
<source-run-id-2>,<organization>/<workspace>
```

Use returned Platform workflow IDs and workspace slugs. Preserve each run's
actual workspace when a user explicitly requests a comparison across workspaces
and their access supports it. Quote CSV values correctly and remove unintended
duplicate rows. The manifest may be prepared in memory; a local file is optional.

## 3. Create and upload a dataset

Discover dataset creation and upload operations, then execute them with the
selected workspace ID and schema-matching arguments. Create a descriptive CSV
dataset with a header and upload the prepared content. Keep the returned dataset
ID and version or content URI; verify the upload result before launching.

Prefer the content URI returned by Platform. If the pipeline needs a `tw://`
reference, resolve the dataset's actual version rather than assuming version 1:

```text
tw://<organization>/<workspace>/datasets/<dataset-id>/versions/<version>/content
```

Record a successfully created dataset before proceeding. If upload fails, report
that partial outcome and reuse or repair that dataset when appropriate rather
than creating duplicate datasets on every retry.

## 4. Resolve revision, compute, output path, and runtime access

Read the official pipeline README and parameter schema at the selected release
tag or commit. Verify the `input` and `outdir` parameters and any additional
parameters or runtime requirements for that revision. Resolve a user-specified
revision first; otherwise select and record a suitable published release and
resolve it to an immutable commit when possible. Never launch the moving default
branch without a pin. Pass the revision using the actual launch schema.

Discover compute-environment listing in the selected workspace. Use a compatible
available environment already selected by the user, or obtain a selection when
several choices remain. Verify the intended output URI is suitable for that
environment and accessible with its configured storage credentials. Use the
user's existing output location or an authorized prefix; do not invent a bucket.

Check how the selected nf-aggregate revision accesses Platform run metrics from
its task runtime. MCP OAuth authorizes the agent's API calls; it does not by
itself establish authentication inside the launched workflow. Reuse the existing
compute environment's supported secret or authentication configuration. If
runtime access has not been configured, explain the missing setup and use the
appropriate Platform workflow to resolve it without requesting or revealing
secrets in chat.

## 5. Launch and verify the aggregation run

Discover the launch operation and inspect its full schema. Use the selected
workspace, compatible compute environment, descriptive run name, repository,
pinned revision, and verified parameters. Conceptually the pipeline parameters
include:

```json
{
  "input": "<verified dataset content URI>",
  "outdir": "<verified output URI>/nf-aggregate-results"
}
```

Map those values into the schema's correct parameter/config representation;
do not assume it accepts a top-level `params` object or flattened revision.
Follow `launch-workflow` when a saved Launchpad pipeline is the requested launch
source so its lineage and labels are preserved.

Execute the launch through `call_seqera_api` and inspect the returned workflow
ID and state. Discover workflow lookup to verify that the run was submitted.
If the launch response is ambiguous or times out, look for the submitted run
before retrying so a retry does not launch duplicates.

Return the verified monitor URL from the API when available. Otherwise use the
configured Platform URL and verified organization/workspace/run identifiers to
construct and check the watch link. Report the source-run count, dataset,
repository and pinned revision, compute environment, output location, and
submitted workflow ID. A submitted run is not a completed report.

## Outputs

The source pipeline produces an aggregated MultiQC report, raw run data, and
comparison outputs. Depending on revision and source data these include:

- the MultiQC report — combined metrics report.
- `runs_dump/` — raw run data per pipeline.
- Gantt report files — Gantt charts for supported Fusion runs.
- Comparison plots for CPU time, wall time, and cost.

Check the chosen revision's documentation and the completed run's actual output
listing before promising a specific artifact. If the user requests the finished
report, follow the run through completion and retrieve the report through the
available Platform API. Summarize failures from returned logs and metadata.
