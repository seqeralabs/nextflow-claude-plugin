<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->

## Using this skill

Use the tools and runtimes available in the user's session. Establish the
pipeline, input data and execution environment from their request or current
context. Use user-selected locations for files and results. Consult companion
skills, bundled references and optional helpers by name when available.

For Seqera operations, read the [MCP connection](../../../launch-workflow/references/seqera-mcp/README.md) connection reference. Any `platform_*` examples
describe API operations. Discover their exact names and parameter schemas with
`search_seqera_api`, then invoke `call_seqera_api` using those schemas. The host
manages OAuth for the connected MCP server.


# Nextflow 25.04 Migration

Full upstream changelog: [25.04 release notes](references/upstream-25-04.md). This reference applies to that target release; verify version-dependent commands against installed help.

## Quick Start — Scan for Issues

Run the comprehensive scanner on any pipeline directory:

If available, use the bundled `find_deprecated_patterns.py` helper to inspect
the user-provided source files with the host's execution tools: [deprecated-pattern scanner](scripts/find_deprecated_patterns.py).

Checks for: deprecated `shell` blocks, unnecessary `nextflow.preview.topic` flags,
workflow output v2 `>>` syntax, and `-with-weblog` usage.

For shell blocks only, use the [shell-block scanner](scripts/find_shell_blocks.py).

Both scripts exit 0 if clean, 1 if issues found.

## Migration Priority

Handle in order — breaking first, then deprecations, then opt-in features.

### 1. Breaking Changes (MUST fix)

**Java 17 required** — check: `java -version`

**HyperQueue 0.20+** — only if using HyperQueue executor.

### 2. Deprecations (SHOULD fix)

#### `shell` → `script` migration

The `shell` section is deprecated. Multi-line `shell` directives become errors in a future release.

**⚠️ This is NOT a simple find-and-replace.** The `shell` and `script` sections use different templating:

| Feature | `shell` block | `script` block |
|---|---|---|
| Variable syntax | `!{var}` | `${var}` |
| Bash `$` handling | Literal (safe) | Interpolated by Groovy |
| Triple-quote style | `'''..'''` | `"""..."""` |

**Migration steps for each shell block:**

1. Change `shell '''` to `script """`
2. Change `'''` (closing) to `"""`
3. Convert `!{var}` → `${var}`
4. **Escape every bash `$`** as `\$` — this is the dangerous part:
   - `awk '{print $1}'` → `awk '{print \$1}'`
   - `$HOME` → `\$HOME` (unless you want Groovy to interpolate it)
   - `$(cmd)` → `\$(cmd)`
5. Test the process

```groovy
// BEFORE (deprecated)
process ALIGN {
    shell '''
    bwa mem !{reference} !{reads} | samtools sort -@ !{task.cpus} > output.bam
    awk '{print $1, $4}' output.bam > summary.txt
    '''
}

// AFTER
process ALIGN {
    script """
    bwa mem ${reference} ${reads} | samtools sort -@ ${task.cpus} > output.bam
    awk '{print \$1, \$4}' output.bam > summary.txt
    """
}
```

#### `-with-weblog` deprecated

Switch to the [nf-weblog plugin](https://github.com/nextflow-io/nf-weblog).

### 3. Workflow Outputs v3 (if using publish)

Breaking changes from v2 → v3:

| v2 | v3 |
|---|---|
| `FOO.out >> 'name'` | `name = FOO.out` |
| `publish:` anywhere | `publish:` only in entry workflow |
| Outputs in subdirs by default | Outputs in base dir by default |
| `mapper` directive | Use `map` operator in workflow body |
| Closure returning closure w/ `path` | Outer closure uses `>>` for individual files |

```groovy
// BEFORE (v2)
workflow {
    main:
    FOO(ch)

    publish:
    FOO.out.results >> 'results'
}

// AFTER (v3)
workflow {
    main:
    FOO(ch)

    publish:
    results = FOO.out.results
}
```

### 4. Opt-in Features (adopt when ready)

**Strict syntax** — `NXF_SYNTAX_PARSER=v2`. Enforces language spec.

**Linting** — `nextflow lint` checks scripts + configs. Supports formatting.

**Topic channels** — Out of preview. Remove `nextflow.preview.topic = true` if present.

**Data lineage** — Provenance tracking:
```groovy
lineage.enabled = true
```
Explore with `nextflow lineage` CLI or `lid://` path prefix.

**Plugin version ranges** — Pin major.minor, float patch:
```groovy
plugins {
    id 'nf-amazon@~2.1'  // latest 2.1.x
}
```

**`env()` function** — Read environment variables in Nextflow scripts.

### 5. New Config Options

See [25.04 release notes](references/upstream-25-04.md) § Miscellaneous for the full list.
Relevant only if using specific cloud executors (AWS Batch, Azure Batch, Google Batch, Fusion).
