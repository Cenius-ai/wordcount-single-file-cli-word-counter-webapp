# wordcount — single-file CLI word counter — complete Full-stack app command-line tool example app

A Full-stack app command-line tool, open-source and ready to self-host: that's **wordcount — single-file CLI word counter**. We will build wordcount, a plain-Python, single-file CLI that takes one file path, counts the whitespace-separated words in it and prints the integer to stdout, with a usage/help surface and a one-line, traceback-free…. wordcount — single-file CLI word counter ships complete — source, design assets, seed data — under the Apache-2.0 license; no cloud account needed. [Remix wordcount — single-file CLI word counter on cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp) for a custom build.


[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Stack](https://img.shields.io/badge/Stack-Full--stack%20app-3b82f6) [![Built with cenius.ai](https://img.shields.io/badge/Built%20with-cenius.ai-8b5cf6)](https://cenius.ai)

[![Open in cenius.ai](https://img.shields.io/badge/▶%20Open%20%26%20edit%20in-cenius.ai-8b5cf6?style=for-the-badge)](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp)

> **▶ [Open & edit in cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp)** — one click to an editable workspace: describe changes in plain English, get an instant preview, one-click deploy and host. Modifications made on the platform come with full rebrand & relicense rights.

_Local clone? See [Quick start](#quick-start) below. cenius.ai is the zero-setup path._

## Demo

![wordcount — single-file CLI word counter demo — command-line tool built with Full-stack app](.github/media/hero.gif)

📽 **[Demo video on cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp)** — the complete run-through · [MP4](.github/media/demo.mp4)

## Architecture

No external services required: the entire command-line tool runs from this Full-stack app repo (25 files). Top-level layout: `design/`, `samples/`, `tests/`. The setup script (`install.sh`) installs runtime dependencies and loads a starter dataset so the app is immediately usable. See [`INSTALL.md`](INSTALL.md) for complete setup instructions.

## Features

- Count the words in one file
- Command-line invocation contract
- Readable failure for bad input

## Quick start

```bash
./install.sh   # installs dependencies + seeds demo data
```

See [`INSTALL.md`](INSTALL.md) for full setup and usage instructions.

## Usage guide

Every example below is copy-pasteable from the project root. `wordcount` is the
console script installed by `install.sh`; `python3 wordcount.py` is the identical
command with no install required — substitute freely.

### The surface in one table

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

### 1. Count the words in a file

```console
$ printf 'the quick brown fox\n' > that.txt
$ wordcount that.txt
4
```

One integer, one newline, nothing else — `4` is the entire stdout stream.

### 2. Use the count inside a script (or pipe)

Because stdout is only the number, capture and comparison are trivial:

```bash
words=$(wordcount chapter-01.txt)
echo "chapter 01: $words words"

if [ "$words" -gt 1000 ]; then
    echo "over the limit — split this chapter"
fi
```

_Full guide: [`USAGE.md`](USAGE.md)_

## FAQ

### What's the quickest way to self-host wordcount — single-file CLI word counter?

Pull the repo, run `./install.sh`, and you are up — the script installs packages and pre-seeds the database. [`INSTALL.md`](INSTALL.md) covers any platform-specific tweaks.

### Is there a no-code way to modify wordcount — single-file CLI word counter?

Non-developers can use [cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp) to make changes. Describe your goal in everyday language and the platform delivers an updated, ready-to-run project — zero coding on your part.

### Can I use wordcount — single-file CLI word counter in a commercial project?

The code is under the Apache-2.0 license, which allows commercial use without restriction. You can build, sell, and deploy it freely. Full text: [LICENSE](LICENSE).

### How do I customise wordcount — single-file CLI word counter's branding?

Yes. The MIT license lets you remove the original branding and ship under your own name. For a guided approach, [remix it on cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp): you get a fresh build with full rebrand and relicense rights.

### How is wordcount — single-file CLI word counter built technically?

Powered by Full-stack app. This repo is the real thing — full source, seed data, and all — ready to clone and start up. Highlights include command-line invocation contract.

## License & rebranding

Released under the [Apache License 2.0](LICENSE) (© 2026 Cenius AI) — free for personal and commercial use. The Cenius name/logo are trademarks (see NOTICE).

**Need a customized version?** [Remix this app on cenius.ai](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp) — modifications made on the platform come with **full rebrand & relicense rights** over your derivative.

## Built with cenius.ai

This entire application — code, design, seeded demo data — was generated on **[cenius.ai](https://cenius.ai)** from a plain-English description.

- 🚀 [Build your own app on cenius.ai](https://cenius.ai)
- 🎛️ [Remix wordcount — single-file CLI word counter on the marketplace](https://cenius.ai/marketplace/p/wordcount-single-file-cli-word-counter?ref=gh&utm_campaign=wordcount-single-file-cli-word-counter-webapp) — open it in a workspace, prompt for changes, and ship your own version.

More open-source apps: [the Cenius-ai catalog](https://github.com/Cenius-ai) · [showcase index](https://github.com/Cenius-ai/showcase)
