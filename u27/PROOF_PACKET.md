# Proof Packet

Project: unit27-eval-bench
Generated: 2026-05-13T00:49:28+00:00

## Verified Claims

- Eval Bench unit and CLI behavior pass in the current local checkout.
  - Case: `tests-pass`
  - Command: `/usr/bin/env PYTHONPATH=src python3 -m unittest discover -s tests`
  - Evidence: `u27/evidence/run-0001.txt`

- Eval Bench can create a complete first-use demo project.
  - Case: `first-use-demo`
  - Command: `/usr/bin/env PYTHONPATH=src python3 -m eval_bench.cli demo --root examples/sample-project`
  - Evidence: `u27/evidence/run-0002.txt`

- Eval Bench can inspect its generated eval results.
  - Case: `result-inspection`
  - Command: `/usr/bin/env PYTHONPATH=src python3 -m eval_bench.cli inspect examples/sample-project/u27/eval_results.json`
  - Evidence: `u27/evidence/run-0003.txt`

- Eval Bench can produce an installable Python wheel.
  - Case: `package-builds`
  - Command: `/Users/joshuabloodworth/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip wheel . --no-deps --no-build-isolation -w /tmp/eval-bench-wheel-modern`
  - Evidence: `u27/evidence/run-0004.txt`

- The built wheel contains the expected modules and console entry point.
  - Case: `wheel-contents`
  - Command: `python3 scripts/verify_wheel.py /tmp/eval-bench-wheel-modern/unit27_eval_bench-0.1.0-py3-none-any.whl`
  - Evidence: `u27/evidence/run-0005.txt`

- The public README stays inside the Eval Bench boundary.
  - Case: `boundary-readme-scan`
  - Command: `/usr/bin/env PYTHONPATH=../unit27-boundary-engine/src python3 -m boundary_engine.cli scan README.md --proof u27/proof_ledger.json`
  - Evidence: `u27/evidence/run-0007.txt`

## Open Failures

- No failing, blocked, or regression runs are recorded.

## Known Limits
- This claim covers the recorded local test command only.
- This claim covers the included starter demo path, not every possible user command.
- This claim covers inspection of Eval Bench's own JSON output.
- This claim covers local artifact creation, not PyPI distribution.
- This claim covers package contents, not runtime installation in every environment.
- This claim covers the README, not every future public surface.

## Case Inventory
- `boundary-readme-scan`: pass - The public README stays inside the Eval Bench boundary.
- `first-use-demo`: pass - Eval Bench can create a complete first-use demo project.
- `package-builds`: pass - Eval Bench can produce an installable Python wheel.
- `result-inspection`: pass - Eval Bench can inspect its generated eval results.
- `tests-pass`: pass - Eval Bench unit and CLI behavior pass in the current local checkout.
- `wheel-contents`: pass - The built wheel contains the expected modules and console entry point.
