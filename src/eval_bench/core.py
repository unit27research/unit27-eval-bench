"""Core eval case runner for Unit27 Eval Bench."""

from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1"
SYSTEM_CLASS = "U27-S05"


@dataclass(frozen=True)
class EvalCase:
    id: str
    claim: str
    command: str
    expected_exit: int = 0
    limits: tuple[str, ...] = ("This eval covers the recorded command only.",)


def slugify(value: str) -> str:
    chars: list[str] = []
    previous_dash = False
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True
    return "".join(chars).strip("-") or "eval-case"


def default_cases() -> list[dict[str, Any]]:
    return [
        {
            "id": "cli-smoke-test",
            "claim": "The primary CLI command returns usable output.",
            "command": "python3 -c \"print('eval bench smoke ok')\"",
            "expected_exit": 0,
            "limits": ["This eval confirms command execution, not full product correctness."],
        }
    ]


def parse_case(raw: dict[str, Any]) -> EvalCase:
    case_id = slugify(str(raw.get("id", "")))
    claim = str(raw.get("claim", "")).strip()
    command = str(raw.get("command", "")).strip()
    expected_exit = int(raw.get("expected_exit", 0))
    limits_raw = raw.get("limits", ["This eval covers the recorded command only."])
    limits = tuple(str(item).strip() for item in limits_raw if str(item).strip())

    if not case_id:
        raise ValueError("Eval case id is required.")
    if not claim:
        raise ValueError(f"Eval case `{case_id}` is missing claim.")
    if not command:
        raise ValueError(f"Eval case `{case_id}` is missing command.")

    return EvalCase(
        id=case_id,
        claim=claim,
        command=command,
        expected_exit=expected_exit,
        limits=limits or ("This eval covers the recorded command only.",),
    )


def load_cases(path: str | Path) -> list[EvalCase]:
    cases_path = Path(path)
    raw = json.loads(cases_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Eval cases file must contain a JSON list.")
    return [parse_case(item) for item in raw]


def run_case(case: EvalCase, root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    evidence_path = root_path / "u27" / "eval_evidence" / f"{case.id}.txt"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        completed = subprocess.run(
            shlex.split(case.command),
            cwd=root_path,
            text=True,
            capture_output=True,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except FileNotFoundError as exc:
        exit_code = 127
        stdout = ""
        stderr = str(exc)

    status = "pass" if exit_code == case.expected_exit else "fail"
    evidence_path.write_text(
        "\n".join(
            [
                f"$ {case.command}",
                f"expected_exit: {case.expected_exit}",
                f"exit_code: {exit_code}",
                "",
                "## stdout",
                stdout,
                "## stderr",
                stderr,
            ]
        ),
        encoding="utf-8",
    )

    return {
        "id": case.id,
        "claim": case.claim,
        "command": case.command,
        "expected_exit": case.expected_exit,
        "exit_code": exit_code,
        "status": status,
        "started_at": started_at,
        "evidence": str(evidence_path.relative_to(root_path)),
        "limits": list(case.limits),
    }


def run_cases(root: str | Path, cases_path: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    cases = load_cases(cases_path)
    results = [run_case(case, root_path) for case in cases]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    report = {
        "schema_version": SCHEMA_VERSION,
        "system_class": SYSTEM_CLASS,
        "generated_at": generated_at,
        "cases_path": str(Path(cases_path)),
        "summary": {
            "total": len(results),
            "passed": sum(1 for result in results if result["status"] == "pass"),
            "failed": sum(1 for result in results if result["status"] == "fail"),
        },
        "results": results,
    }
    write_outputs(root_path, report)
    return report


def proof_cases_from_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    proof_cases: list[dict[str, Any]] = []
    for result in results:
        proof_cases.append(
            {
                "id": f"eval-{result['id']}",
                "claim": result["claim"],
                "expected": f"Eval Bench records `{result['id']}` as pass and stores evidence.",
                "limits": result["limits"],
            }
        )
    return proof_cases


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Eval Report",
        "",
        "`SOURCE_STATUS: PUBLIC_PACKAGE`",
        "`ACCESS_STATUS: CLEARED_FOR_EXTERNAL_USE`",
        "",
        f"Generated: {report['generated_at']}",
        f"System Class: {report['system_class']}",
        "",
        "## Summary",
        "",
        f"- Total: {report['summary']['total']}",
        f"- Passed: {report['summary']['passed']}",
        f"- Failed: {report['summary']['failed']}",
        "",
        "## Results",
        "",
    ]
    for result in report["results"]:
        lines.extend(
            [
                f"### {result['id']} // {result['status'].upper()}",
                "",
                f"- Claim: {result['claim']}",
                f"- Command: `{result['command']}`",
                f"- Expected exit: `{result['expected_exit']}`",
                f"- Actual exit: `{result['exit_code']}`",
                f"- Evidence: `{result['evidence']}`",
                "",
            ]
        )
    return "\n".join(lines)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(root: Path, report: dict[str, Any]) -> dict[str, Path]:
    results_path = root / "u27" / "eval_results.json"
    report_path = root / "u27" / "EVAL_REPORT.md"
    proof_cases_path = root / "evals" / "proof_cases.json"
    write_json(results_path, report)
    report_path.write_text(render_report(report), encoding="utf-8")
    write_json(proof_cases_path, proof_cases_from_results(report["results"]))
    return {
        "results": results_path,
        "report": report_path,
        "proof_cases": proof_cases_path,
    }


def init_cases(root: str | Path) -> Path:
    cases_path = Path(root) / "evals" / "eval_cases.json"
    write_json(cases_path, default_cases())
    return cases_path


def create_demo(root: str | Path) -> dict[str, Path]:
    root_path = Path(root)
    cases_path = init_cases(root_path)
    run_cases(root_path, cases_path)
    return {
        "results": root_path / "u27" / "eval_results.json",
        "report": root_path / "u27" / "EVAL_REPORT.md",
        "proof_cases": root_path / "evals" / "proof_cases.json",
    }
