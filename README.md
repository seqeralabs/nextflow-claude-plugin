# Nextflow plugin for Claude

Build, migrate, test, debug and run [Nextflow](https://www.nextflow.io) pipelines with
Claude, connected to [Nextflow Platform](https://seqera.io), Wave containers and nf-core.

The default plugin bundles **11 core skills** and the hosted Seqera MCP server
(`https://mcp.seqera.io/mcp`). Four separately installed optional packs add eight
specialist entrypoints; installing every pack exposes **19 skills**, not 11.

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

| Core job | Skills |
| --- | --- |
| Build and design | `build-nextflow-pipeline`, `nf-pipeline-design`, `create-container` |
| Parameters and execution config | `nextflow-schema`, `nextflow-config` |
| Repair and debug | `repair-workflow`, `debug-local-run`, `debug-seqera-failed-run` |
| Test and modernise | `nf-test`, `migrate-nextflow-code` |
| Launch and resume | `launch-workflow` |

Construction includes selectively loaded playbooks for Python/R/notebook and
Snakemake conversion, read-only readiness audits, module discovery/native runs,
requested tool comparisons and runtime setup. Design owns output-correctness
patterns; containers own script-placement/packaging guidance. A bounded helper
request does not force pipeline creation or container construction.

Core keeps the run/cache identification needed for ordinary debugging and resume,
and basic nf-core-safe editing rules. Broader specialist procedures are optional.

### Optional packs

Install core first, then explicitly install only the packs you need:

| Plugin | Specialist entrypoints |
| --- | --- |
| `nextflow-platform` | `ce-credentials-setup`, `seqera-data-links`, `seqerakit` |
| `nextflow-nf-core` | `nextflow-development` (omics analysis/GEO/SRA), `maintain-nf-core-pipeline` |
| `nextflow-plugins` | `nf-plugin-development` (including legacy registry migration) |
| `nextflow-provenance` | `nextflow-history`, `nf-data-lineage` |

```bash
claude plugin install nextflow-platform@nextflow-claude-plugin
claude plugin install nextflow-nf-core@nextflow-claude-plugin
claude plugin install nextflow-plugins@nextflow-claude-plugin
claude plugin install nextflow-provenance@nextflow-claude-plugin
```

These are opt-in commands, not required installation steps. Enable core alongside
any optional pack. Packs do not declare auto-installing dependencies or register
another MCP server; Platform operations reuse core's Seqera connection. Local
work does not need Platform OAuth. Missing specialists are reported by name,
not silently installed.

Skill identities are namespaced, for example
`nextflow:build-nextflow-pipeline` and `nextflow-plugins:nf-plugin-development`.
Cross-plugin handoffs use these identities rather than filesystem paths between
installed cache directories.

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
python3 -I tools/test_skill_packs.py
claude plugin validate --strict .
python3 -I tools/verify_skill_packs.py
```

`import_package.py` replaces `skills/`, `scripts/`, `assets/`, `licenses/`, `packs/`
and `sources.json`, and regenerates `.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, optional-pack manifests and `.mcp.json`.
Do not edit those paths by hand; change the upstream package instead.

The importer also drops the skills listed in `EXCLUDED_SKILLS` and applies the text edits in
`EDITS`. It then replays `tools/skill_consolidations.json`: removed entrypoints become linked
playbooks under their surviving skill, including supporting files and original provenance.
It then applies `tools/core_skill_consolidations.json` and partitions the result
using `tools/skill_packs.json`. Supporting assets and original provenance move
with their owner; cross-plugin file links become namespaced handoffs. Shared
connection/safety resources are generated from single curation sources.

Change these plans and curation assets, then re-import; do not hand-edit generated
skills or move optional directories manually. `tools/build_skill_packs.py` can
build a previously imported, unpartitioned catalog or validate a completed replay.
A changed plan requires re-import so the unsplit source is available again.

`check_sources.py` also verifies complete skill-resource inventories, matching
marketplace/manifest versions, local links within each installed plugin root,
and the absence of duplicate optional MCP registrations.
`verify_skill_packs.py` installs core, each core/pack combination, all packs, and
an optional pack alone in fresh temporary Claude configurations. It makes no
Platform calls and checks exact skill discovery plus server registration counts.

### Behavioral smoke tests

The authored `evals/*/prompt.md` cases exercise bounded requests, missing-pack
handoffs, publication authority and a small Snakemake conversion. Run locally
with your own Claude authentication; this uses model quota and is not part of
unauthenticated CI:

```bash
claude plugin eval . --trust-plugin --no-publish --ablation none \
  --runs 3 --allow-tools Write Edit --scaffold --keep-temp
```

The scaffold only supplies synthetic fixture files. Bash is deliberately not
granted; generated conversions require separate execution/output comparisons.
Routing smoke tests are not proof of general scientific equivalence or an
optimal skill count.

To release, bump `VERSION` in `tools/import_package.py`, re-import, merge, then tag:

```bash
claude plugin tag .
```

Installed copies pick up the new version on `claude plugin update nextflow@nextflow-claude-plugin`,
or automatically if the user has marketplace auto-update enabled.
