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


# Nextflow 26 Syntax (v2 Parser)

Nextflow 26.04+ defaults to `NXF_SYNTAX_PARSER=v2`. The v2 parser is
stricter than every version before it and rejects code that older
Nextflow versions silently accept. This skill is the entry point for any
work on a Nextflow 26 workflow: what changes, what breaks, and how to
migrate.

Do not reconstruct version-to-version syntax from memory. The official
migration notes are the source of truth for breaking changes, feature
flags, and the current typed / record / output syntax:

- Hub (pick the page for the installed Nextflow version):
  https://docs.seqera.io/nextflow/migrations/
- Then load that page with the host's web tools restricted to official https://docs.seqera.io/nextflow/ documentation (the official migration guides)
  before writing the first example.
- Follow the linked tutorials for static types, record/operator migration,
  and workflow outputs, then read the typed-process and static-typing
  reference pages when those features are needed.

This skill only adds parser pitfalls and the operational order for a
large existing pipeline. Official notes win on syntax.

## How to Spot Strict Syntax Violations

### 1. Boolean parameters from CLI arrive as strings

With strict syntax, legacy CLI type detection is disabled. `--verbose true`
arrives as the string `"true"`, not a boolean. This causes validation errors
(`Value is [string] but should be [boolean]`) and subtle bugs where
`if (params.flag)` is always truthy.

**Fix:** Use the typed `params` block (Nextflow 25.10+) to declare types
explicitly. Nextflow auto-converts CLI values to the annotated type.

```nextflow
params {
    verbose: Boolean = false
    skip_trimming: Boolean = false
    input: Path
}

workflow {
    if (params.verbose) {  // now correctly evaluates as Boolean
        println "Verbose mode"
    }
}
```

Move boolean param declarations from `nextflow.config` to the script's
`params` block. Always provide `--flag true` or `--flag false` explicitly
on the command line (bare `--flag` no longer works).

**Do NOT work around this with string comparisons.** These patterns are
genuinely wrong — they break the moment the param actually arrives as a
real Boolean (e.g. after you adopt the typed block, or via a profile):

```nextflow
// ❌ Wrong — breaks on real Booleans
if (params.include_header == 'true') { ... }
if (params.include_header.toString().toLowerCase() != 'false') { ... }
```

These patterns *work* on a string-only input but are **redundant** once
the typed `params` block exists — remove them rather than keeping them
alongside it:

```nextflow
// ⚠ Redundant once the typed block is in place — delete, don't keep
if (params.include_header.toBoolean()) { ... }
if (params.include_header.toString().toBoolean()) { ... }
def flag = params.include_header as Boolean
```

```nextflow
// ✅ DO: declare the type once in the params block
params {
    include_header: Boolean = true
}

workflow {
    if (params.include_header) { ... }   // already a real Boolean
}
```

The typed `params` block is the right fix because Nextflow coerces the CLI
value once at parse time. Per-call-site coercion duplicates that work,
breaks when callers pass `--flag` without a value, and doesn't fix
validation errors raised by `nf-schema`.

### 2. Type annotations are opt-in — and use a different syntax

Strict syntax (v2 parser) does **not** by itself require type annotations.
Legacy qualifiers (`val x`, `path reads`, `tuple val(meta), path(reads)`)
still parse. Static types are a separate, opt-in feature enabled per script
with `nextflow.enable.types = true`, and typed processes use a different
input/output syntax — not `val x: Type`.

**Wrong (neither legacy nor typed — does not parse):**
```nextflow
input:
val sample_id: String
path reads: Path
```

**Legacy (valid under strict syntax, no types):**
```nextflow
process FOO {
    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*.bam"), emit: bam
```

**Typed (Nextflow 26.04+, `nextflow.enable.types = true` in the same file):**
```nextflow
nextflow.enable.types = true

process FOO {
    input:
    sample_id: String
    reads: Path

    output:
    bam: Path = file("*.bam")
```

Typed and legacy processes/workflows cannot be mixed in one script, but can
coexist across scripts — which is what makes an incremental, file-by-file
migration possible (see "Migrating a large pipeline" below). For the full
typed-process rules (`tuple(meta: Map, reads: Path)`, `topic:`, `stage:`,
no `.out`), load `nf-pipeline-design`.

### 3. Implicit `it` variable in closures

The v2 parser disallows the implicit `it` closure parameter.

```nextflow
// Bad
channel.map { it.trim() }

// Good
channel.map { item -> item.trim() }
```

### 4. Named output access without `emit:`

Accessing a process output by name requires the `emit:` label.

```nextflow
// Bad (v1 style)
process FOO {
    output:
    path "results.txt"
}
workflow { FOO.out.results }  // ← fails: no emit label

// Good
process FOO {
    output:
    path "results.txt", emit: results
}
workflow { FOO.out.results }  // ← works
```

### 5. DSL1 patterns

If the pipeline uses DSL1 syntax (no `workflow {}` block, direct process
chaining), it must be migrated to DSL2 before strict mode will work.

### 6. Top-level statements mixed with declarations

When a script contains declarations (`params { }`, `workflow { }`, `process X { }`,
`def f() { }`), the top level is **declaration-only**. Variable assignments
or other expression statements at the top level produce:

```
Error main.nf:N:1: Statements cannot be mixed with script declarations
```

**Allowed at top level:**
- `params { ... }` block
- `workflow { ... }` and `workflow NAME { ... }` blocks
- `process X { ... }` blocks
- `def f(args) { ... }` — **function** declarations
- `include { X } from '...'`
- feature flags such as `nextflow.enable.types = true` when the script defines typed processes/workflows

Do **not** add deprecated `nextflow.enable.dsl = 2` or `nextflow.enable.strict = true` to new 26.04+ examples.

**NOT allowed at top level (move inside `workflow { }` or a function):**
- `def HEADER = '...'` — variable assignment (it's a statement, not a declaration)
- Any free-floating expression like `println 'hello'`, channel chains, etc.

```nextflow
// ❌ Bad — `def HEADER = ...` is a statement at top level
params { include_header: Boolean = true }
def HEADER = 'sample_id\tvalue'
workflow { ... }

// ✅ Good — move the constant inside workflow, OR wrap it in a function
params { include_header: Boolean = true }
def header() { 'sample_id\tvalue' }                // function declaration: OK
workflow {
    def HEADER = 'sample_id\tvalue'                // statement inside workflow: OK
    ...
}
```

## Migrating a large pipeline (strict syntax → outputs → types → records)

Full modernization of a real pipeline (e.g. an nf-core pipeline with dozens
of modules) is not a one-shot edit. Reshaping channels touches every module
and subworkflow, and one wrong tuple position fails silently downstream.
Treat it as a staged migration where every stage ends green.

**Before editing anything:**

1. Record a baseline: run the existing test profile (`-profile test,docker`
   or the repo's equivalent) and the existing nf-test suite on the
   *unmodified* code. Save the output file list and checksums/snapshots.
   This baseline is the definition of "equivalent outputs" for every later
   stage. If the baseline itself fails, stop and report that first.
2. Confirm the installed Nextflow version (`nextflow -version`). Records,
   typed workflows, and some output-block features need 26.04+.
3. Open https://docs.seqera.io/nextflow/migrations/ and retrieve the
   notes for that version (and any versions being crossed) with
   the host's web tools restricted to official https://docs.seqera.io/nextflow/ documentation (the official migration guides). Follow those pages for
   syntax — workflow outputs, typed processes, records, feature flags —
   instead of inventing examples. Follow the linked tutorials for static
   types, records and operators, and workflow outputs. Look up the official
   guide again if a later stage needs a feature you have not checked yet.
4. Present the stage plan and the files each stage touches, then proceed.

**Stage order** (each stage is its own commit, each ends with lint + tests
matching the baseline):

1. **Strict syntax** — lint the selected pipeline sources to zero errors/warnings. No
   behavior change; outputs must be byte-identical to the baseline.
2. **Workflow outputs** — replace module/config `publishDir` with a
   workflow-level `publish:` section and top-level `output {}` block.
   Diff the published directory tree against the baseline — same files, same
   relative paths (or an explicitly documented new layout). In nf-core
   pipelines `publishDir` usually lives in the pipeline's publication configuration, not in the
   module files; migrate it from there.
3. **Typed params** — `params {}` block with types and defaults; keep
   `nextflow_schema.json` in sync.
4. **Static types** — enable `nextflow.enable.types` one script at a time,
   leaves first (local modules → subworkflows → workflows → `main.nf`).
   Shared nf-core component files are owned upstream: do not rewrite them
   in place (see `maintain-nf-core-pipeline`) — call them from typed code or
   vendor a project-owned copy with a note, and say which you chose.
5. **Tuples → records** — the riskiest stage. Migrate one channel family at
   a time (e.g. the reads channel end-to-end, then the BAM channel), not one
   file at a time. For each channel, write down the old tuple shape and the
   new record fields before editing, update every producer and consumer,
   and rerun tests before moving to the next channel. `join`/`groupTuple`/
   `combine` keyed on tuple positions are the usual breakage points.

After each stage, report: files changed, lint result, test result, and any
output difference from the baseline with its explanation. If a stage cannot
be finished in the session, stop at the last green stage and list what is
left rather than leaving a half-migrated channel.

## Fix Procedure

### Step 1: Find all Nextflow files

```bash
find . -name "*.nf" -o -name "*.nf.test" | sort
```

### Step 2: Check for violations

Let the language tooling find them rather than grepping:

```bash
nextflow lint <pipeline>
```

Fix errors first, then warnings. Only add type annotations when the task
asks for static typing (or the script already sets `nextflow.enable.types`).

### Step 3: Apply fixes in-place

Edit each file in place. Keep diffs per file small enough to review.

### Step 4: Select the v2 parser

Default in NF 26.04+. On 25.04 / 25.10 pre-26 environments, opt in with the environment variable when validating:

```bash
NXF_SYNTAX_PARSER=v2 nextflow run main.nf
```

Do not use `nextflow.enable.strict = true` as a parser switch — it is deprecated in 26.04 and never selected the v2 parser.

### Step 5: Verify

```bash
nextflow run <pipeline> -preview
# or
nextflow inspect <pipeline> 2>&1
```

## Response Format

1. **Files scanned** — list every `.nf` file checked
2. **Violations found** — grouped by file and type of violation
3. **Fixed files** — show the diff or changed blocks for each file
4. **Verification** — suggest the command to confirm the fix works

## Related Skills

- [boolean parameter compatibility](../nf-v2-boolean-params/README.md) — read the boolean compatibility reference when the task also involves a flag that is not toggling; otherwise keep the syntax investigation scoped to the observed parser errors.
- `nf-pipeline-design` — typed process/workflow rules and the workflow `output {}` block in new code
- `maintain-nf-core-pipeline` — when the pipeline being migrated is an nf-core pipeline (template sync and module updates come first)
- `nf-test` / [nf-test failure repair](../nf-test/references/repair-nf-test/README.md) — regression tests between migration stages

## References

- [Nextflow migration notes](https://docs.seqera.io/nextflow/migrations/) — start here; follow the page for the installed version
- [Nextflow DSL2 syntax parser docs](https://www.nextflow.io/docs/latest/dsl2.html#syntax-parser)
- [NF 26.04 release notes](https://github.com/nextflow-io/nextflow/releases/tag/v26.04.0)
