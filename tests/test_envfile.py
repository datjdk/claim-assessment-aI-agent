"""Loading OPENROUTER_API_KEY and OPENROUTER_MODEL from a .env file."""

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from claim_agent.cli import main
from claim_agent.envfile import load_env_file, parse_env_file
from claim_agent.llm import LLMConfig


def env_file(text):
    d = tempfile.mkdtemp()
    path = Path(d, ".env")
    path.write_text(text)
    return path


class ParseEnvFileTest(unittest.TestCase):
    def test_parses_common_formats(self):
        path = env_file(
            "# comment\n\nOPENROUTER_API_KEY=sk-test-123\nexport OPENROUTER_MODEL='anthropic/claude-haiku-5.5'\n"
            'QUOTED="a value with spaces"\nINLINE=value # trailing comment\nNOT A PAIR\n'
        )
        self.assertEqual(parse_env_file(path), {
            "OPENROUTER_API_KEY": "sk-test-123",
            "OPENROUTER_MODEL": "anthropic/claude-haiku-5.5",
            "QUOTED": "a value with spaces",
            "INLINE": "value",
        })


class LoadEnvFileTest(unittest.TestCase):
    def test_sets_missing_variables_and_config_reads_them(self):
        environ = {}
        loaded = load_env_file(env_file("OPENROUTER_API_KEY=sk-from-file\nOPENROUTER_MODEL=openai/gpt-6-luna\n"), environ)
        self.assertEqual(set(loaded), {"OPENROUTER_API_KEY", "OPENROUTER_MODEL"})
        config = LLMConfig.from_env(environ)
        self.assertEqual((config.api_key, config.model), ("sk-from-file", "openai/gpt-6-luna"))

    def test_shell_environment_wins(self):
        environ = {"OPENROUTER_API_KEY": "sk-from-shell"}
        load_env_file(env_file("OPENROUTER_API_KEY=sk-from-file\n"), environ)
        self.assertEqual(environ["OPENROUTER_API_KEY"], "sk-from-shell")

    def test_empty_values_are_ignored(self):
        environ = {}
        load_env_file(env_file("OPENROUTER_API_KEY=\nOPENROUTER_MODEL=\n"), environ)
        self.assertEqual(environ, {})
        self.assertEqual(LLMConfig.from_env({"OPENROUTER_API_KEY": "k", **environ}).model, "openai/gpt-4o")

    def test_missing_file_is_fine(self):
        self.assertEqual(load_env_file(Path("/nonexistent/.env"), {}), {})

    def test_loaded_names_never_include_values(self):
        loaded = load_env_file(env_file("OPENROUTER_API_KEY=sk-secret-value\n"), {})
        self.assertNotIn("sk-secret-value", repr(loaded))


class CliKeyTest(unittest.TestCase):
    def test_llm_without_key_explains_where_to_put_it(self):
        empty = env_file("OPENROUTER_API_KEY=\n")
        with mock.patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as exit_:
                main(["CLM-APP-001", "--llm", "--env-file", str(empty)])
        self.assertIn("OPENROUTER_API_KEY is not set", str(exit_.exception))
        self.assertIn(".env", str(exit_.exception))


if __name__ == "__main__":
    unittest.main()
