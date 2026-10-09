# Eleven-skill core verification

Scope: follow-up to PR #1's 28-skill catalog (`cfa99eb`). Implementation: `1fac28b`, with the behavioral suite and execution harness committed separately. No release/tag, production change or authenticated Platform operation was performed.

## Packaging and discovery

- **17 CLI tests passed:** eight consolidation tests and nine pack-generation/boundary tests.
- **147 bundled file records verified:** hashes, original provenance, complete skill resources, per-pack provenance manifests and local links within installed plugin roots.
- Marketplace and all five plugin manifests pass strict Claude validation.
- Full importer replay from a synthetic generic package reproduces core, packs and provenance; repeated imports are identical. The fixture reverses public curation and supplies placeholders for excluded entrypoints, not a private upstream package.

Actual isolated installation results, using Claude Code **2.1.293**:

| Enabled plugins | Discovered skills | Registered MCP servers |
| --- | ---: | ---: |
| Core | 11 | 1 |
| Core + platform | 14 | 1 |
| Core + nf-core | 13 | 1 |
| Core + plugins | 12 | 1 |
| Core + provenance | 13 | 1 |
| Core + all four packs | 19 | 1 |
| Plugins pack alone | 1 | 0 |

Exact skill names, not just counts, were checked. No unrequested plugin was installed. These are connection-registration checks; they do not establish OAuth authentication or live API behavior. CI repeats the matrix with its pinned Claude version.

One pre-existing `requirements.txt` lacked an upstream provenance entry. It is retained with an explicit origin-gap note and a hash of the imported bytes; no canonical upstream identity was invented. Repackaged license files normalize only trailing newlines, retain their original source hash, and record a bundled override when needed.

## Behavioral smoke tests

Nine cases passed across **three runs each (27/27)** using Sonnet and Haiku graders:

1. Read-only conversion readiness: missing helper/data references and honest access uncertainty.
2. Native single-module advice without a wrapper or invented inputs.
3. Single-tool construction without mandatory alternative branches; baseline comparisons remain required.
4. Header/aggregation correctness rather than relying on successful execution.
5. Script placement/staging without forcing an image build.
6. Missing platform pack: explicit named installation help and a safe stop.
7. Pre-launch publication authority: a launch question does not authorize commit/push.
8. Small Snakemake conversion: runnable output and honest unexecuted verification handoff.
9. Installed optional plugin specialist: legacy registry migration assessment through its preserved playbook.

The first suite exposed missing-pack naming and pre-launch discovery gaps; core descriptions were corrected. A trivial conversion can be solved without invoking Skill, so its hard checks are produced artifacts, verification honesty and subsequent real execution. Other cases retain explicit skill-discovery checks.

Bash-enabled native evaluation was refused by Claude's SSH-store symlink security check. It was not bypassed or weakened. The successful suite grants Read/Glob/Grep/Skill/Write/Edit only, runs authored synthetic scaffolds, starts no real MCP servers, and keeps reports local.

## Real execution/output evidence

Three separately generated, inspected conversions were materialized from public Write-tool trace payloads; sealed eval directories were not unsealed. Each was executed in a fresh temporary project:

- Run the source Snakefile with Snakemake **9.19.0**.
- Compare source and converted outputs against independently specified values: inputs 3 and 5 produce 8 and 24.
- Execute a holdout input: 2 and 7 produce 3 and 48.
- Confirm helper staging and publication to the selected output directory.
- Resume the explicitly selected `fixture-holdout` run; task trace reports **CACHED**, and the output remains correct.

All three conversions passed. The executable's own version report identifies **Nextflow 26.04.4**, regardless of the Homebrew launcher's directory label. The harness records the actual runtime and uses `-C` with the fixture config to avoid unrelated user configuration. No user runtime installation or upgrade was performed.

The installed 26.06-edge launcher failed before executing the fixture because it tried to download unavailable `nf-seqera@1.0.0`. Disabling agent mode and isolating config did not fix that launcher's startup. Execution results therefore establish this synthetic contract on **26.04.4**, not execution compatibility with that edge runtime.

## Limits

- No general scientific-equivalence or optimal-catalog-size claim: this is one small deterministic conversion fixture plus bounded routing tests.
- No registry module was actually executed; its case checks release-aware native advice and scope boundaries.
- No production launch, cloud provisioning, credential change, template merge, registry publication or lineage-store mutation was attempted.
- MCP Skills-extension support, Portal host behavior and the private generic package remain outside this PR's verified scope.

## Reproduce

```bash
python3 -I tools/test_consolidate_skills.py
python3 -I tools/test_skill_packs.py
python3 -I tools/check_sources.py
python3 -I tools/verify_skill_packs.py --report /tmp/pack-installations.json
claude plugin eval . --trust-plugin --no-publish --ablation none \
  --runs 3 --allow-tools Write Edit --scaffold --keep-temp
```

After inspecting/materializing a conversion's synthetic workspace, select an installed executable and verify its reported release:

```bash
python3 -I tools/verify_conversion_fixture.py /path/to/inspected-fixture \
  --nextflow /path/to/installed-nextflow --report /tmp/conversion-proof.json
```

Model smoke tests consume the operator's Claude quota; they are not run by unauthenticated CI. Temporary execution projects are removed by the harness. Raw machine-local model traces, reports and account data are not included in this repository.
