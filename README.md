# Nextflow plugin for Claude

Build, migrate, test, debug and run [Nextflow](https://www.nextflow.io) pipelines with
Claude, connected to [Nextflow Platform](https://seqera.io), Wave containers and nf-core.

The plugin bundles 28 skills and the hosted Seqera MCP server (`https://mcp.seqera.io/mcp`).

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
the Nextflow Platform sign-in (OAuth). Skills that only work with local files and Nextflow do
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
| Build pipelines | `build-nextflow-pipeline`, `nf-pipeline-design`, `nextflow-config`, `nextflow-schema`, `nextflow-output-patterns`, `search-existing-modules`, `run-module`, `create-container` |
| Convert to Nextflow | `build-nextflow-pipeline` (Python, R and notebook playbooks), `migrate-from-snakemake`, `audit-conversion-readiness`, `nextflow-schema` (parameter triage), `find-alternative-tools` |
| Migrate and modernise | `migrate-nextflow-code` (version, strict-syntax and boolean references), `nextflow-schema` (schema migration), `nf-plugin-development`, `nf-plugin-legacy-migration`, `maintain-nf-core-pipeline` |
| Test and debug | `nf-test` (authoring and failure repair), `repair-workflow` (including static diagnostics), `debug-local-run`, `debug-seqera-failed-run`, `nextflow-history` (history, cache and narrative recaps), `nf-data-lineage`, `nf-docker-scripts` |
| Nextflow Platform | `launch-workflow` (with shared MCP connection reference), `ce-credentials-setup`, `seqera-data-links`, `seqerakit` |
| General | `nextflow-development`, `install-nextflow` |

## Licensing

Licensed under the [Apache License, Version 2.0](LICENSE). Third-party attributions are in
[`NOTICE`](NOTICE), and per-file origin is recorded in [`sources.json`](sources.json).

The Apache-2.0 license covers the files in this repository. The hosted Seqera MCP server it
connects to is a separate work, governed by its own license and Seqera's terms of service.

## Development

The plugin content is generated from a host-neutral Agent Plugins package. To update it:

```bash
python3 -I tools/import_package.py /path/to/nextflow.zip
python3 -I tools/check_sources.py
python3 -I tools/test_consolidate_skills.py
claude plugin validate --strict .
```

`import_package.py` replaces `skills/`, `scripts/`, `assets/`, `licenses/` and `sources.json`, and
regenerates `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and `.mcp.json`.
Do not edit those paths by hand; change the upstream package instead.

The importer also drops the skills listed in `EXCLUDED_SKILLS` and applies the text edits in
`EDITS`. It then replays `tools/skill_consolidations.json`: removed entrypoints become linked
playbooks under their surviving skill, including supporting files and original provenance.
Change that plan (and any referenced curation assets), rather than editing generated skills.
To apply a new consolidation to an already imported tree, run:

```bash
python3 -I tools/consolidate_skills.py
python3 -I tools/check_sources.py
```

To release, bump `VERSION` in `tools/import_package.py`, re-import, merge, then tag:

```bash
claude plugin tag .
```

Installed copies pick up the new version on `claude plugin update nextflow@nextflow-claude-plugin`,
or automatically if the user has marketplace auto-update enabled.
