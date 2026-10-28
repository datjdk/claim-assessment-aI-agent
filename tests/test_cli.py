"""CLI output formats: text (default), md and json."""

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from claim_agent.cli import main


def run(*argv):
    """Run the CLI offline; tests never call OpenRouter."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        main([*argv, "--no-llm"])
    return out.getvalue()


class CliFormatTest(unittest.TestCase):
    def test_default_is_terminal_text(self):
        out = run("CLM-RFI-001")
        self.assertIn("Recommendation  Request more information", out)
        self.assertNotIn("| Requirement |", out)

    def test_md_flag_prints_markdown_report(self):
        for argv in (["--md"], ["--format", "md"]):
            with self.subTest(argv=argv):
                out = run("CLM-RFI-001", *argv)
                self.assertIn("# Claim Assessment Report — CLM-RFI-001", out)
                self.assertIn("## 6. Policy Citations", out)
                self.assertIn("### Tool call log", out)

    def test_json_flag_prints_report_and_audit(self):
        data = json.loads(run("CLM-APP-001", "--json"))
        self.assertEqual(data["report"]["recommendation"]["outcome"], "APPROVE")
        self.assertTrue(data["audit"]["events"])

    def test_md_and_json_flags_are_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            run("CLM-APP-001", "--md", "--json")

    def test_out_writes_markdown_and_json_files(self):
        with tempfile.TemporaryDirectory() as d:
            run("CLM-APP-001", "--out", d)
            self.assertTrue(Path(d, "CLM-APP-001.md").read_text().startswith("# Claim Assessment Report"))
            json.loads(Path(d, "CLM-APP-001.json").read_text())


class CliLlmDefaultTest(unittest.TestCase):
    def test_llm_is_required_by_default(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {}, clear=True):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as ctx:
                main(["CLM-APP-001", "--env-file", str(Path(d, "missing.env"))])
        self.assertIn("--no-llm", str(ctx.exception.code))

    def test_no_llm_skips_explanations(self):
        out = run("CLM-APP-001", "--md")
        self.assertIn("Explanations: Not requested", out)


if __name__ == "__main__":
    unittest.main()
