# Policy Delta Desk R26 — bounded provenance and trustworthy text differences

**Status:** Engineering-only source. No approved binary, download, or legal interpretation.

## Problem and deliverable

The old policy comparator checked a pathname's stat then read the entire text,
used unsanitized basenames as unified-diff headers, had no physical-line cap,
and did not cite the compared file bytes. It also used difflib's raw joined
output, which can concatenate changes to final lines lacking a newline.

The new products/desktop/fvs_suite/policy_diff.py performs **all input
validation before allocating an output file** and returns the same one-report
list as the prior engine.policy_delta entrypoint.

## Input contract (two distinct named local source paths)

* Existing .txt, .md or .csv files; UTF-8 text (UTF-8 BOM accepted); no network.
* 10 MiB maximum per source, checked via fstat on an opened descriptor and
  bounded read of 10 MiB + one byte. Files grown or modified by another process
  remain a local concurrency risk; byte digests reflect precisely what was read.
* 50,000 physical text lines maximum per source; larger files must be split.
* Reject NUL, other ASCII/C1 control characters except TAB/LF/CR, Unicode
  bidirectional directional overrides/isolates, ambiguous Unicode line
  separators, and an embedded BOM. These can otherwise conceal or spoof changes.
* Invalid UTF-8 and unreadable local input return sanitized error messages.
* The originals are never modified, uploaded, renamed or transmitted.

## Output and evidence limitations

One UTF-8 text report includes a non-legal-advice banner, escaped JSON-quoted
source basenames, physical line counts, and SHA-256 digests of **raw input bytes**.
The deterministic unified text diff preserves changed line content and includes
the visible Git-style marker "\ No newline at end of file" for unterminated lines.
Identical decoded content with a BOM-only difference will show **no textual
change** but still produce different SHA-256 fingerprints; reviewers must
distinguish byte integrity from textual equality.

The SHA-256 digests are **not signatures** and do not establish that a document
is authentic or legally binding. CSV is compared as text, *not* parsed or
normalized; TXT/MD contents are not legal interpretations. Human verification
of every substantive change remains mandatory.

## Actual tests and release controls

17 tests in tests/test_policy_diff_r26.py execute real local file I/O and
the comparison helper directly. They cover exact SHA-256 provenance,
good/identical/BOM/Unicode inputs, no-final-newline markers, newline-only
differences, invalid UTF-8, NUL and deceptive controls, input-size boundaries
(including a sparse >10 MiB file), physical-line caps, unsupported extensions,
filename-header injection, no partial report, and no report overwrite.

The separate test_policy_engine_r26.py adds four real-engine integration
checks that **must** pass on a complete connected repository checkout;
do not claim they have passed until actually executed. The standard CI suite
runs on both Windows and Linux, with these two files also in the optimized
Python verification step. CI infrastructure may still be failing before
step 1 (BlobNotFound), which is not a successful test result.

Before release, run the full regression suite in a trusted checkout; build
and inspect all six Windows x64 EXEs, smoke-test them as native processes,
record SHA-256 inventories, scan binaries, verify premium access controls,
and obtain independent Final Vestige site/QD approvals. No files from this
work may be published as public executable downloads.
