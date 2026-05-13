"""Command-line interface for Unit27 Eval Bench."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from eval_bench.core import create_demo, init_cases, run_cases


def command_init(args: argparse.Namespace) -> int:
    path = init_cases(args.root)
    print(f"Eval cases initialized: {path}")
    return 0


def command_run(args: argparse.Namespace) -> int:
    cases_path = Path(args.cases) if args.cases else Path(args.root) / "evals" / "eval_cases.json"
    if not cases_path.exists():
        print(f"eval-bench: cases file not found: {cases_path}", file=sys.stderr)
        return 2
    try:
        report = run_cases(args.root, cases_path)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"eval-bench: {exc}", file=sys.stderr)
        return 2

    print("Eval run complete")
    print(f"Total: {report['summary']['total']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    return 1 if report["summary"]["failed"] else 0


def command_inspect(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"eval-bench: results file not found: {path}", file=sys.stderr)
        return 2
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"eval-bench: invalid results JSON: {path}: {exc}", file=sys.stderr)
        return 2

    print(f"System Class: {report.get('system_class', 'unknown')}")
    print(f"Total: {report.get('summary', {}).get('total', 'unknown')}")
    print(f"Passed: {report.get('summary', {}).get('passed', 'unknown')}")
    print(f"Failed: {report.get('summary', {}).get('failed', 'unknown')}")
    return 1 if report.get("summary", {}).get("failed", 0) else 0


def command_demo(args: argparse.Namespace) -> int:
    paths = create_demo(args.root)
    print(f"Demo eval report written: {paths['report']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eval-bench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create starter eval cases.")
    init_parser.add_argument("--root", default=".", help="Project root.")
    init_parser.set_defaults(func=command_init)

    run_parser = subparsers.add_parser("run", help="Run eval cases.")
    run_parser.add_argument("--root", default=".", help="Project root.")
    run_parser.add_argument("--cases", default=None, help="Eval cases JSON path.")
    run_parser.set_defaults(func=command_run)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect eval results.")
    inspect_parser.add_argument("path", nargs="?", default="u27/eval_results.json", help="Eval results JSON path.")
    inspect_parser.set_defaults(func=command_inspect)

    demo_parser = subparsers.add_parser("demo", help="Create a demo eval project.")
    demo_parser.add_argument("--root", default="eval-bench-demo", help="Demo root path.")
    demo_parser.set_defaults(func=command_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
