<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->
# Seqera CLI Subagent Skill

A skill included in the Nextflow plugin that uses the Seqera AI CLI to answer questions about bioinformatics, Nextflow pipelines, and the Seqera Platform.

## What is this?

This skill delegates domain-specific questions to the Seqera AI CLI, which has specialized knowledge about:

- **Nextflow** - Pipeline development, DSL2 syntax, configuration
- **Seqera Platform** - Compute environments, pipelines, runs, datasets
- **Bioinformatics** - Tools, best practices, data formats
- **nf-core** - Community pipelines and standards

## CLI Setup

### Prerequisites

1. Install the Seqera AI CLI:
   ```bash
   # Download the latest release from GitHub
   # https://github.com/seqeralabs/portal/releases
   ```

2. Authenticate with Seqera Platform:
   ```bash
   seqera login
   ```

The skill is already bundled with the Nextflow plugin. Confirm that `seqera` is
available on the host's PATH before using it:

```bash
seqera --help
```

## Usage

Once the CLI is installed and authenticated, the host can invoke it through an
available shell tool. The skill is triggered by phrases like:

- "ask seqera about..."
- "nextflow help with..."
- "seqera platform question..."

### Example Queries

```bash
# Ask about Nextflow concepts
seqera --headless "How do I configure resource limits in a Nextflow process?"

# Query your Seqera Platform data
seqera --headless "What is my latest run and what tasks are associated with it?"

# Get help with pipelines
seqera --headless "How do I run the nf-core/rnaseq pipeline?"
```

### Headless Mode Options

| Flag | Description |
|------|-------------|
| `--headless` | Run without TUI, output to stdout |
| `--show-thinking` | Include reasoning in output |
| `--show-tools` | Show tool calls made by the agent |
| `--show-tool-results` | Show results of tool calls |
| `-c, --continue` | Continue the most recent session |
| `-s, --session <id>` | Continue a specific session |

## How It Works

When the host has shell access and `seqera` is installed, it invokes the CLI in
headless mode for questions that match this skill:

```bash
seqera --headless "your question"
```

The Seqera AI CLI then:
1. Connects to the Seqera Platform API
2. Uses AI to understand your question
3. Fetches relevant data from your workspaces
4. Returns a comprehensive answer

## Configuration

### Environment Variables

```bash
# Use a direct platform token (skip OAuth)
export SEQERA_ACCESS_TOKEN=your-token

# Custom backend URL (optional)
export SEQERA_AI_BACKEND_URL=https://your-backend.example.com
```

### Organization Selection

```bash
# List available organizations
seqera org

# Select an organization
seqera org <org-name>
```

## License

MIT
