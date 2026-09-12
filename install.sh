#!/usr/bin/env bash
#
# Install wordcount's project-level dependencies and wire up the `wordcount`
# console script.
#
# Runs as an unprivileged user: no sudo, no system package manager, no service
# management, and it never starts anything long-running -- it installs and
# EXITS. Idempotent, so it is safe to re-run.
#
# wordcount has ZERO runtime dependencies, so the final step is the one that
# matters: it proves the shipped tool actually counts a file. Anything that only
# makes the tool more convenient (pip/setuptools upgrades, the editable install
# that puts `wordcount` on PATH, the test runner) is reported loudly and skipped
# rather than failing the whole install, because `python3 wordcount.py FILE`
# works without any of it.
set -uo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
WARNINGS=0

# Report a problem with an optional step without failing the install: the
# delivered tool is a single dependency-free file and is verified at the end.
warn() {
    echo "install.sh: WARNING: $*" >&2
    WARNINGS=$((WARNINGS + 1))
}

echo "==> Checking the interpreter ($PYTHON)"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "install.sh: '$PYTHON' not found on PATH (wordcount needs Python 3.9+)." >&2
    echo "install.sh: install Python 3.9+, or re-run as: PYTHON=/path/to/python3 bash install.sh" >&2
    exit 1
fi
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
    echo "install.sh: wordcount needs Python 3.9 or newer; found:" >&2
    "$PYTHON" --version >&2
    exit 1
fi
"$PYTHON" --version

echo "==> Upgrading pip/setuptools/wheel (optional)"
"$PYTHON" -m pip install --upgrade pip setuptools wheel \
    || warn "could not upgrade pip/setuptools/wheel; continuing (wordcount needs no build tooling)"

echo "==> Installing runtime dependencies (requirements.txt)"
"$PYTHON" -m pip install -r requirements.txt \
    || warn "pip install -r requirements.txt failed; wordcount has no runtime dependencies, so this is not fatal"

echo "==> Installing wordcount so the 'wordcount' console script is on PATH (optional)"
if ! "$PYTHON" -m pip install --no-build-isolation -e .; then
    echo "==> System site-packages is not writable; retrying with --user" >&2
    "$PYTHON" -m pip install --no-build-isolation --user -e . \
        || warn "editable install failed; run the tool as 'python3 wordcount.py FILE' (no install needed)"
fi

echo "==> Installing developer dependencies (requirements-dev.txt)"
"$PYTHON" -m pip install -r requirements-dev.txt \
    || warn "could not install pytest; the suite still runs with 'python3 -m unittest discover -s tests'"

echo "==> Self-check 1/2: importing the tool"
"$PYTHON" -c 'import wordcount; print("wordcount", wordcount.__version__, "imported OK")' || {
    echo "install.sh: FAILED: wordcount.py could not be imported." >&2
    exit 1
}

echo "==> Self-check 2/2: counting samples/sample.txt (must print 42)"
count="$("$PYTHON" wordcount.py samples/sample.txt)"
if [ "$count" != "42" ]; then
    echo "install.sh: FAILED: expected 42 words in samples/sample.txt, got '${count}'." >&2
    exit 1
fi
echo "$count"

echo
if [ "$WARNINGS" -ne 0 ]; then
    echo "Setup finished with $WARNINGS warning(s) -- see above. The tool itself is verified working:"
else
    echo "Setup complete. Nothing is running -- wordcount is a one-shot command."
fi
cat <<'EOF'
  Run the tool : python3 wordcount.py FILE      (or: wordcount FILE)
  See the demo : bash demo.sh
  Run the tests: python3 -m pytest
EOF
exit 0
