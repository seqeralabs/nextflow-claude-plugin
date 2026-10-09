---
name: nf-v2-boolean-params
description: >
  Handle boolean parameters correctly in Nextflow v2 strict syntax.
  Use when writing or migrating Nextflow workflows with Boolean params,
  debugging "Value is [string] but should be [boolean]", fixing truthy
  string flags, or when --flag true/false behaves differently under
  NXF_SYNTAX_PARSER=v2 / Nextflow 26+.
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


# Nextflow v2 Strict Syntax — Boolean Parameters

## The Problem

In Nextflow v2 strict syntax (`NXF_SYNTAX_PARSER=v2`, default from 26.04), legacy CLI type detection is **disabled**. Command-line values like `--verbose true` are no longer auto-cast to their expected types — they arrive as raw strings.

```
# With legacy parser (v1) — works
nextflow run main.nf --use_bar true   # params.use_bar → Boolean TRUE

# With strict syntax (v2) — BREAKS
nextflow run main.nf --use_bar true   # params.use_bar → String "true"
# ERROR: Value is [string] but should be [boolean]
```

This also means `--flag` without a value (which previously set the param to `true`) no longer works. And `if (params.flag)` is always truthy when the value is a non-empty string like `"false"`.

### Why it changed

The legacy CLI type detection was disabled intentionally to prevent it from interfering with the new typed `params` block. The old heuristic would guess types (e.g. casting a string to a number because it looks numeric), which conflicts with explicit type annotations.

See [nextflow-io/nextflow#6760](https://github.com/nextflow-io/nextflow/issues/6760) for the upstream issue.

## The Solution: Typed `params` Block

Nextflow 25.10+ introduces the `params` block with type annotations. When a parameter has a type annotation, CLI values are converted to the annotated type automatically.

```nextflow
params {
    verbose: Boolean = false
    iterations: Integer = 10
    input: Path
}

workflow {
    if (params.verbose) {
        println "Running with ${params.iterations} iterations on ${params.input}"
    }
    // ...
}
```

Now `--verbose true`, `--verbose false`, and `--iterations 5` all work correctly because Nextflow converts the CLI string to the declared type.

### Requirements

- Nextflow 25.10.0 or later
- Strict syntax enabled: `NXF_SYNTAX_PARSER=v2` (or Nextflow 26.04+ where it's default)

### Boolean default behavior

From Nextflow 26.04+, boolean parameters without a default value automatically default to `false`:

```nextflow
params {
    verbose: Boolean       // defaults to false (26.04+)
    debug: Boolean = false // explicit default (works on 25.10+)
}
```

For 25.10 compatibility, always provide an explicit default.

## Migration Checklist

When writing or reviewing Nextflow code that uses boolean parameters:

- [ ] Use the typed `params` block instead of legacy `params.foo = false` declarations
- [ ] Declare all boolean params with type `Boolean` and an explicit default
- [ ] Move param declarations from `nextflow.config` to the script's `params` block (for params used in the script)
- [ ] Params used only in config can stay in config, but test that CLI overrides cast correctly
- [ ] Remove any manual `as Boolean` casts — the typed block handles this
- [ ] Test with `NXF_SYNTAX_PARSER=v2` before merging

## Common Patterns

### Before (legacy — breaks with strict syntax)

```groovy
// nextflow.config
params.verbose = false
params.save_intermeds = false
params.input = null
```

```nextflow
// main.nf
if (params.verbose) {           // BUG: "false" is truthy as a string!
    println "Verbose mode on"
}
```

### After (correct — works with strict syntax)

```nextflow
// main.nf
params {
    verbose: Boolean = false
    save_intermeds: Boolean = false
    input: Path
}

workflow {
    if (params.verbose) {       // Correctly evaluates as Boolean
        println "Verbose mode on"
    }
    // ...
}
```

### Config-only params

Params used exclusively in config (not in the script) should remain in config. However, be aware that CLI boolean overrides for config-only params may not auto-cast with strict syntax. Test this behavior and consider moving them to the script's `params` block if issues arise.

```groovy
// nextflow.config — params only used by config logic
params.use_gpu = false

process {
    withName: 'ALIGN' {
        accelerator = params.use_gpu ? 1 : 0
    }
}
```

If `--use_gpu true` fails with strict syntax, move the declaration to the script:

```nextflow
// main.nf
params {
    use_gpu: Boolean = false
}
```

## Mistakes to Avoid

### String comparison instead of boolean check

```nextflow
// WRONG — fragile, breaks on "True", "TRUE", "1", etc.
if (params.verbose == "true") { ... }

// RIGHT — use typed params block, then check the boolean directly
if (params.verbose) { ... }
```

### Bare flag without value

```bash
# WRONG with strict syntax — no value means the param is set to empty string or ignored
nextflow run main.nf --verbose

# RIGHT — always provide an explicit value
nextflow run main.nf --verbose true
```

### Using `as Boolean` as a workaround

```nextflow
// AVOID — manual casting is fragile and redundant with typed params
if (params.verbose as Boolean) { ... }

// RIGHT — declare type in params block, Nextflow handles casting
params {
    verbose: Boolean = false
}
```

### Forgetting that non-empty strings are truthy in Groovy

```nextflow
// With legacy params, params.flag might be the String "false"
// In Groovy, ANY non-empty string is truthy:
if ("false") { println "This WILL print!" }

// The typed params block prevents this by ensuring params.flag is a real Boolean
```

## Interaction with nf-schema

If using the `nf-schema` plugin (`validateParameters()`), be aware:

- `nf-schema` validates param types against its JSON schema
- With strict syntax, untyped CLI values arrive as strings, causing validation failures
- The `params` block resolves this by converting types before nf-schema validates
- `Path`-type params may cause `StackOverflowError` with some nf-schema versions — check [nf-schema#195](https://github.com/nextflow-io/nf-schema/issues/195)

## Quick Reference

| Nextflow version | Strict syntax | `params` block | Boolean CLI behavior |
|---|---|---|---|
| < 25.04 | Not available | Not available | Legacy auto-cast (works) |
| 25.04 | Opt-in (`NXF_SYNTAX_PARSER=v2`) | Not available | Strings, no auto-cast |
| 25.10 | Opt-in (`NXF_SYNTAX_PARSER=v2`) | Available | Auto-cast via type annotation |
| 26.04+ | Default (opt-out with `v1`) | Available | Auto-cast via type annotation |

## Related Skills

- `nextflow-26-syntax` — broader v2 parser rules (type annotations on process I/O, implicit `it`, top-level statements vs declarations, emit labels). **Load together with this skill when the task touches multiple v2 grammar rules; load this one alone when the failure is specifically about a boolean CLI param.**
- [static diagnostics](../repair-workflow/references/nf-debug/README.md) — Pipeline diagnostics with lint, config validation, and preview
