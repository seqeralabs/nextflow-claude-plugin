---
name: generate-pipeline-memory
description: >
  Build internal, private "memory" about a specific pipeline's run history
  and failure patterns at this organization. Produces
  private notes with specific run IDs, dates, stderr signatures, and known fixes. Output is private:
  it stays in a private notes directory excluded from version control and is NOT
  intended to be published. Use when the user asks to "build pipeline
  memory", "track run history", "capture error patterns", "initialize
  pipeline notes", or wants persistent internal context for debugging
  and pattern recognition across runs.
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


# Generate Private Pipeline Notes

Capture evidence about the user's pipeline runs, recurring failures, and known
fixes. Use a private location and document names selected by the user or already
established for their project. If file access is unavailable, describe the
limitation without claiming to write or save notes.

Publishable documentation and aggregate patterns belong in
`generate-pipeline-docs`. These notes are private.

## Privacy before writing

Verify that the selected notes location is private and excluded from version
control before writing. For a location within a Git repository, use the matching
ignore rule and verify that the notes are not tracked; an ignore rule does not
hide files that are already tracked. For a location outside the repository,
verify that it remains private and outside publication workflows.

Explain which location will hold the notes and why they must remain private.
Notes may include run IDs, workspace identifiers, reference sample tags, error
signatures, and input-location evidence from real runs. Never copy raw PHI,
patient identifiers, full customer-identifying data, API keys, access tokens,
or credentials into them. Redact secrets in log excerpts.

Never copy private note content into PRs, public documentation, external issues,
or exported transcripts.

## Procedure

1. Establish the user-selected pipeline, workspace, and history scope. Default
   to considering the last 30 runs when no count is specified.
2. Identify the user's existing private notes and read them before updating.
   Use the user's supplied local run history if it is relevant and available.
3. Verify the privacy and version-control exclusion of the selected location.
4. Discover workspace, workflow, and task operations with `search_seqera_api`.
   Call them only through `call_seqera_api` with discovered schemas.
5. Gather actual run names and IDs, status, exit status, timing, revision,
   internal user identifier, failure message, and relevant parameter changes.
6. For failed tasks, gather process, exit status, resource requests and usage,
   sample tag when appropriate, and a short redacted error excerpt. Prefer the
   first roughly 20 meaningful lines over full logs.
7. Cluster failure evidence and update the user's private notes. Preserve
   existing evidence and append new observations rather than replacing history.

## Run-history content

Record the analyzed run count, success rate, duration range, date range, and
revisions observed. Summarize individual runs by date, user identifier, status,
duration, revision, and brief evidence-based notes.

Track important changes across revisions or parameter choices. A changed value
is a clue, not proof of the causal fix. Distinguish observation from inference.

## Failure-pattern content

Group failures by process and meaningful error signature. The same process with
different stderr may represent different problems; the same exit code alone is
insufficient.

For each repeated pattern, record frequency, last observation, process, exit
status, relevant redacted error lines, affected runs, likely root cause,
confidence, and any demonstrated fix. Mark it Active, Intermittent, or Resolved
based on recent evidence. Do not fabricate a recurring pattern from one failure.

Resource-related fixes may include a consistent memory or heap increase and a
bounded retry policy. Input, reference, permissions, and configuration problems
require correction of the underlying issue rather than a blind retry.

## Updates and handoff

Read existing history and failure notes first. Append new runs, update pattern
counts and last-observed dates, and revise status as the evidence changes. Report
a short delta such as the number of new runs and patterns.

Tell the user what was created or updated in their chosen private location,
how its contents remain excluded from publication, the top supported findings,
and any evidence gaps. Do not claim automatic loading or updates in future chats.
