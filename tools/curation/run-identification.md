# Identify the selected local run before debugging or resuming

Read history in the environment that owns the run, using the installed release's command help and user-selected workspace. `nextflow log` lists runs; `nextflow log <run-name>` retrieves selected task metadata. Record the run name/session ID, pipeline revision, command/parameters, status and work directory before choosing a resume target.

Confirm that the selected work directory and cache metadata are accessible. A newer run, matching filename or cache hit does not prove that it is the intended analysis. Inspect the selected task's .command files and outputs when diagnosing failures; distinguish cached reuse, submission and completed output verification.

Read-only inspection does not authorize cleanup, deletion, installation or rerunning a pipeline. Ask for approval before mutations; `nextflow clean` can destroy work required for resume.

Broad historical recaps and storage analysis belong to `nextflow-provenance:nextflow-history`; output-origin/LID exploration belongs to `nextflow-provenance:nf-data-lineage`. Use those skills only when the optional pack is enabled; ordinary debugging and resume selection do not require it.
