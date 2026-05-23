# Eval Bench Design Notes

`U27-S05 // EVAL BENCH`

Eval Bench exists to run deterministic eval cases and write result artifacts before Proof Ledger records durable proof.

## System Role

```text
Stack Engine -> Context Engine -> Knowledge Readiness -> Handoff Engine -> Eval Bench -> Proof Ledger -> Boundary Engine -> u27-check
```

Handoff Engine states what should be checked. Eval Bench runs declared cases. Proof Ledger records evidence-bearing runs after the eval result exists.

## Boundary

Eval Bench does not design the project, package repo context, generate handoff packets, preserve proof, check public claims, or perform launch QA.

It owns eval execution and eval result artifacts only.

## Output Contract

```text
evals/eval_cases.json
u27/eval_results.json
u27/EVAL_REPORT.md
u27/eval_evidence/*.txt
evals/proof_cases.json
```

The eval result is inspectable, but not a proof ledger. Proof Ledger remains the durable evidence record.

## Failure Modes

1. Eval cases become vague acceptance statements instead of runnable commands.
2. The tool starts acting like a benchmark suite.
3. Failed evals are hidden instead of returning exit code `1`.
4. Proof cases imply broader evidence than the eval command actually recorded.
5. The README blurs Eval Bench with Proof Ledger.
