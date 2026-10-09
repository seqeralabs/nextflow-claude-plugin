# Nextflow plugin for Claude and Codex

Build, migrate, test, debug and run [Nextflow](https://www.nextflow.io) pipelines with
Claude or Codex, connected to [Nextflow Platform](https://seqera.io), Wave containers and nf-core.

The plugin bundles **11 skills** and the hosted Seqera MCP server (`https://mcp.seqera.io/mcp`).
Specialist procedures remain available as selectively loaded references; no extra plugins are needed.

## Install

In Claude Code:

```
/plugin marketplace add seqeralabs/nextflow-plugin
/plugin install nextflow@nextflow-plugin
```

Or from a shell:

```bash
claude plugin marketplace add seqeralabs/nextflow-plugin
claude plugin install nextflow@nextflow-plugin
```

Restart Claude Code after installing. The first time a Seqera tool is used, Claude Code opens
the Nextflow Platform sign-in (OAuth). Skills that only work with local files and Nextflow do
not need a Seqera account.

To make the plugin available to everyone working in a repository, add it to that repository's
`.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "nextflow-plugin": {
      "source": { "source": "github", "repo": "seqeralabs/nextflow-plugin" }
    }
  },
  "enabledPlugins": { "nextflow@nextflow-plugin": true }
}
```

### Codex

In the Codex app, open **Plugins → Add → Add plugin marketplace**, enter
`seqeralabs/nextflow-plugin` as the source and install **Nextflow**. Or from a shell:

```bash
codex plugin marketplace add seqeralabs/nextflow-plugin
codex plugin add nextflow@nextflow-plugin
```

The same repository serves both hosts: Codex reads the Claude marketplace and plugin layout,
and takes its listing (name, logo, starter prompts) from `.codex-plugin/plugin.json`.

## What's included

| Area | Skills and selectively loaded procedures |
| --- | --- |
| Build and convert | `build-nextflow-pipeline` — Python/R/notebooks/Snakemake, readiness audits, module discovery/native runs, requested tool comparisons and runtime setup |
| Design and package | `nf-pipeline-design` — code structure and output correctness; `create-container` — containers and script staging/packaging |
| Configure and validate | `nextflow-config`, `nextflow-schema` — parameters, schemas and validation migrations |
| Test and repair | `nf-test`, `repair-workflow` |
| Debug and trace | `debug-local-run` — local failures, run/cache history and lineage; `debug-seqera-failed-run` — Platform failures |
| Modernise | `migrate-nextflow-code` — language migrations, plugin authoring/legacy migration and nf-core maintenance |
| Run and launch | `launch-workflow` — local/Platform execution, nf-core/GEO/SRA analyses, compute readiness, data links and Seqerakit |

Each skill links its specialist playbooks and keeps their supporting assets. Read only the
matching playbook and stop at the requested task: an audit does not require pipeline creation,
compute setup does not authorize a launch, and a launch does not authorize committing or pushing.

## Licensing

Licensed under the [Apache License, Version 2.0](LICENSE). Third-party attributions are in
[`NOTICE`](NOTICE), and per-file origin is recorded in [`sources.json`](sources.json).

The Apache-2.0 license covers the files in this repository. The hosted Seqera MCP server it
connects to is a separate work, governed by its own license and Seqera's terms of service.
