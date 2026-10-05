# Salam Subtitle Check

An offline SRT subtitle validator built with the
[Salam Programming Language](https://github.com/SalamLang/Salam).

Check subtitles before publishing a video: find malformed timestamps, reversed
time ranges, overlapping cues, numbering gaps and text that may be hard to read.
The program only reads the specified file. It does not rewrite subtitles, send
data over the network, or require an account.

## Build and run

The verified configurations are **Windows x64, Salam 0.4.8, GCC 10.3.0
(TDM-GCC)** and **Linux x64 under WSL Ubuntu, Salam 0.4.8 with its embedded
LLVM/LLD musl target**.
Download Salam from the [official releases](https://github.com/SalamLang/Salam/releases/tag/v0.4.8)
and, for the Windows commands, make `salam` and `gcc` available in your terminal. The compiler and standard
library are not vendored into this repository. No third-party Salam packages
are required.

In PowerShell, from the repository root:

```powershell
New-Item -ItemType Directory -Path build -Force | Out-Null
salam build src/main.salam --backend=c --cc=gcc --output=build/subtitle-check.exe --log-level=error
./build/subtitle-check.exe examples/clean.srt
```

Expected output:

```text
Checked 2 cues: 0 errors, 0 warnings.
```

`--cc=gcc` also avoids a Salam 0.4.8 bundled-TCC launch failure when its
installation path contains spaces.

On Linux x64, use the official Linux release, which includes the LLVM/LLD
toolchain and musl sysroot. GCC is not needed for this command:

```sh
mkdir -p build/linux
salam build src/main.salam --target=x86_64-linux-musl --output=build/linux/subtitle-check --log-level=error
./build/linux/subtitle-check examples/clean.srt
```

Other operating systems and architectures have not been verified for this
project. The Linux archive tested on 2026-10-05 had SHA-256
`55810d1dc85dde83b502ec96a97dd3d9ac94c4d4ad596be1517a368491b48d88`.
Its `salam version` output reports 0.4.8 and source commit
`f9fdc5522e8862d98fd3ba32375dda376a90156f-dirty`; this is the official
release asset's embedded build metadata.

## Options and reports

```powershell
./build/subtitle-check.exe --json examples/warnings.srt
./build/subtitle-check.exe --strict examples/warnings.srt
./build/subtitle-check.exe --max-cps 25 --max-line 48 'my subtitles.srt'
./build/subtitle-check.exe -- '--file.srt'
```

| Option | Meaning |
| --- | --- |
| `--json` | Emit one JSON object to standard output. |
| `--strict` | Return exit code 1 for warnings as well as errors. |
| `--max-cps N` | Maximum characters per second; default 20, range 1–1000. |
| `--max-line N` | Maximum characters per line; default 42, range 1–1000. |
| `--` | Treat all following arguments as filenames (exactly one is required). |
| `--help`, `-h` | Show usage. |

Exit codes are **0** for accepted input, **1** for subtitle errors (or warnings
with `--strict`), and **2** for invalid arguments or a file/encoding failure.
Warnings are editorial suggestions; overlapping bilingual subtitles, for
example, may be intentional.

Successful inspection, including inspection that finds subtitle errors, has
this JSON shape:

```json
{"schema_version":1,"file":"examples/clean.srt","exit_code":0,"cues":2,"errors":0,"warnings":0,"diagnostics":[]}
```

Each diagnostic contains `severity`, `code`, `line` (one-based physical source
line), `cue` (parsed identifier), and `message`. Diagnostic order follows the
parser, timing, and readability passes; it is not necessarily source order.
The `cues` count includes only blocks with parseable timestamps. An invalid
identifier is represented internally and in related diagnostics as `-1`;
the initial `E_NUMBER` diagnostic uses `0` for an unknown cue.

Operational failures with `--json` have `schema_version`, `file`, `exit_code: 2`
and `fatal`. Put `--json` before other options if you also want argument errors
as JSON. Without `--json`, operational failures go to standard error. `--help`
always prints plain text. Subtitle text is omitted from reports.

## Supported input and limits

- UTF-8, with or without an initial BOM. LF, CRLF and lone CR endings work.
- Windows Unicode filenames are supported through a wide-argument workaround
  for Salam 0.4.8's narrow `args()` implementation.
- Timestamps use exactly `HH:MM:SS,mmm`, with hours 00–99 and minutes/seconds
  00–59. Positioning extensions on timing lines are rejected explicitly.
- Cue identifiers must be positive decimal integers of at most nine digits.
  Blank or whitespace-only lines separate cue blocks.
- Maximum file size is 1 MiB; maximum nonempty cue blocks is 5,000.
- NUL bytes, invalid UTF-8 and ASCII control characters other than tab/line
  endings are rejected. UTF-16 and legacy code pages are unsupported.
- Readability counts Unicode **code points**, including spaces and literal
  markup, but excluding line breaks. It does not render HTML tags, decode
  entities, measure display width, or combine emoji/grapheme sequences.
- Duration suggestions are below 500 ms or above 7 seconds. More than two text
  lines also produces a warning. These defaults are heuristics, not an SRT
  specification or accessibility certification.

See [diagnostic codes](docs/diagnostics.md) for the complete reference.

## Verify the application

Tests use synthetic data only. Python 3 is needed for the black-box test runner,
not for the compiled application.

```powershell
./scripts/check.ps1
# Or specify compiler locations without changing PATH:
./scripts/check.ps1 -Salam 'C:\tools\salam\salam.exe' -Compiler 'C:\tools\gcc\bin\gcc.exe'
```

On Linux x64:

```sh
sh scripts/check.sh
# Or use a compiler extracted outside PATH:
SALAM='/path/to/salam-linux-x86_64/salam' sh scripts/check.sh
```

The script builds the application and native Salam tests, then runs the CLI
through Python's standard library. The current suite has **55 native assertions
and 39 end-to-end cases**. It covers timestamp boundaries, parser recovery,
nested overlaps, Unicode character counts and filenames, JSON decoding,
exit codes, all three newline styles, BOMs, malformed UTF-8, input limits,
and unchanged file hashes after inspection. Both suites passed on the Windows
and Linux configurations above; no Docker execution is claimed.

For manual inspection, the examples include a clean file, a warning-only file,
and a file with two errors. All examples were written for this project.

## Source layout

| Module | Responsibility |
| --- | --- |
| `model.salam` | Cue/diagnostic records, ownership and counts. |
| `timestamp.salam` | Strict bounded timestamp and identifier parsing. |
| `parser.salam` | SRT block parsing, recovery and physical line numbers. |
| `source.salam` | Bounded file reads, UTF-8 checks and newline normalization. |
| `timing.salam` | Ordering, overlaps and duration diagnostics. |
| `readability.salam` | Unicode line lengths and reading speed. |
| `cli.salam` | Options, help and Windows Unicode command-line arguments. |
| `text_report.salam` | Human-readable reports. |
| `json_report.salam` | JSON escaping and structured reports. |
| `main.salam` | Application orchestration and exit status. |

Development and testing use OpenAI Codex; no independent human technical review
is claimed. The commit history records incremental implementation and actual
validation fixes.

Licensed under GPL-3.0-only; see [LICENSE](LICENSE).
