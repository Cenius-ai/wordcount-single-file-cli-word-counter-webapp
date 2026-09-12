#!/usr/bin/env bash
#
# Non-interactive demo of the wordcount CLI: the happy path, the whitespace and
# empty-file rules, the help surface, and every failure class with its exit
# code. Nothing here prompts for input, touches the network, or keeps running.
set -uo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
SAMPLES="samples/sample.txt"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

printf 'notes on the tide\n' >"$WORK_DIR/notes.txt"
printf 'one two three four five six seven\n' >"$WORK_DIR/seven.txt"
: >"$WORK_DIR/empty.txt"
printf 'caf\xe9 latin-1 bytes\n' >"$WORK_DIR/latin1.txt"

# run: echo the command, execute it, then report the exit code without ever
# failing the demo script itself (non-zero exits are part of what we show).
run() {
    printf '\n$ %s\n' "$*"
    local status=0
    "$@" || status=$?
    printf '[exit %d]\n' "$status"
    return 0
}

echo "wordcount demo -- ${PYTHON} wordcount.py FILE"
echo "============================================="

echo
echo "-- 1. usage and help ----------------------------------------------"
run "$PYTHON" wordcount.py --help

echo
echo "-- 2. count a file --------------------------------------------------"
run "$PYTHON" wordcount.py "$SAMPLES"
run "$PYTHON" wordcount.py "$WORK_DIR/notes.txt"
run "$PYTHON" wordcount.py "$WORK_DIR/seven.txt"

echo
echo "-- 3. whitespace and empty-file rules -------------------------------"
run "$PYTHON" wordcount.py "$WORK_DIR/empty.txt"

echo
echo "-- 4. scriptable: stdout is the bare integer ------------------------"
count="$("$PYTHON" wordcount.py "$SAMPLES")"
printf 'count=$(wordcount %s)  ->  %s\n' "$SAMPLES" "$count"

echo
echo "-- 5. failure classes: one stderr line, distinct exit code ----------"
run "$PYTHON" wordcount.py "$WORK_DIR/missing.txt"
run "$PYTHON" wordcount.py "$(pwd)/samples"
run "$PYTHON" wordcount.py "$WORK_DIR/latin1.txt"
run "$PYTHON" wordcount.py
run "$PYTHON" wordcount.py --words "$SAMPLES"

echo
echo "-- 6. installed console script (present after install.sh) -----------"
if command -v wordcount >/dev/null 2>&1; then
    run wordcount "$SAMPLES"
else
    printf '\nwordcount is not on PATH yet; run: bash install.sh\n'
fi

printf '\nDemo complete.\n'
