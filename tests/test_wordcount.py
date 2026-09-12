"""Tests for the wordcount CLI.

Covers the happy path, whitespace and empty-file rules, the help surface, every
bad-command-line case and every I/O failure class.  Standard library only --
run it with either runner:

    python3 -m unittest discover -s tests
    python3 -m pytest tests

The CLI is driven in-process through ``wordcount.main(argv)`` under redirected
stdout/stderr, so the tests assert on the real streams and the real exit codes
(including argparse's ``SystemExit`` for --help/--version/usage errors) without
spawning a shell.
"""

from __future__ import annotations

import ast
import contextlib
import io
import sys
import tempfile
import unittest
from collections import namedtuple
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "samples" / "sample.txt"

sys.path.insert(0, str(REPO_ROOT))
import wordcount  # noqa: E402  (import after the path is set up on purpose)

Result = namedtuple("Result", "returncode stdout stderr")


def run_cli(*args: str) -> Result:
    """Run ``wordcount.main`` with ``args`` and capture streams + exit code."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            returncode = wordcount.main(list(args))
        except SystemExit as exit_signal:
            # argparse raises SystemExit for --help (0), --version (0) and
            # usage errors (2); mirror what the interpreter would exit with.
            returncode = exit_signal.code if isinstance(exit_signal.code, int) else 0
    return Result(returncode, stdout.getvalue(), stderr.getvalue())


class WordCountUnitTests(unittest.TestCase):
    """The tokenizer itself, without touching the filesystem."""

    def test_plain_sentence(self) -> None:
        self.assertEqual(wordcount.count_words("the quick brown fox"), 4)

    def test_any_run_of_whitespace_is_one_separator(self) -> None:
        self.assertEqual(wordcount.count_words("a\tb\nc   d"), 4)

    def test_leading_trailing_and_blank_lines_do_not_count(self) -> None:
        self.assertEqual(wordcount.count_words("\n\n  \t alpha beta \n\n"), 2)

    def test_empty_text_counts_zero(self) -> None:
        self.assertEqual(wordcount.count_words(""), 0)

    def test_exit_codes_are_the_documented_contract(self) -> None:
        self.assertEqual(wordcount.EXIT_OK, 0)
        self.assertEqual(wordcount.EXIT_IO_ERROR, 1)
        self.assertEqual(wordcount.EXIT_USAGE_ERROR, 2)


class CliWordCountTests(unittest.TestCase):
    """End-to-end runs against real files on disk."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmpdir = Path(self._tmp.name)

    def write(self, name: str, content: str) -> Path:
        path = self.tmpdir / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_counts_words_and_prints_only_the_integer(self) -> None:
        fixture = self.write("that.txt", "the quick brown fox")

        result = run_cli(str(fixture))

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "4\n")
        self.assertEqual(result.stderr, "")

    def test_words_are_counted_across_lines_and_tabs(self) -> None:
        fixture = self.write("mixed.txt", "a\tb\nc   \n\td\n")

        result = run_cli(str(fixture))

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "4\n")

    def test_empty_file_prints_zero(self) -> None:
        fixture = self.write("empty.txt", "")

        result = run_cli(str(fixture))

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "0\n")

    def test_whitespace_only_file_prints_zero(self) -> None:
        fixture = self.write("blank.txt", "  \n\t\n   \n")

        result = run_cli(str(fixture))

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "0\n")

    def test_single_word(self) -> None:
        fixture = self.write("one.txt", "solitude")

        result = run_cli(str(fixture))

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "1\n")

    def test_output_is_capturable_and_deterministic(self) -> None:
        fixture = self.write("stable.txt", "one two three four five")

        first = run_cli(str(fixture))
        second = run_cli(str(fixture))

        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, "5\n")
        self.assertEqual(first.stdout, second.stdout)


class HelpSurfaceTests(unittest.TestCase):
    """F2: the help/usage surface and its exit code."""

    def assert_names_file_and_example(self, stdout: str) -> None:
        self.assertIn("FILE", stdout)
        self.assertIn("samples/sample.txt", stdout)

    def test_long_help_exits_zero(self) -> None:
        result = run_cli("--help")

        self.assertEqual(result.returncode, 0)
        self.assert_names_file_and_example(result.stdout)
        self.assertEqual(result.stderr, "")

    def test_short_help_matches_long_help(self) -> None:
        short = run_cli("-h")
        long = run_cli("--help")

        self.assertEqual(short.returncode, 0)
        self.assertEqual(short.stdout, long.stdout)

    def test_help_documents_the_exit_codes(self) -> None:
        stdout = run_cli("--help").stdout

        self.assertIn("exit codes", stdout)
        for code in ("0", "1", "2"):
            self.assertIn(code, stdout)

    def test_version_prints_and_exits_zero(self) -> None:
        result = run_cli("--version")

        self.assertEqual(result.returncode, 0)
        self.assertIn(wordcount.__version__, result.stdout)


class UsageErrorTests(unittest.TestCase):
    """F2: every wrong command line prints usage to stderr and exits 2."""

    def assert_usage_error(self, result: Result) -> None:
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("usage: wordcount", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_no_file_argument(self) -> None:
        self.assert_usage_error(run_cli())

    def test_unknown_option(self) -> None:
        self.assert_usage_error(run_cli("--words", "samples/sample.txt"))

    def test_two_file_paths(self) -> None:
        self.assert_usage_error(run_cli("samples/sample.txt", "samples/sample.txt"))


class IoErrorTests(unittest.TestCase):
    """F3: one plain-English stderr line, no traceback, exit code 1."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmpdir = Path(self._tmp.name)

    def assert_io_error(self, result: Result, reason: str) -> None:
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1)
        self.assertTrue(result.stderr.endswith(reason + "\n"), result.stderr)

    def test_missing_file(self) -> None:
        result = run_cli("missing.txt")

        self.assertEqual(result.stderr.strip(), "wordcount: missing.txt: no such file")
        self.assert_io_error(result, "no such file")

    def test_directory_instead_of_file(self) -> None:
        result = run_cli(str(self.tmpdir))

        self.assert_io_error(result, "is a directory")
        self.assertIn(str(self.tmpdir), result.stderr)

    def test_bytes_that_are_not_utf8_text(self) -> None:
        fixture = self.tmpdir / "latin1.txt"
        fixture.write_bytes(b"caf\xe9 not utf-8\n")

        result = run_cli(str(fixture))

        self.assert_io_error(result, "not valid UTF-8 text")

    def test_io_failure_never_writes_to_stdout(self) -> None:
        result = run_cli(str(self.tmpdir / "absent.txt"))

        self.assertEqual(result.stdout, "")


class SampleFixtureTests(unittest.TestCase):
    """T6: the committed fixture and a repeatable acceptance run."""

    def test_sample_fixture_holds_forty_two_words(self) -> None:
        self.assertEqual(len(SAMPLE.read_text(encoding="utf-8").split()), 42)

    def test_sample_fixture_end_to_end(self) -> None:
        result = run_cli("samples/sample.txt")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "42\n")
        self.assertEqual(result.stderr, "")

    def test_repeated_runs_agree(self) -> None:
        outputs = {run_cli("samples/sample.txt").stdout for _ in range(3)}

        self.assertEqual(outputs, {"42\n"})


class ModuleSurfaceTests(unittest.TestCase):
    """The module stays importable and dependency-free for library callers."""

    def test_module_exposes_the_documented_entry_points(self) -> None:
        self.assertEqual(wordcount.PROG, "wordcount")
        self.assertTrue(callable(wordcount.main))
        self.assertTrue(callable(wordcount.count_words))
        self.assertTrue(callable(wordcount.count_words_in_file))

    def test_module_imports_standard_library_only(self) -> None:
        source = (REPO_ROOT / "wordcount.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported |= {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }

        allowed = {"__future__", "argparse", "errno", "sys", "typing"}
        self.assertEqual(imported - allowed, set())


if __name__ == "__main__":
    unittest.main()
