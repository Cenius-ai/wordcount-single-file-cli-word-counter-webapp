#!/usr/bin/env python3
"""Count the whitespace-separated words in one text file.

``wordcount`` takes exactly one FILE path, splits the file's decoded text on
runs of whitespace (spaces, tabs and newlines alike) and prints the resulting
integer to stdout -- that integer plus a trailing newline is the *only* thing
stdout ever carries, so ``count=$(wordcount notes.txt)`` and pipes work.

Diagnostics are written to stderr as a single line of plain English, never a
traceback.  The exit code is a stable contract for scripts:

=====  ==========================================
code   meaning
=====  ==========================================
0      the count was printed
1      the file could not be read (I/O failure)
2      the command line itself was wrong
=====  ==========================================

The module is standard-library only and runs offline, unaided, on Python 3.9+.
"""

from __future__ import annotations

import argparse
import errno
import sys
from typing import IO, Optional, Sequence

__version__ = "1.0.0"

PROG = "wordcount"

#: The count was printed to stdout.
EXIT_OK = 0
#: The file could not be read: missing, a directory, undecodable, ...
EXIT_IO_ERROR = 1
#: The command line was wrong: no FILE, an unknown option, too many paths.
EXIT_USAGE_ERROR = 2

_HELP_EPILOG = """\
exit codes:
  0  the count was printed to stdout
  1  the file could not be read (missing, a directory, not valid UTF-8)
  2  the command line was wrong

example:
  wordcount samples/sample.txt
"""


class InputError(Exception):
    """A file could not be turned into text, with a human-readable reason.

    ``reason`` is a short lower-case phrase designed to slot straight into the
    one-line diagnostic ``wordcount: <path>: <reason>``.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def count_words(text: str) -> int:
    """Return the number of whitespace-separated words in ``text``.

    ``str.split()`` with no argument already collapses any run of whitespace
    (spaces, tabs, newlines) into one separator, which is exactly the word
    definition this tool promises.

    >>> count_words("the quick brown fox")
    4
    >>> count_words("a\\tb\\nc   ")
    3
    >>> count_words("   \\n\\t ")
    0
    """
    return len(text.split())


def describe_input_error(error: OSError) -> str:
    """Translate an :class:`OSError` into one short human phrase."""
    if isinstance(error, FileNotFoundError):
        return "no such file"
    if isinstance(error, IsADirectoryError) or error.errno == errno.EISDIR:
        return "is a directory"
    if isinstance(error, PermissionError):
        return "permission denied"
    return (error.strerror or "could not be read").lower()


def count_words_in_file(path: str) -> int:
    """Return the word count of the UTF-8 text file at ``path``.

    The file is streamed line by line -- one pass, constant memory -- so a
    100 MB text file costs no more than a 1 KB one.

    Raises:
        InputError: the file is missing, is a directory, is unreadable, or its
            bytes are not valid UTF-8 text.  ``InputError.reason`` holds the
            phrase for the stderr line.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return _count_open_file(handle)
    except UnicodeDecodeError:
        raise InputError("not valid UTF-8 text") from None
    except OSError as error:
        raise InputError(describe_input_error(error)) from error


def _count_open_file(handle: IO[str]) -> int:
    """Sum the word counts of every line of an already-open text file."""
    total = 0
    for line in handle:
        total += count_words(line)
    return total


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser that defines the invocation contract."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Count the whitespace-separated words in one text file.",
        epilog=_HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        help="path of the UTF-8 text file to count",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} {__version__}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the CLI and return its exit code.

    ``-h``/``--help`` and bad command lines are handled by argparse, which
    prints the help/usage block and exits 0 / 2 respectively before we get
    here.
    """
    args = build_parser().parse_args(argv)

    try:
        total = count_words_in_file(args.file)
    except InputError as error:
        print(f"{PROG}: {args.file}: {error.reason}", file=sys.stderr)
        return EXIT_IO_ERROR

    print(total)
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - the interpreter calls main() here
    sys.exit(main())
