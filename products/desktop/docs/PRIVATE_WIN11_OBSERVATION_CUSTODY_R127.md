# R127 — privacy-safe, source-bound human observation intake (DRAFT / RELEASE HOLD)

**Issue #73 · Stacked on R126 draft PR #548, not `main`.** No distribution or public website changes.

## What R127 protects

The R122 one-check Windows 11 witness writer previously read `--observation-file`
with a generic file-open helper. It rejected note locations inside the candidate
EXE directory but did not require the note to be an ordinary unlinked file.
A reviewer could inadvertently select a symlink/junction to an unrelated
local financial record, a hardlink, the raw R9 custody report, or an existing
witness as their note. If the contents happened to pass the textual constraints,
they would be copied into the human review evidence. The writer also could not
reliably notice an ordinary file swapped during intake.

R127 requires an independent **regular, single-linked UTF-8 note file** and
verifies its identity and size before, during and after an exact size-bounded
descriptor read. It rejects linked inputs and linked/reparse ancestors, raw R9
report paths, review matrix paths, notes from inside executable or witness
custody, malformed UTF-8, oversized input, and path replacement, including a
byte-identical file replacement. On POSIX, nonblocking no-follow descriptors
avoid following a late symlink or blocking on a substituted FIFO. On Windows,
descriptor-to-path identity and metadata checks provide best-effort race
detection. Failed intake leaves the matrix and any previously recorded
evidence unchanged.

The guard emits **no observation text, customer path, or private file content**
on CLI failure. It does not redact valid human-entered observations: reviewers
must never paste sensitive client data, ledgers, PII, secrets or screenshots.
It is not a defense against a privileged attacker with full filesystem control,
malicious clock manipulation, all possible filesystem driver behavior, or
in-place mutation engineered to preserve all metadata.

## Reviewer procedure

On a real independent Windows 11 x64 workstation, use a private ordinary
folder such as `C:\PRIVATE\review\notes`, separate from `witnesses` and the
six executable candidates. Create a new, original UTF-8 `.txt` containing
a meaningful observation of **one personally performed** check. Do not
point `--observation-file` at a symlink, network redirect, hardlink, R9
report, review matrix, or previously recorded witness.

Run the existing [R122 one-check command](PRIVATE_WIN11_WITNESS_WRITER_R122.md)
with the independently authenticated R9 digest. The writer still requires
source-bound six-app custody, Windows 11 workstation validation, an unchanged
46-check matrix, an exclusive cooperative lock, and a named human PASS/FAIL.
An intake HOLD requires manual custody investigation; do not bypass the guard
or modify historical evidence.

## Regression scope

`test_windows11_observation_input_r127.py` contains **13 synthetic,
source-owned methods**. The exact-method runner
`scripts/safe_unittest_r127.py` rejects missing, extra, skipped and
unexpected methods and redacts failures. Mandatory Linux and Windows GitHub
Actions run both normal Python and `-OO` (52 method executions total).
Coverage includes ordinary notes, linked sources, linked parents, hardlinks,
oversize/UTF-8 failures, R9 path and witness input, file replacement
before opening and after opening, nonregular inputs, privacy-safe CLI errors,
and production assertions. The existing R122 lock mutation regression is
retargeted to the descriptor reader.

All tests use synthetic fixtures, no customer data and no true physical
Windows 11 accessibility observation. Actual executable custody, all **46
human Windows 11 checks**, genuine Defender/EDR with history, code signing,
authenticated premium distribution, independent QD and founder authorization
are still missing. **All six utilities remain UNRELEASED.**
