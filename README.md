# Nextflow plugin for Claude

Build, migrate, test, debug and run [Nextflow](https://www.nextflow.io) pipelines with
Claude, connected to [Seqera Platform](https://seqera.io), Wave containers and nf-core.

The plugin bundles 50 skills and the hosted Seqera MCP server (`https://mcp.seqera.io/mcp`).

## Install

In Claude Code:

```
/plugin marketplace add seqeralabs/nextflow-claude-plugin
/plugin install nextflow@nextflow-claude-plugin
```

Or from a shell:

```bash
claude plugin marketplace add seqeralabs/nextflow-claude-plugin
claude plugin install nextflow@nextflow-claude-plugin
```

Restart Claude Code after installing. The first time a Seqera tool is used, Claude Code opens
the Seqera Platform sign-in (OAuth). Skills that only work with local files and Nextflow do
not need a Seqera account.

To make the plugin available to everyone working in a repository, add it to that repository's
`.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "nextflow-claude-plugin": {
      "source": { "source": "github", "repo": "seqeralabs/nextflow-claude-plugin" }
    }
  },
  "enabledPlugins": { "nextflow@nextflow-claude-plugin": true }
}
```

## What's included

| Area | Skills |
| --- | --- |
| Build pipelines | `create-workflow`, `build-nextflow-pipeline`, `nf-pipeline-design`, `nf-pipeline-structure`, `nextflow-config`, `nextflow-schema`, `nextflow-output-patterns`, `search-existing-modules`, `run-module`, `create-container` |
| Convert to Nextflow | `convert-python-script`, `convert-r-script`, `convert-jupyter-notebook`, `migrate-from-snakemake`, `audit-conversion-readiness`, `triage-pipeline-parameters`, `find-alternative-tools`, `enumerate-alternative-tools` |
| Migrate and modernise | `migrate-nextflow-code`, `nextflow-26-syntax`, `nf-migrate-25-04`, `nf-schema-migration`, `nf-v2-boolean-params`, `nf-plugin-development`, `nf-plugin-legacy-migration`, `maintain-nf-core-pipeline` |
| Test and debug | `nf-test`, `repair-nf-test`, `repair-workflow`, `nf-debug`, `debug-local-run`, `debug-seqera-failed-run`, `nextflow-history`, `nf-run-history`, `nf-data-lineage`, `nf-storedir`, `nf-docker-scripts` |
| Seqera Platform | `launch-workflow`, `seqera-mcp`, `ce-credentials-setup`, `seqera-data-links`, `seqerakit`, `nf-aggregate`, `seqera-cli-agent`, `generate-pipeline-docs`, `generate-pipeline-memory` |
| Accelerated genomics | `parabricks`, `genomics-workflow-acceleration` |
| General | `nextflow-development`, `install-nextflow` |

## Licensing

This repository contains material under more than one license. See [`licenses/`](licenses/)
and the `LICENSE.txt` files inside individual skill directories. Per-file origin is recorded in
[`sources.json`](sources.json).

## Development

The plugin content is generated from a host-neutral Agent Plugins package. To update it:

```bash
python3 -I tools/import_package.py /path/to/nextflow.zip
python3 -I tools/check_sources.py
claude plugin validate --strict .
```

`import_package.py` replaces `skills/`, `scripts/`, `assets/`, `licenses/` and `sources.json`, and
regenerates `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and `.mcp.json`.
Do not edit those paths by hand; change the upstream package instead.

To release, bump the version in the upstream package, re-import, merge, then tag:

```bash
claude plugin tag .
```

Installed copies pick up the new version on `claude plugin update nextflow@nextflow-claude-plugin`,
or automatically if the user has marketplace auto-update enabled.
