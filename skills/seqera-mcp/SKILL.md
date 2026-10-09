---
name: seqera-mcp
description: >
  Seqera Platform tools via MCP (Model Context Protocol). Use for structured
  operations on workflows, pipelines, compute envs, datasets, and data links,
  including resuming a failed Platform run.
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


# Seqera MCP Skill

Access Seqera Platform, Wave, and SeqeraHub
through the MCP server. Connect to https://mcp.seqera.io/mcp using the host's OAuth sign-in.
The host manages credentials; never paste or package access tokens.

## When to Use

Load this skill for any Platform read or mutation: listing workspaces,
fetching workflow details, launching pipelines, creating credentials,
managing data links and claiming Wave containers. Use the connected MCP tools
for these operations so the host manages Platform authentication.

## What's Loaded

The production MCP server is configured in the plugin's mcp.json.
After connecting, inspect the tools actually exposed by the host. This skill
uses the following five tools; authenticated live discovery is authoritative.
If a required tool is unavailable, report the connection or capability gap:

**Seqera API (Platform / Wave / SeqeraHub):**
- `search_seqera_api(query, service_filter?, limit?)` — natural-language
  search; returns ranked `api_name`s with parameter schemas and
  `suggested_parameters`.
- `call_seqera_api(service, api_name, parameters)` — executes the
  chosen `api_name`. `service` is one of `platform`, `wave`,
  `seqerahub`.

**nf-core helpers:**
- `search_nfcore_module(query, limit?)`
- `describe_nfcore_module(module_name)` — returns module inputs, outputs, and metadata.
  Verify command examples against the current native module workflow before use
- `nfcore_suggest_analysis(library_strategy?, organism?)`

## Workflow: search → call

Always discover first, then call with the exact `api_name`:

```
search_seqera_api(query="list workflows in my workspace")
  → suggestion: {service: "platform",
                 api_name: "platform_list_workflows",
                 suggested_parameters: {workspaceId: 0, max: 50, ...}}

call_seqera_api(service="platform",
                api_name="platform_list_workflows",
                parameters={"workspaceId": 12345, "max": 10})
```

Use the exact `api_name` from search results — do not invent, translate,
or shorten it.

## Parameter Shape (Common Pitfall)

`parameters` must use the exact camelCase field names and nesting from the
selected API's full `parameters` schema. The `suggested_parameters` template
contains required fields only, so inspect the full schema before adding optional
fields. For example, pipeline launch changes belong under
`{"pipelineId": 999, "workspaceId": 12345, "launch": {"revision": "master"}}`;
do not flatten `revision` beside `pipelineId`.

Do not pass a raw HTTP method, endpoint, and body object. That shape will be rejected — the MCP server handles
HTTP construction internally.

## When Search Doesn't Find It

If `search_seqera_api` doesn't surface a relevant suggestion, broaden
the query (use the user's wording, not your guess at an endpoint
name). Only call `call_seqera_api` with an `api_name` you've seen in a
search result — fabricated names will fail.

## Resume a failed Platform run

When the user asks to resume an existing run, search for
`platform_resume_workflow` and call it with the original `workflowId`
and `workspaceId`. That tool looks up the Nextflow session UUID, copies
the saved launch, and names the new run `original_2`, `original_3`, and
so on — matching the Platform UI.

Do not pass a Platform workflow ID as `sessionId`. Do not omit `runName`
on `platform_launch_workflow` and let Platform invent `adjective_noun`
names. Prefer `platform_resume_workflow` over `resume: true` on the
generic launch tools.

## References

`tool-schemas.md` — worked parameter examples for common
`api_name`s. Load via the host's file-reading tool if you need a concrete shape
before calling `call_seqera_api`.
