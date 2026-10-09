#!/usr/bin/env python3
"""Execute an inspected, model-produced synthetic conversion against golden vectors.

This is a local smoke check, not a general scientific-equivalence evaluation.
The workspace must contain the authored eval fixture plus its generated main.nf.
"""

import argparse
import csv
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

KNOWN_INPUT = "id\tvalue\na\t3\nb\t5\n"
KNOWN_OUTPUT = "id\tscore\na\t8\nb\t24\n"
HOLDOUT_INPUT = "id\tvalue\nc\t2\nd\t7\n"
HOLDOUT_OUTPUT = "id\tscore\nc\t3\nd\t48\n"


def verify_conversion_workspace(workspace: Path, nextflow: str = "nextflow") -> dict:
    for command in ["snakemake", nextflow]:
        if not shutil.which(command):
            raise ValueError(f"missing fixture runtime: {command}; no installation was attempted")
    for filename in ["Snakefile", "transform.py", "main.nf", "nextflow.config"]:
        if not (workspace / filename).is_file():
            raise ValueError(f"missing conversion fixture: {filename}")
    with tempfile.TemporaryDirectory(prefix="nextflow-conversion-proof-") as tmp:
        root = Path(tmp)
        project = root / "project"
        shutil.copytree(workspace, project)
        home = root / "home"
        home.mkdir()
        env = {**os.environ, "HOME": str(home), "NXF_HOME": str(root / "nxf-home"), "NXF_ANSI_LOG": "false", "NXF_AGENT_MODE": "false"}
        commands = []

        def run(*args):
            result = subprocess.run(args, cwd=project, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
            commands.append({"command": list(args), "exit_code": result.returncode, "output": result.stdout})
            if result.returncode:
                raise ValueError(f"fixture command failed: {' '.join(args)}\n{result.stdout}")
            return result.stdout

        (project / "input.tsv").write_text(KNOWN_INPUT)
        (project / "baseline.tsv").unlink(missing_ok=True)
        run("snakemake", "--cores", "1", "baseline.tsv")
        if (project / "baseline.tsv").read_text() != KNOWN_OUTPUT:
            raise ValueError("source workflow disagrees with independent known-output oracle")
        for label, inputs, expected in [("known", KNOWN_INPUT, KNOWN_OUTPUT), ("holdout", HOLDOUT_INPUT, HOLDOUT_OUTPUT)]:
            (project / "input.tsv").write_text(inputs)
            outdir = project / f"outputs-{label}"
            run(nextflow, "-C", "nextflow.config", "run", "main.nf", "-name", f"fixture-{label}", "--input", "input.tsv", "--outdir", str(outdir), "-work-dir", str(project / "work"), "-with-trace", f"trace-{label}.tsv")
            actual = outdir / "result.tsv"
            if not actual.is_file() or actual.read_text() != expected:
                raise ValueError(f"converted workflow disagrees with independent {label} oracle")
        run(nextflow, "-C", "nextflow.config", "run", "main.nf", "-name", "fixture-resume", "--input", "input.tsv", "--outdir", str(project / "outputs-holdout"), "-work-dir", str(project / "work"), "-resume", "fixture-holdout", "-with-trace", "trace-resume.tsv")
        with (project / "trace-resume.tsv").open() as trace:
            tasks = list(csv.DictReader(trace, delimiter="\t"))
        if not tasks or any(task["status"] != "CACHED" for task in tasks):
            raise ValueError("selected run did not resume cached tasks")
        if (project / "outputs-holdout/result.tsv").read_text() != HOLDOUT_OUTPUT:
            raise ValueError("resume changed the verified output")
        version = run(nextflow, "-version").strip()
        return {"status": "pass", "nextflow_version": version, "workspace": str(workspace), "known_output": KNOWN_OUTPUT, "holdout_output": HOLDOUT_OUTPUT, "resume_statuses": [task["status"] for task in tasks], "commands": commands}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="inspected native-eval workspace")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--nextflow", default="nextflow", help="explicitly selected installed runtime; no installation or upgrade")
    args = parser.parse_args()
    report = verify_conversion_workspace(args.workspace.resolve(), args.nextflow)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS source execution, known/holdout output comparisons and named cached resume")


if __name__ == "__main__":
    main()
