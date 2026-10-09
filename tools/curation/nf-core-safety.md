# nf-core safety in the core plugin

When a project declares nf-core conventions, preserve its scaffolding, schema, samplesheet checks, software-version emissions and resource profiles. Match publication syntax to the project's supported Nextflow release and existing output contract; legacy examples do not mandate replacing workflow outputs with publishDir.

Inspect the repository's contribution rules and actual branches before editing. nf-core commonly develops on dev and releases from main/master; verify this repository rather than unconditionally switching branches. Opening or merging PRs requires the user's authorization.

Shared modules are upstream-owned: avoid silently modifying them in place. Prefer a documented local adapter or approved upstream change; preserve the shared module's input/output contract and dependency pins. Run the applicable installed nf-core lint checks and representative tests before claiming compliance.

Template synchronization, bulk module updates and upstream contributions are separate maintenance work. If explicitly requested, use `nextflow-nf-core:maintain-nf-core-pipeline` when that pack is enabled. Otherwise explain the missing pack and ask the user to install/enable it; do not silently install plugins or expand a conversion into maintenance.
