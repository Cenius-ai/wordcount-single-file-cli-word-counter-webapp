# Using wordcount

Every example below is copy-pasteable from the project root. `wordcount` is the
console script installed by `install.sh`; `python3 wordcount.py` is the identical
command with no install required — substitute freely.

## The surface in one table

| Invocation | stdout | stderr | Exit |
| --- | --- | --- | --- |
| `wordcount FILE` | the integer + newline | empty | `0` |
| `wordcount --help` / `-h` | usage block | empty | `0` |
| `wordcount --version` | `wordcount 1.0.0` | empty | `0` |
| `wordcount` (no FILE) | empty | usage line + `the following arguments are required: FILE` | `2` |
| `wordcount --words FILE` | empty | usage line + `unrecognized arguments: --words` | `2` |
| `wordcount a.txt b.txt` | empty | usage line + `unrecognized arguments: b.txt` | `2` |
| `wordcount missing.txt` | empty | `wordcount: missing.txt: no such file` | `1` |
| `wordcount ./samples` | empty | `wordcount: ./samples: is a directory` | `1` |
| `wordcount latin1.txt` | empty | `wordcount: latin1.txt: not valid UTF-8 text` | `1` |

## 1. Count the words in a file

```console
$ printf 'the quick brown fox\n' > that.txt
$ wordcount that.txt
4
```

One integer, one newline, nothing else — `4` is the entire stdout stream.

## 2. Use the count inside a script (or pipe)

Because stdout is only the number, capture and comparison are trivial:

```bash
words=$(wordcount chapter-01.txt)
echo "chapter 01: $words words"

if [ "$words" -gt 1000 ]; then
    echo "over the limit — split this chapter"
fi
```

`wordcount FILE | ...` works too, and diagnostics never contaminate the pipe:
they go to stderr, so `wordcount FILE > count.txt` still writes a clean file.

Branch on the exit code rather than on the text of the message:

```bash
if wordcount "$notes"; then
    echo "counted $notes"
else
    case $? in
        1) echo "could not read $notes" >&2 ;;
        2) echo "wordcount was called wrong" >&2 ;;
    esac
fi
```

Running the tool on many files is the shell's job — the interface is one
explicit path:

```bash
total=0
for f in drafts/*.txt; do
    n=$(wordcount "$f") || continue
    total=$((total + n))
    printf '%6d  %s\n' "$n" "$f"
done
echo "total: $total words"
```

## 3. What counts as a word

A word is a maximal run of non-whitespace characters. Spaces, tabs, newlines and
carriage returns all separate words, and any run of them counts as one
separator — words broken across lines are still single words.

| File content | Count | Why |
| --- | --- | --- |
| `the quick brown fox` | `4` | four runs |
| `a\tb\nc   ` | `3` | tab and newline are separators, trailing spaces are not words |
| `"  \n\t \n"` (whitespace only) | `0` | nothing but separators |
| *empty file* | `0` | an empty count is still a printed line, never a blank one |

The empty file matters for scripts: `0` is printed, so `[ "$words" -eq 0 ]`
works and `$(wordcount empty.txt)` never expands to nothing.

```console
$ : > empty.txt
$ wordcount empty.txt
0
```

## 4. Read the failure instead of a traceback

Every input problem is one line of plain English on stderr, followed by a
non-zero exit code. There is never a Python traceback.

```console
$ wordcount missing.txt
wordcount: missing.txt: no such file
$ echo $?
1

$ wordcount ./samples
wordcount: ./samples: is a directory
$ echo $?
1

$ printf 'caf\xe9\n' > latin1.txt        # 0xE9 alone is not valid UTF-8
$ wordcount latin1.txt
wordcount: latin1.txt: not valid UTF-8 text
$ echo $?
1
```

Reasons you may see, and what each means:

| Reason | Meaning |
| --- | --- |
| `no such file` | the path does not exist (a typo, or a relative path from the wrong directory) |
| `is a directory` | the path is a directory; wordcount counts files, not trees |
| `permission denied` | the file exists but you cannot open it |
| `not valid UTF-8 text` | the bytes are not UTF-8 (Latin-1, UTF-16 and binaries land here) |

To count a Latin-1 export, convert it first: `iconv -f latin1 -t utf-8 file > file.utf8`.

## 5. Help and version

```console
$ wordcount --help
usage: wordcount [-h] [--version] FILE

Count the whitespace-separated words in one text file.

positional arguments:
  FILE        path of the UTF-8 text file to count

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

exit codes:
  0  the count was printed to stdout
  1  the file could not be read (missing, a directory, not valid UTF-8)
  2  the command line was wrong

example:
  wordcount samples/sample.txt
```

`-h` prints the same block. `wordcount --version` prints `wordcount 1.0.0`.

## 6. Performance and limits

- **Single pass, constant memory.** The file is decoded and tokenized while it is
  streamed, so memory stays flat no matter how big the file is.
- **Measured on the shipped CPU:** a 98 MB file (20 million words, 2 225 long
  lines) counts in about 2 seconds; a short file is dominated by Python's own
  start-up (~30 ms).
- **The count is computed before anything is printed:** a file that turns out to
  be invalid UTF-8 halfway through produces the error line and *no* number.
- **Not supported, on purpose:** stdin (`-`), directory walking, multi-file
  aggregation, line/character/byte/unique-word counts, other encodings, and
  machine-readable output. The tool counts words in one file; a shell loop and
  `iconv` cover the rest.

## 7. Calling it as a library

`wordcount.py` is importable — useful for tests or for reusing the tokenizer:

```python
from wordcount import count_words, count_words_in_file, InputError

count_words("the quick brown fox")        # 4
try:
    count_words_in_file("notes.txt")
except InputError as error:
    print("could not count notes.txt:", error.reason)
```
