# Follow-up: 11 default Nextflow skills

Status: implemented on `feat/nextflow-core-and-optional-packs`, following PR #1's 28-skill catalog. The generated marketplace now lists the core plugin and four optional plugins. This file records the approved design; execution evidence and limits are in [verification](../verification/11-skill-core.md). No release/tag has been performed.

## Purpose

Help a pipeline author build, change, diagnose and run a correct Nextflow pipeline. Keep authorization, scientific-output checks, runtime compatibility and completion evidence; reduce globally advertised entrypoints rather than deleting specialist knowledge.

## Exact default entrypoints (11)

| Keep | Owns |
| --- | --- |
| `build-nextflow-pipeline` | Construction, source conversion, bounded readiness audits, module reuse and direct module execution |
| `nf-pipeline-design` | Channel contracts, workflow structure and correct aggregation/output semantics |
| `repair-workflow` | Minimal evidence-based pipeline repair and static diagnostics |
| `debug-local-run` | Local run/task artifacts and causal failure diagnosis |
| `debug-seqera-failed-run` | Platform failure diagnosis, cascades, attempts and confidence |
| `nf-test` | Test authoring and failure repair without hiding regressions |
| `migrate-nextflow-code` | Behavior-preserving, release-aware Nextflow modernization |
| `nextflow-schema` | Parameter and samplesheet contracts, triage and schema migration |
| `nextflow-config` | Profiles, resource selectors, precedence and execution configuration |
| `create-container` | Dependency/container decisions, script packaging and representative command/output validation |
| `launch-workflow` | Local/Platform launch and resume decisions, including authoritative post-action readback |

No twelfth routing skill: broaden the surviving descriptions and add short conditional playbook links. A module-only run, audit-only request or comparison must remain bounded; routing through construction must not force pipeline creation.

## Fold the remaining eight helper entrypoints

| Remove standalone entrypoint | Single owning destination | Risk to prevent |
| --- | --- | --- |
| `migrate-from-snakemake` | Construction → Snakemake conversion playbook | Preserve wildcard/DAG/scheduler semantics and golden-output comparisons |
| `audit-conversion-readiness` | Construction → read-only conversion preflight | Do not write pipeline code for an audit request; distinguish unavailable access from absent data |
| `search-existing-modules` | Construction → module discovery/reuse playbook | Keep reuse/vendor/write-new verdicts and verified contracts |
| `run-module` | Construction → native module validation/run playbook | Verify installed command support; do not create a wrapper just to run a registry module |
| `find-alternative-tools` | Construction → requested tool-comparison playbook | Research is not authorization for additional branches |
| `install-nextflow` | Construction → shared runtime setup playbook, linked by launch/debug/migration | No automatic install/upgrade; minimum version is operation-specific, not a blanket 26.04 requirement |
| `nextflow-output-patterns` | Design → output-correctness playbook, linked by repair | Preserve aggregation, join cardinality and null-handling checks |
| `nf-docker-scripts` | Containers → script-placement/packaging playbook, linked by design/construction | Keep process-script guidance usable without forcing a Docker build; preserve all supporting assets |

References are stored once under their owner. Other core skills link to them rather than copying their bodies. Supply the relevant reference to helper subagents; do not assume the host can invoke a removed skill identity.

## Move nine current entrypoints into four optional packs

Proposed distribution: separately installable Claude plugins in the same marketplace, with `nextflow` remaining the default/core plugin.

| Proposed plugin | Current skills to move | Optional entrypoints after consolidation |
| --- | --- | --- |
| `nextflow-platform` | `ce-credentials-setup`, `seqera-data-links`, `seqerakit` | 3 |
| `nextflow-nf-core` | `nextflow-development`, `maintain-nf-core-pipeline` | 2 |
| `nextflow-plugins` | `nf-plugin-development`, `nf-plugin-legacy-migration` | 1: development, with legacy migration as a playbook |
| `nextflow-provenance` | `nextflow-history`, `nf-data-lineage` | 2: keep cache/run history distinct from lineage-store semantics |

`nextflow-development` currently means nf-core analysis and GEO/SRA acquisition, not general pipeline authoring. Keep that scope explicit in the optional pack.

Count: **28 − 8 folded helpers − 9 moved entries = 11 default skills**. Folding plugin legacy migration inside its optional pack leaves **8 optional entrypoints**, or **19 skills with every pack installed**. Eleven is a default surface, not a cap on all installed capabilities.

## Loading and ownership boundaries

- Optional plugins are explicitly installed/enabled; never silently install them. Core can identify the relevant pack without registering every optional procedure by default.
- Core remains self-sufficient for ordinary execution, local/Platform debugging, resume selection and output verification. Keep minimal run/cache identification needed by those tasks in core; only broader history analysis and lineage exploration move out.
- Preserve basic nf-core-safe editing and applicable scaffold/lint invariants in core. Template sync, upstream contributions and omics-analysis orchestration belong in the nf-core pack. An optional maintenance pack must not be required just to avoid unsafe edits.
- Core retains the hosted Seqera MCP connection. Optional plugins must not register duplicate server connections. Their descriptions should state the core connection prerequisite; verify this install combination before release.
- Resolve optional/core handoffs through installed skill identities and supported host discovery, not relative paths crossing installed plugin roots. Carry minimum connection/safety guidance with an optional pack if needed; do not duplicate API schemas.
- Keep upstream/canonical procedure ownership separate from Claude distribution. Generate every package through an explicit importer partition contract; do not hand-edit generated skill trees or depend on undeployed MCP Skills-extension support.

## Implementation and acceptance gates

1. Extend the declarative import plan to fold the eight helpers and partition core/optional output paths, assets and provenance. Update callers and broaden core descriptions so standalone helper requests still route correctly.
2. Generate the four optional plugin manifests and marketplace entries, with explicit installation guidance and no duplicate MCP configuration. Fold legacy plugin migration within its pack.
3. Test exact inventories, idempotent replay, upstream edit drift, full resource retention, local links and all generated hashes. No default skill may depend on an absent optional file.
4. In an isolated Claude configuration, install core alone and verify exactly 11 skills; install each optional pack individually alongside core, then all packs together and verify 19 skills and one hosted MCP connection. Verify namespaced handoffs and unavailable-pack behavior in that host rather than assuming them.
5. Evaluate representative bounded requests: readiness audit (no edits), direct module execution (no wrapper), Snakemake conversion (golden outputs), single-tool construction (no extra branches), output aggregation, script staging, local failure diagnosis, launch/resume and optional-pack tasks. Compilation is not proof of scientific equivalence.

The 11-skill target remains a design choice, not a demonstrated performance optimum. Distribution, bounded behavioral smoke tests and synthetic execution checks are recorded in the verification report; private upstream packages, production Platform operations and other hosts are not covered. PR #1 was left unchanged and subsequently merged; this follow-up targets the resulting main branch.
