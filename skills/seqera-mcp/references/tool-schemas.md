<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->
# MCP Tool Parameter Schemas

Worked examples of the parameter shapes `call_seqera_api` accepts. Always
discover the exact `api_name` and parameter schema via `search_seqera_api`
first; the names below are illustrative, not exhaustive.

## Shape Rule

`parameters` uses the exact camelCase field names and nesting from the selected
API's full `parameters` schema. The `suggested_parameters` template contains
required fields only and can omit optional nested objects such as `launch`.
It is NOT a raw HTTP payload — do not pass `{method, endpoint, body}`. The MCP
layer constructs the HTTP request server-side from the `api_name`.

`workspaceId` is the integer ID of the user's workspace. If you don't
have one yet, discover the appropriate workspace-listing operation with `search_seqera_api` before calling
anything else — the examples below use `12345` only as a placeholder.

## Platform — Workflows

### `platform_list_workflows`
```json
{
  "service": "platform",
  "api_name": "platform_list_workflows",
  "parameters": {
    "workspaceId": 12345,
    "max": 50,
    "offset": 0,
    "search": "rnaseq",
    "status": "SUCCEEDED"
  }
}
```

### `platform_get_workflow`
```json
{
  "service": "platform",
  "api_name": "platform_get_workflow",
  "parameters": {
    "workflowId": "abc123",
    "workspaceId": 12345
  }
}
```

### `platform_resume_workflow`
```json
{
  "service": "platform",
  "api_name": "platform_resume_workflow",
  "parameters": {
    "workflowId": "abc123",
    "workspaceId": 12345
  }
}
```

### `platform_launch_workflow`
```json
{
  "service": "platform",
  "api_name": "platform_launch_workflow",
  "parameters": {
    "workspaceId": 12345,
    "computeEnvId": "ce123",
    "pipeline": "nf-core/rnaseq",
    "revision": "3.12.0",
    "workDir": "<user-provided working location>",
    "paramsText": "{\"input\": \"<user-provided input>\", \"outdir\": \"<user-provided output location>\"}"
  }
}
```

## Platform — Pipelines & Compute Envs

### `platform_list_pipelines`
```json
{
  "service": "platform",
  "api_name": "platform_list_pipelines",
  "parameters": {"workspaceId": 12345, "max": 50}
}
```

### `platform_get_pipeline_launch`
```json
{
  "service": "platform",
  "api_name": "platform_get_pipeline_launch",
  "parameters": {"pipelineId": 999, "workspaceId": 12345}
}
```

### `platform_update_pipeline`

Changes a pipeline's Git revision (`launch.revision`) or any other launch setting,
in place. Send only the metadata and launch fields to change. The tool retrieves
the current pipeline and merges the changes server-side, preserving omitted
settings. Use `null` to clear a nullable field and an empty `labelIds` array to
remove every pipeline label.

Pass `versionId` to edit a specific pipeline version; omit it for the default.
The `launch` object is required for launch-configuration changes: do not place
`revision`, `workDir`, `computeEnvId`, or other launch fields beside `pipelineId`.

```json
{
  "service": "platform",
  "api_name": "platform_update_pipeline",
  "parameters": {
    "pipelineId": 999,
    "workspaceId": 12345,
    "launch": {
      "revision": "master"
    }
  }
}
```

### `platform_list_pipeline_versions`

Lists a Launchpad pipeline's Seqera pipeline versions — saved snapshots of its
launch configuration, each with a name, hash, and default flag. These are not Git
branches or tags. Omit `isPublished` to list every version; pass it only when
the user asks specifically for published or draft versions.

```json
{
  "service": "platform",
  "api_name": "platform_list_pipeline_versions",
  "parameters": {"pipelineId": 999, "workspaceId": 12345}
}
```

### `platform_manage_pipeline_version`

Renames a pipeline version or makes it the default, leaving its launch
configuration untouched. Promoting a version unsets the previous default. A
version cannot be renamed once workflow runs reference it. Retrieve the version
first and always send both its complete current `name` and `isDefault` flag,
changing only the requested value; Platform overwrites both when omitted.

```json
{
  "service": "platform",
  "api_name": "platform_manage_pipeline_version",
  "parameters": {
    "pipelineId": 999,
    "workspaceId": 12345,
    "versionId": "3xa1b2c3d4",
    "name": "rnaseq-3",
    "isDefault": true
  }
}
```

### `platform_list_compute_envs`
```json
{
  "service": "platform",
  "api_name": "platform_list_compute_envs",
  "parameters": {"workspaceId": 12345, "status": "AVAILABLE"}
}
```

### `platform_create_compute_env`

Seqera Compute (fully managed — no credentials needed):
```json
{
  "service": "platform",
  "api_name": "platform_create_compute_env",
  "parameters": {
    "workspaceId": 12345,
    "name": "seqera-compute-eu",
    "platform": "seqeracompute-platform",
    "config": {
      "region": "eu-west-1"
    }
  }
}
```

AWS Batch (manual mode — requires credentials):
```json
{
  "service": "platform",
  "api_name": "platform_create_compute_env",
  "parameters": {
    "workspaceId": 12345,
    "name": "aws-batch-prod",
    "platform": "aws-batch",
    "credentialsId": "cred123",
    "config": {
      "region": "us-east-1",
      "computeQueue": "arn:aws:batch:us-east-1:123456789:job-queue/nextflow",
      "headQueue": "arn:aws:batch:us-east-1:123456789:job-queue/nextflow-head",
      "workDir": "<user-provided working location>"
    }
  }
}
```

Set cliPath only when the compute environment requires an explicit AWS CLI
location. Use the actual configured executable rather than assuming a system
installation location.

## Platform — Credentials

### `platform_create_credentials`
```json
{
  "service": "platform",
  "api_name": "platform_create_credentials",
  "parameters": {
    "workspaceId": 12345,
    "name": "my-k8s-creds",
    "provider": "k8s",
    "keys": {
      "token": "<bearer_token>",
      "certificate": "<ca_cert_pem>"
    }
  }
}
```

`provider` is the credential type (`aws`, `k8s`, `github`,
`container-registry`, etc.). `keys` is provider-specific — use
`search_seqera_api` with a query like "create credentials k8s" to see
the exact key names for the provider you want.

## Wave — Containers

### `wave_claim_container`
```json
{
  "service": "wave",
  "api_name": "wave_claim_container",
  "parameters": {
    "condaPackages": ["bioconda::samtools=1.21"],
    "platform": "linux/amd64"
  }
}
```

## When You're Not Sure

Run `search_seqera_api(query="...")` and copy
the `api_name` from the result. Build `parameters` from the full schema;
use `suggested_parameters` only as a required-fields starting point because it
can omit optional nested objects. Do not guess parameter names — use the
schema's exact camelCase fields and nesting.
