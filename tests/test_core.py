import json
import tempfile
import unittest
from pathlib import Path

from eval_bench.core import create_demo, init_cases, load_cases, run_cases


class EvalBenchCoreTests(unittest.TestCase):
    def test_init_cases_writes_default_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = init_cases(tmp)
            cases = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(cases[0]["id"], "cli-smoke-test")
        self.assertEqual(cases[0]["expected_exit"], 0)

    def test_load_cases_requires_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evals" / "eval_cases.json"
            path.parent.mkdir()
            path.write_text(json.dumps({"id": "bad"}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON list"):
                load_cases(path)

    def test_run_cases_records_pass_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases_path = Path(tmp) / "evals" / "eval_cases.json"
            cases_path.parent.mkdir()
            cases_path.write_text(
                json.dumps(
                    [
                        {
                            "id": "passes",
                            "claim": "A passing command is recorded.",
                            "command": "python3 -c \"print('ok')\"",
                            "expected_exit": 0,
                        },
                        {
                            "id": "fails",
                            "claim": "A failing command is recorded.",
                            "command": "python3 -c \"raise SystemExit(2)\"",
                            "expected_exit": 0,
                        },
                    ]
                ),
                encoding="utf-8",
            )

            report = run_cases(tmp, cases_path)

            self.assertEqual(report["summary"], {"total": 2, "passed": 1, "failed": 1})
            self.assertTrue((Path(tmp) / "u27" / "eval_evidence" / "passes.txt").exists())
            self.assertTrue((Path(tmp) / "u27" / "EVAL_REPORT.md").exists())
            proof_cases = json.loads((Path(tmp) / "evals" / "proof_cases.json").read_text(encoding="utf-8"))
            self.assertEqual(proof_cases[0]["id"], "eval-passes")

    def test_create_demo_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = create_demo(tmp)
            report = paths["report"].read_text(encoding="utf-8")

        self.assertIn("# Eval Report", report)
        self.assertIn("cli-smoke-test", report)


if __name__ == "__main__":
    unittest.main()
