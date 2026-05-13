import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from eval_bench.cli import main


class EvalBenchCliTests(unittest.TestCase):
    def run_cli(self, args):
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_init_creates_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr = self.run_cli(["init", "--root", tmp])

            self.assertEqual(code, 0, stderr)
            self.assertIn("Eval cases initialized", stdout)
            self.assertTrue((Path(tmp) / "evals" / "eval_cases.json").exists())

    def test_run_missing_cases_returns_error(self):
        code, stdout, stderr = self.run_cli(["run", "--cases", "missing.json"])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("cases file not found", stderr)

    def test_run_default_cases_path_respects_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            self.run_cli(["init", "--root", str(root)])

            code, stdout, stderr = self.run_cli(["run", "--root", str(root)])

            self.assertEqual(code, 0, stderr)
            self.assertIn("Failed: 0", stdout)
            self.assertTrue((root / "u27" / "eval_results.json").exists())

    def test_run_returns_nonzero_when_eval_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases = Path(tmp) / "evals" / "eval_cases.json"
            cases.parent.mkdir()
            cases.write_text(
                json.dumps(
                    [
                        {
                            "id": "bad",
                            "claim": "Failure is visible.",
                            "command": "python3 -c \"raise SystemExit(3)\"",
                            "expected_exit": 0,
                        }
                    ]
                ),
                encoding="utf-8",
            )

            code, stdout, stderr = self.run_cli(["run", "--root", tmp, "--cases", str(cases)])

            self.assertEqual(code, 1, stderr)
            self.assertIn("Failed: 1", stdout)

    def test_demo_and_inspect(self):
        with tempfile.TemporaryDirectory() as tmp:
            demo_root = Path(tmp) / "demo"
            demo_code, demo_stdout, demo_stderr = self.run_cli(["demo", "--root", str(demo_root)])
            inspect_code, inspect_stdout, inspect_stderr = self.run_cli(
                ["inspect", str(demo_root / "u27" / "eval_results.json")]
            )

            self.assertEqual(demo_code, 0, demo_stderr)
            self.assertIn("Demo eval report written", demo_stdout)
            self.assertEqual(inspect_code, 0, inspect_stderr)
            self.assertIn("System Class: U27-S05", inspect_stdout)
            self.assertIn("Failed: 0", inspect_stdout)


if __name__ == "__main__":
    unittest.main()
