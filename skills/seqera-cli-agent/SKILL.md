---
name: seqera-cli-agent
description: Use the Seqera AI CLI as a subagent to answer questions about bioinformatics, Nextflow pipelines, Seqera Platform, and workflow management
triggers:
  - ask seqera
  - seqera agent
  - nextflow help
  - pipeline question
  - bioinformatics question
  - seqera platform help
metadata:
  service: seqera-cli
  audience: developers
  workflow: integration
  version: '1.0'
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


# Seqera AI CLI Subagent

Use the Seqera AI CLI in headless mode as a subagent to answer questions about:
- Nextflow pipelines and workflow development
- Seqera Platform configuration and usage
- Bioinformatics tools and best practices
- nf-core pipelines and community resources

## Usage

Requires an available shell tool and an installed, authenticated Seqera CLI.
If either is unavailable, report the missing prerequisite and see
CLI setup.

### Basic Query (Headless Mode)

Run the CLI with a query in headless mode to get a response without the TUI:

```bash
seqera --headless "your question here"
```

### Example Queries

**Nextflow questions:**
```bash
seqera --headless "How do I configure resource limits in a Nextflow process?"
```

**Seqera Platform questions:**
```bash
seqera --headless "How do I set up a compute environment in Seqera Platform?"
```

**Pipeline development:**
```bash
seqera --headless "What's the best practice for handling input files in Nextflow?"
```

**nf-core questions:**
```bash
seqera --headless "How do I run the nf-core/rnaseq pipeline?"
```

## Headless Mode Options

| Flag | Description |
|------|-------------|
| `--headless` | Run without TUI, output to stdout |
| `--show-thinking` | Include reasoning/thinking in output |
| `--show-tools` | Show tool calls made by the agent |
| `--show-tool-results` | Show results of tool calls |
| `-c, --continue` | Continue the most recent session |
| `-s, --session <id>` | Continue a specific session |

### Verbose Output

For debugging or seeing the full agent response:
```bash
seqera --headless --show-thinking --show-tools "your question"
```

### Continue a Conversation

To continue a previous session:
```bash
seqera --headless --continue "follow-up question"
```

## When to Use This Skill

Use this skill when:
1. You need domain expertise about Nextflow, pipelines, or bioinformatics
2. You want to query the Seqera Platform API through natural language
3. You need help with pipeline development or debugging
4. You want to leverage Seqera AI's specialized knowledge

## Integration Pattern

When using as a subagent:

```bash
# Ask a question and capture the response
response=$(seqera --headless "How do I configure Nextflow to use AWS Batch?")
echo "$response"
```

## Authentication

The CLI requires authentication. If not already authenticated:
```bash
seqera login
```

Or set the access token directly:
```bash
export SEQERA_ACCESS_TOKEN=your-token
```

## Organization Selection

To work with a specific organization:
```bash
# List available organizations
seqera org

# Select an organization
seqera org <org-name>
```
