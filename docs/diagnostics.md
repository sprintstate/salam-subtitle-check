# Diagnostic reference

Errors return exit code 1. Warnings return 0 unless `--strict` is set.

| Code | Severity | Meaning |
| --- | --- | --- |
| `E_EMPTY` | error | No cues were found. |
| `E_NUMBER` | error | The identifier is not a positive decimal integer of at most nine digits. |
| `E_TIMING` | error | A timing line or its `-->` separator is missing. |
| `E_TIMESTAMP` | error | A timestamp is malformed/out of range, or a positioning extension is present. |
| `E_TEXT` | error | A cue has no subtitle text. |
| `E_DURATION` | error | The end time is less than or equal to the start time. |
| `E_LIMIT` | error | More than 5,000 nonempty cue blocks were encountered; inspection stops. |
| `W_SEQUENCE` | warning | The identifier differs from the one-based position among parsed cues. |
| `W_ORDER` | warning | Start time goes backwards compared with the previous parsed cue. |
| `W_OVERLAP` | warning | The cue starts before the latest end of an earlier valid-duration cue. |
| `W_SHORT` | warning | Duration is below 500 ms. |
| `W_LONG` | warning | Duration is above 7 seconds. |
| `W_LINES` | warning | A cue has more than two text lines. |
| `W_WIDTH` | warning | A line exceeds `--max-line` Unicode code points. |
| `W_CPS` | warning | Text exceeds `--max-cps` code points per second. |

Equal endpoints on adjacent cues do not overlap. The overlap check retains the
latest prior end, so an enclosing cue is still detected after a shorter cue
ends. Invalid-duration cues do not extend that end. After a malformed block,
parsing resumes at the next blank-line boundary; numbering suggestions may
therefore accompany parser errors.

File access, encoding, size and usage failures are operational errors (exit 2),
not entries in the diagnostic array. JSON mode reports them through `fatal`.
