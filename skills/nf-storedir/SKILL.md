---
name: nf-storedir
description: >
  Diagnose and fix Nextflow storeDir issues. Use when asked to "fix storeDir",
  "debug caching", "storeDir not working", "files not caching", "mv cannot stat",
  "permission denied on storeDir", or any storeDir-related problems.
---
<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->

## Using this skill

Use the tools and runtimes available in the user's session. Establish the
pipeline, input data and execution environment from their request or current
context. Use user-selected locations for files and results. Consult companion
skills, bundled references and optional helpers by name when available.

For Seqera operations, use the `seqera-mcp` skill. Any `platform_*` examples
describe API operations. Discover their exact names and parameter schemas with
`search_seqera_api`, then invoke `call_seqera_api` using those schemas. The host
manages OAuth for the connected MCP server.


# Nextflow storeDir Troubleshooting

Diagnose storeDir using the user's process definition, configuration, task logs, and chosen cache location. Do not assume a cache directory or prescribe an output layout.

## How storeDir Works

Nextflow checks the declared outputs in the configured store location to decide whether the process can be skipped. After a successful run, it moves declared outputs there individually.

## Avoid Declaring a Directory and Its Children Together

Declaring both an output directory and files contained in it can make staging fail: moving the directory first removes the children from their original location. A typical signature is a file-not-found move error after the tool itself completed successfully.

Choose an output contract that fits the downstream workflow:

- Declare individual files when downstream tasks consume those files independently.
- Declare only the directory when downstream tasks require that directory as a unit.
- Do not declare both representations for the same artifacts.

## Use a Task-Specific Store Location

Derive task-specific cache identity from stable input and analysis identifiers supplied by the pipeline. Respect the user's configured storage location. Verify that distinct tasks cannot collide.

A generic process declaration can use an existing parameter:

~~~groovy
storeDir params.cache_location

output:
tuple val(meta), path('*.txt'), emit: results
tuple val(meta), path('versions.yml'), emit: versions
~~~

The output glob and versions.yml are illustrative output contracts. Adapt them to the actual tool. Write any completion sentinel only after the tool and required output checks succeed.

## Partial Entries

A killed run can leave an incomplete cache entry. A later move may fail when an existing nonempty directory cannot be replaced. Inspect the affected entry and compare it with the declared output contract before proposing removal or repair.

Limit cleanup to the incomplete entry identified from the user's configuration. Do not prescribe a fixed cleanup command or remove an entire cache.

## Permissions and Containers

Inspect ownership and permissions on the actual affected outputs. Container execution under a different user can leave artifacts the launching user cannot modify. Configure the container user according to the user's runtime and storage policy; do not assume one Docker user setting fits every environment.

## Glob Completeness

A glob can match only part of an expected result set. A partially populated store can therefore satisfy an overly broad output contract.

Use explicit required outputs or a completion sentinel that is written only after successful processing. Verify that the sentinel itself is a required output and cannot exist after an incomplete run.

## storeDir and Publishing

Review how storeDir interacts with the process's publication settings in the user's Nextflow version. Moving outputs into permanent storage changes where those outputs are available. Validate the intended downstream and publication behavior rather than adding redundant copy-back logic.

## Diagnostic Workflow

1. Identify the affected process and its declared outputs.
2. Check for overlapping directory and child-file declarations.
3. Verify task-specific cache identity and the configured storage location.
4. Inspect the real ownership, permissions, and partial entries.
5. Check whether the skip condition proves that all required outputs are complete.
6. Apply the smallest correction and rerun the user's representative test.

Report the observed cause, affected output contract, correction, and validation result.
