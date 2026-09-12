# Installing wordcount

wordcount is a single Python file with **no third-party runtime dependencies**,
so installation is optional. This document covers the one-command setup (which
also puts the `wordcount` console script on your PATH) and the "just run it"
path.

## Prerequisites

| Need | Version | Notes |
| --- | --- | --- |
| Python | 3.9+ (3.11 recommended) | Must be on `PATH` as `python3` (or set `PYTHON=/path/to/python`). Standard library only — `argparse`, `errno`, `os`, `sys`. |
| bash | any POSIX-ish shell | Only to run `install.sh` / `demo.sh`. Running the tool itself needs no shell scripts. |
| pip | ships with Python | Package manager used for the (empty) runtime requirements and the dev test runner. |

Nothing else is needed: no compiler, no build tools, no system packages, no
database, no network access. The package manager is **pip** — this project ships
no lockfile other than the pinned developer requirement in
`requirements-dev.txt`, and `requirements.txt` declares no runtime dependencies
at all.

## Step 1 — install the project (optional, exits when done)

```bash
bash install.sh
```

What it does, in order:

1. **Required** — checks that `python3` exists and is 3.9+. Fails if not.
2. *Optional* — `python3 -m pip install --upgrade pip setuptools wheel`.
3. *Optional* — `python3 -m pip install -r requirements.txt` (a no-op: there are no runtime dependencies).
4. *Optional* — `python3 -m pip install --no-build-isolation -e .`, which puts the `wordcount` console script on your PATH (retries with `--user` when site-packages is not writable).
5. *Optional* — `python3 -m pip install -r requirements-dev.txt` (the test runner).
6. **Required** — self-checks: imports the module, then counts `samples/sample.txt`, which must print `42`.

An optional step that fails is reported loudly as a `WARNING` and skipped, because
wordcount is a single dependency-free file: `python3 wordcount.py FILE` works
with no installation at all. Only the two required steps can fail the script, so
an unrelated pip or registry problem never makes a working tool look broken.

It is idempotent and it **exits**. It never starts a server or any other
long-running process, and it needs no privileges (no `sudo`, no system package
manager). Exit code `0` means the delivered tool was proven to count a file.

## Step 2 — verify the install

```bash
python3 wordcount.py samples/sample.txt   # -> 42
wordcount samples/sample.txt              # -> 42  (console script, after step 1)
```

Expected: the integer on stdout, nothing on stderr, exit status 0.

## Step 3 — run it

```bash
python3 wordcount.py path/to/file.txt     # no install required at all
wordcount path/to/file.txt                # after step 1
```

Everything else — the exit codes, the error messages, scripting recipes — is in
[USAGE.md](USAGE.md).

## Step 4 — run the tests

```bash
python3 -m pytest
# or, without pytest:
python3 -m unittest discover -s tests
```

Both runners collect `tests/test_wordcount.py` (27 tests) and exit 0 when the
suite is green. The tests spawn the CLI as a subprocess, use temporary files
created inline, and need no network.

## Skipping the install entirely

From a fresh checkout:

```bash
python3 wordcount.py samples/sample.txt
```

That is the whole requirement. Copy `wordcount.py` anywhere and it still works —
it has no package-relative imports.

## Demo

```bash
bash demo.sh
```

Prints the full surface non-interactively (help, real counts, empty file, stdout
capture, each failure class with its exit code) and exits 0. No prompts, no
network, nothing left running.

## Uninstalling

```bash
python3 -m pip uninstall wordcount
```

Removing the editable install leaves the repository untouched; the tool still
runs as `python3 wordcount.py FILE`.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `python3: command not found` | Python is not on `PATH`. Install Python 3.9+ or run with the full interpreter path, and pass it to the scripts too: `PYTHON=/usr/bin/python3 bash install.sh`. |
| `install.sh: wordcount needs Python 3.9 or newer` | The interpreter found is too old. Point `PYTHON=` at a newer one. |
| `error: externally-managed-environment` from pip | Your distribution marks the system Python as managed. Use a virtual environment (`python3 -m venv .venv && . .venv/bin/activate`) or add `--user`, then re-run `bash install.sh`. Running the tool itself is unaffected — `python3 wordcount.py FILE` always works. |
| `wordcount: samples/sample.txt: no such file` | Run commands from the project root, or pass an absolute path. |
| `wordcount: <path>: not valid UTF-8 text` | The file is not UTF-8 (a Latin-1 or UTF-16 export, for example). Re-encode it: `iconv -f latin1 -t utf-8 file > file.utf8`. |
