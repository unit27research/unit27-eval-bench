# U27-S05 // Eval Bench

[![CI](https://github.com/unit27research/unit27-eval-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/unit27research/unit27-eval-bench/actions/workflows/ci.yml)

Eval Bench runs deterministic eval cases before proof recording.

```text
U27-S05
EVAL BENCH

CLASS: SYSTEM
FUNCTION: Eval Case Execution + Result Artifact Generation
REF_ID: EVAL-BENCH-01
```

## Release Status

`SOURCE_STATUS: PUBLIC_PACKAGE`
`ACCESS_STATUS: CLEARED_FOR_EXTERNAL_USE`

This repository is a released Unit27 field kit: visible, inspectable, and intended for orientation, testing, and practical use. Controlled protocol materials remain outside this source package.

It answers one narrow question:

> Did the declared eval cases run, and what did they record?

## Why Use It

Use Eval Bench after a handoff packet defines what should be checked and before Proof Ledger records durable proof.

It is useful when a repo needs deterministic eval results instead of a vague statement that something was tested.

Example:

```text
Problem: The handoff names acceptance checks, but there is no eval result artifact.
Result: Eval Bench runs the declared cases and writes a report Proof Ledger can record.
```

## 60-Second Start

The current public release is GitHub-first. Run it from a local checkout:

```bash
git clone https://github.com/unit27research/unit27-eval-bench
cd unit27-eval-bench
pip install -e .
eval-bench demo
cat eval-bench-demo/u27/EVAL_REPORT.md
```

On your own repo:

```bash
eval-bench init
eval-bench run
eval-bench inspect u27/eval_results.json
```

## What It Does

Eval Bench writes:

1. `evals/eval_cases.json`
2. `u27/eval_results.json`
3. `u27/EVAL_REPORT.md`
4. `u27/eval_evidence/*.txt`
5. `evals/proof_cases.json`

It is designed to feel like a deterministic eval runner, not a benchmark platform or proof ledger.

## System Position

```text
Stack Engine -> Context Engine -> Handoff Engine -> Eval Bench -> Proof Ledger -> Boundary Engine -> u27-check
```

Eval Bench sits after handoff generation and before proof recording. It runs declared eval cases and produces result artifacts. Proof Ledger remains responsible for durable proof records.

## CLI

```bash
eval-bench init
eval-bench run
eval-bench inspect u27/eval_results.json
eval-bench demo
```

Exit codes:

```text
0 = success
1 = one or more eval cases failed
2 = input or inspection error
```

## Case Shape

```json
{
  "id": "cli-smoke-test",
  "claim": "The primary CLI command returns usable output.",
  "command": "python3 -c \"print('eval bench smoke ok')\"",
  "expected_exit": 0,
  "limits": ["This eval confirms command execution, not full product correctness."]
}
```

## Reliability

Eval Bench is released as part of the Unit27 public tooling channel. CI is configured to verify the unit test suite and wheel contents before changes are considered ready.

## What It Does Not Do

Eval Bench does not:

1. Decide which project should be built
2. Generate agent handoff packets
3. Record durable proof
4. Check public claims
5. Perform launch QA
6. Replace Proof Ledger, Boundary Engine, or `u27-check`

## Verify

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
eval-bench demo
eval-bench inspect eval-bench-demo/u27/eval_results.json
```

## Acceptance

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m eval_bench.cli demo --root examples/sample-project
PYTHONPATH=src python3 -m eval_bench.cli inspect examples/sample-project/u27/eval_results.json
python3 -m pip wheel . --no-deps --no-build-isolation -w /tmp/eval-bench-wheel
python3 scripts/verify_wheel.py /tmp/eval-bench-wheel/unit27_eval_bench-0.1.0-py3-none-any.whl
```

## License

MIT
