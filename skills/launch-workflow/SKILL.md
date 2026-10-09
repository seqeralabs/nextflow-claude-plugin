---
name: launch-workflow
description: >
  Plan, launch or resume Nextflow pipelines locally or through Nextflow Platform.
  Also use for nf-core omics analyses, GEO/SRA acquisition, samplesheets, compute
  and credential setup, data links and Seqerakit automation. Choose the requested
  playbook without forcing a launch; publication, infrastructure creation and
  other mutations need explicit authorization.
---
<!-- Modified for the Nextflow plugin: generic host tools and companion guidance. -->

## Using this skill

Use the tools and runtimes available in the user's session. Establish the
pipeline, input data and execution environment from their request or current
context. Use user-selected locations for files and results. Consult companion
skills, bundled references and optional helpers by name when available.

For Seqera operations, read the [MCP connection](references/seqera-mcp/README.md) connection reference. Any `platform_*` examples
describe API operations. Discover their exact names and parameter schemas with
`search_seqera_api`, then invoke `call_seqera_api` using those schemas. The host
manages OAuth for the connected MCP server.


# Launch or Resume a Pipeline

## Local runs and resume

For a local run, confirm the user's pipeline, parameters, executor and output destination. Use the installed release's `nextflow run` interface; a local run does not require Platform authentication, a remote Git repository or Nextflow 26.04.

Before resuming, read [run identification](../debug-local-run/references/nextflow-history/references/nf-run-history/README.md) and verify the requested run/session and accessible work/cache metadata. Use `-resume` with the selected identity; do not choose a run solely because it is newest. Inspect completion status and representative outputs; a cache hit alone is not scientific-output verification.

For missing runtime setup, read [runtime setup](../build-nextflow-pipeline/references/install-nextflow/README.md). Stop before installing or upgrading without explicit approval.

## Platform launches

Launch Nextflow pipeline executions on cloud (AWS, Google Cloud, Azure) and HPC clusters (Slurm, LSF, etc.) through Nextflow Platform. Nextflow Platform manages the target compute environment, executes the pipeline from a remote Git repository, and provides monitoring.

**Requires Nextflow 26.04 or later** (for the `nextflow auth` and `nextflow launch` commands).

## Main Flow

1. **Configure the compute environment** — select a Nextflow Platform compute environment for the target cloud or cluster.
2. **Ensure the pipeline is in a remote Git repository** — Nextflow Platform launches pipelines from GitHub (or a compatible Git host such as GitLab or Bitbucket). If the local pipeline is not yet hosted, assist the user in setting up the repository.
3. **Select a published revision** — verify that the remote contains the intended code. Publishing local changes requires separate explicit approval; a launch request alone is not authority to commit or push.
4. **Launch with `nextflow launch`** — submit the pipeline by passing the Git repository URL and the expected parameters.

## Step 1: Authenticate with Nextflow Platform

Check whether the user is already authenticated:

```bash
nextflow auth status
```

If not authenticated, sign in:

```bash
nextflow auth login
```

This opens a browser for authentication. Wait for the user to complete the login flow before proceeding.

## Step 2: Configure the Compute Environment

List available compute environments using the Seqera API:

```
call_seqera_api(
  service: "platform",
  api_name: "platform_list_compute_envs",
  parameters: {}
)
```

Selecting the compute environment:

1. Present the available compute environments to the user (name, platform type, region/cluster).
2. If multiple environments are available, ask the user which one to use.
3. If only one is available, propose it and ask for confirmation.
4. Confirm the selected compute environment with the user before launching.

## Step 3: Ensure the Pipeline Is in a Remote Git Repository

Nextflow Platform launches pipelines from a remote Git URL — it cannot launch directly from a local path. Verify the pipeline directory is a Git repository connected to a remote on GitHub (or a compatible host like GitLab or Bitbucket).

Check the current state:

```bash
git remote -v
git status
```

**If the pipeline is not yet a Git repository or has no remote**, assist the user in setting it up:

Explain the missing published revision and ask for separate authorization before initializing Git, creating a remote, staging files or publishing code. Alternatively select an already published revision the user approves.

## Step 4: Upload Local Changes

Compare local changes with the selected remote revision. If the intended code is unpublished, stop and ask whether the user wants a separate commit/push task or a launch of the existing published revision. Only publish after explicit approval, staging only the approved files.

If the working tree is clean and the local branch is in sync with the remote, skip this step.

## Step 5: Launch the Pipeline

Use `nextflow launch` with the user-confirmed public or private Git repository
URL, a pinned revision, and the pipeline parameters from the user's launch
configuration. Obtain input and output destinations from the user rather than
providing example storage locations. Check required parameters before submitting.

A public repository URL such as https://github.com/nf-core/rnaseq identifies the
pipeline; it does not determine the user's inputs or output destination.

### Key options

| Option | Description |
|--------|-------------|
| `-r <revision>` | Pipeline version, branch, or tag |
| `--input` | Input samplesheet or data |
| `--outdir` | Output directory (cloud storage when running on cloud CEs) |
| `-params-file` | User-provided parameter configuration |
| `-resume` | Resume a previous execution |

## Step 6: Monitor the Execution

`nextflow launch` returns a run URL on Nextflow Platform. Retrieve the authoritative submitted workflow using discovered MCP operations and confirm its revision, parameters, compute environment and resume identity. Present the verified run identifier/URL and distinguish submission from successful completion.

## Critical Rules

1. **AUTHENTICATE first** — check `nextflow auth status` before attempting to launch.
2. **CONFIRM the compute environment** — always show the user the selected CE before launching.
3. **REQUIRE a remote Git repository** — the pipeline must be hosted on GitHub or a compatible Git host. If not, help the user set it up before launching.
4. **VERIFY the published revision** — use the approved remote code; obtain separate authorization before committing or pushing local changes.
5. **PASS the Git repository URL** to `nextflow launch`, not a local path.
6. **PIN the revision** — always use `-r` to target a specific branch, tag, or commit for reproducibility.
7. **USE cloud storage for `--outdir`** when the target CE runs on a cloud platform (s3://, gs://, az://).
8. **PRESENT the run URL** returned by `nextflow launch` so the user can monitor the run.

## MCP connection reference

When a Seqera connection is missing or operation discovery is unclear, use the shared connection reference. Otherwise rely on the live tool descriptions and returned schemas. Read [MCP connection](references/seqera-mcp/README.md) before proceeding.

## Compute readiness

For provider credentials or compute setup, follow only the requested setup task; never expose secrets or create infrastructure without approval. Read [compute readiness](references/ce-credentials-setup/README.md) before proceeding.

## Data links

For browsing or managing Platform data links, use discovered schemas and confirm any requested mutations; do not launch a workflow implicitly. Read [data links](references/seqera-data-links/README.md) before proceeding.

## Seqerakit automation

For declarative Platform automation, inspect the requested resources and permissions before executing changes. Read [Seqerakit automation](references/seqerakit/README.md) before proceeding.

## nf-core analyses and public data

For omics analysis, GEO/SRA acquisition or samplesheet creation, follow the requested stage and confirm pipeline, data, genome and output contracts. Bundled helpers are under this playbook directory, not the parent skill directory. Read [nf-core analysis](references/nextflow-development/README.md) before proceeding.
