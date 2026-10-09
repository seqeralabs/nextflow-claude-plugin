---
name: nf-debug
description: >
  Debug Nextflow pipelines with lint, config validation, and preview compilation.
  Use when asked to "debug pipeline", "check my pipeline", "lint nextflow",
  "validate pipeline", "why won't my pipeline run", "pipeline diagnostics",
  or "check pipeline syntax".
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


# Nextflow Pipeline Debugger

Run three diagnostic passes, fix issues found, re-run until clean.

## Diagnostic Steps

### 1. Lint

```bash
nextflow lint <pipeline>
```

Catches syntax errors, deprecated patterns, undeclared variables.

### 2. Config Validation

```bash
nextflow config -show-profiles
```

Validates config files merge correctly. Look for unresolved params, profile conflicts, duplicate keys.

### 3. Preview (DAG compilation)

```bash
nextflow run <pipeline> -preview
```

Compiles the pipeline and generates the DAG without executing. Surfaces channel wiring errors, missing process inputs, and type mismatches.

## Workflow

1. Run all three commands, collect output.
2. Analyze errors — group by file and severity.
3. Fix issues directly in source files.
4. Re-run the failing diagnostic to confirm the fix.
5. Repeat until all three pass clean.

## Common Fixes

| Symptom | Likely cause |
|---------|-------------|
| `Missing process` | Typo in `include` or workflow block |
| `Channel has no origin` | Process output not connected |
| `Invalid config` | Unquoted string or missing closure brace |
| `Deprecated operator` | Replace with current DSL2 equivalent |

## Notes

- Assumes `nextflow` is on PATH.
- If the repo has a custom entry script (not `main.nf`), adjust paths in `nextflow run`.
- When additional context is provided (e.g. specific errors), focus diagnostics on those areas first.
