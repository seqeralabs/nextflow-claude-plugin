<!-- Modified for the Nextflow plugin: generic host tools and companion guidance. -->

## Using this skill

Use the tools and runtimes available in the user's session. Establish the
pipeline, input data and execution environment from their request or current
context. Use user-selected locations for files and results. Consult companion
skills, bundled references and optional helpers by name when available.

For Seqera operations, read the [MCP connection](../../../launch-workflow/references/seqera-mcp/README.md) connection reference. Any `platform_*` examples
describe API operations. Discover their exact names and parameter schemas with
`search_seqera_api`, then invoke `call_seqera_api` using those schemas. The host
manages OAuth for the connected MCP server.


# Run Nextflow Registry Modules

Use native Nextflow module commands without assuming an input location, output folder, or project layout. Check that the user's Nextflow release supports the module command family.

The bundled command baseline requires Nextflow 26.04 or later. Verify command
availability in the installed release before recommending execution.

## Discover and Inspect First

~~~bash
nextflow module search "quality control"
nextflow module view nf-core/fastqc
~~~

Registry identifiers such as nf-core/fastqc name public modules; they are not local filesystem locations.

Read the module's current input contract and run template. Ask for the user's actual input files, parameters, execution environment, and desired result location when they are not established.

## Run the Selected Module

Use nextflow module run with the selected registry identifier and arguments derived from its current template. Supply the user's input references and output choices only after verifying them in the execution environment.

Do not prescribe sample filenames, storage folders, or a wrapper workflow. Modules are fetched on demand when supported by the installed Nextflow release.

If inputs contain several files, follow the template's accepted representation and quoting rules. Resolve any wildcard or file selection from the user's supplied data before running.

## Container Provisioning

Use the module's declared container or dependencies and the user's available runtime. Wave and Conda can provision containers when supported and configured appropriately. A configuration may enable wave.enabled, wave.strategy, and the selected container engine, but do not assume Docker is installed or remote execution uses the local machine.

## Command Reference

| Command | Purpose |
|---|---|
| nextflow module search | Find modules by capability |
| nextflow module view | Inspect a module's inputs and invocation |
| nextflow module run | Execute the selected module with verified arguments |
| nextflow module list | List available modules |

Use current command help for exact arguments and release support.

## When a Run Fails

1. Inspect the actual error.
2. Reread the selected module's current template and input contract.
3. Compare supplied arguments, file availability, runtime, and parameters.
4. Correct the direct invocation and retry the smallest representative input.

Do not write a wrapper workflow merely to recover from missing or incorrect module arguments.

## Report the Result

Read stdout and summarize status, useful metrics, warnings, and errors. Inspect produced files when the module contract or user's task requires it, using the locations reported by the run.

Suggest a logical next analysis step based on the result. Distinguish an unexecuted recommendation from a completed module run.

## Public Reference

https://registry.nextflow.io
