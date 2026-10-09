---
name: convert-r-script
description: >
  Convert R scripts to Nextflow pipelines. Analyzes R code to identify logical
  steps, inputs, outputs, and dependencies, then generates modular Nextflow
  processes with proper channels, containers, and conda environments.
  Trigger: "convert R script", "R to Nextflow", "migrate R to Nextflow",
  "convert this R script to Nextflow".
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


# Convert R Script to Nextflow

Convert an R script into a well-structured Nextflow pipeline. Do NOT simply wrap
the script in a single process — decompose it into multiple processes connected
by channels.

## Workflow

### 0. Audit readiness

For anything beyond a self-contained script, run
`audit-conversion-readiness` first. `setwd()` plus relative reads,
`source()` of files outside the handover, and reference paths on a lab share are
the usual blockers, and they are cheaper to surface now than mid-conversion.

### 1. Analyze the R script

- Identify input files, parameters, and output files
- Map R library dependencies (`library()`, `require()`)
- Find logical boundaries: data loading → processing → analysis → output
- Note file I/O patterns (`read.csv`, `write.csv`, `saveRDS`, `ggsave`, etc.)

### 2. Plan the pipeline structure

- Each logical step becomes a Nextflow process
- Define channels connecting processes
- Identify which R libraries each process needs
- Determine parallelization opportunities (e.g., per-sample, per-chromosome)

### 3. Generate the Nextflow pipeline

For each process:

- Correct `input:`, `output:`, and `script:` blocks
- Use proper Nextflow DSL2 syntax
- Handle R library dependencies via container or conda directive
- Use `publishDir` for final outputs

### 4. Validate

After generating the pipeline:

1. Validate compilation using the user's selected pipeline and installed runtime
2. Fix any syntax errors
3. Run `nextflow lint` to check best practices

Run validation with an available Nextflow installation and host execution tools.
If either is unavailable, report validation as unverified and read
`install-nextflow` for installation guidance.

## Guidelines

### Process decomposition

Split at natural boundaries:

| R pattern | Nextflow process |
|-----------|-----------------|
| `read.csv()` / data loading | `LOAD_DATA` |
| `dplyr` / `tidyr` transforms | `PREPROCESS` |
| Statistical modeling (`lm`, `glm`, DESeq2) | `ANALYZE` |
| Plotting (`ggplot2`, `pheatmap`) | `PLOT_RESULTS` |
| `write.csv()` / saving results | Often part of the process that generates them |

### R script embedding

```nextflow
process EXAMPLE {
    conda 'r-base=4.3 r-tidyverse=2.0'
    // OR: container 'rocker/tidyverse:4.3'

    input:
    path input_csv

    output:
    path "result.csv"

    script:
    """
    Rscript - <<'RSCRIPT'
    library(tidyverse)

    data <- read_csv("${input_csv}")
    result <- data %>% filter(!is.na(value)) %>% mutate(norm = value / max(value))
    write_csv(result, "result.csv")
    RSCRIPT
    """
}
```

### Container / conda strategy

- Prefer `conda` directive for simple dependency lists
- Use `container` with rocker images for complex setups
- Bioconductor packages: use `bioconductor/bioconductor_docker` or conda `bioconda` channel
- Group related libraries in the same process to minimize environments

### Common R → Nextflow patterns

- `args <- commandArgs(trailingOnly=TRUE)` → use Nextflow `val` inputs or template variables
- `source("helpers.R")` → bundle as a `path` input or include in the container
- `for (sample in samples)` → Nextflow channel parallelism (`.splitCsv()`, `.map{}`)
- `if (!dir.exists(...)) dir.create(...)` → not needed; Nextflow manages work directories
- Hardcoded file paths → replace with Nextflow input channels

## References

- `nextflow-dsl2.md` — DSL2 process and workflow syntax reference
- `r-container-images.md` — Common R container images and conda environments
