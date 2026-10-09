# Optional Nextflow packs

Inspect the session's available skill inventory before invoking a specialist. If the namespaced skill is available, use it for the requested task. If not, explain which pack is needed and ask the user to explicitly install/enable it. Do not silently install plugins, invoke a missing skill or access paths outside the current plugin root.

| Requested task | Optional skill |
| --- | --- |
| Create compute environments or credentials | `nextflow-platform:ce-credentials-setup` |
| Create/update storage data links | `nextflow-platform:seqera-data-links` |
| Write declarative Platform provisioning YAML | `nextflow-platform:seqerakit` |
| Run omics analysis or acquire GEO/SRA datasets | `nextflow-nf-core:nextflow-development` |
| Template sync or upstream nf-core maintenance | `nextflow-nf-core:maintain-nf-core-pipeline` |
| Develop or migrate a Nextflow extension plugin | `nextflow-plugins:nf-plugin-development` |
| Broad run/cache history or storage analysis | `nextflow-provenance:nextflow-history` |
| Trace lineage-store output origins | `nextflow-provenance:nf-data-lineage` |

All packs share the enabled `nextflow` core plugin's hosted Seqera connection. They carry only discovery/safety guidance, not duplicate MCP servers or API schemas. Credential, infrastructure, publication and destructive changes need explicit authorization. Core debugging, run identification, ordinary launch/resume and basic nf-core-safe edits remain available without optional packs.
