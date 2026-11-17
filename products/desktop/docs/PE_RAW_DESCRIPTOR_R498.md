# R498 — unbuffered PE candidate inspection (internal, QD HOLD)

**2026-11-17 UTC · Issue #73 · not a release authorization.**

## Bug and scope

R497 probes the final byte of each claimed aligned WIN_CERTIFICATE record to catch
external truncation after a size observation. However the PE parser previously
opened the descriptor using `os.fdopen(fd, "rb")`, yielding a buffered reader.
A small header read may prefetch up to an entire internal block. If another
process truncates the underlying candidate after that read, subsequent
`seek(...); read(1)` in the same buffered reader may return an old cached
certificate-tail byte. A held descriptor alone does **not** guarantee fresh
physical reads while Python readahead remains enabled.

**R498 changes the actual PE parser** to `os.fdopen(fd, "rb", buffering=0)`.
This uses raw `io.FileIO` for structural parsing, WIN_CERTIFICATE tail
inspection and the same-descriptor SHA-256 check. It does not load certificate
payloads, open an independent pathname, execute any binary, or access customer
data. Failure paths still close the owned descriptor and redact private
exceptions. Unbuffered I/O closes a specific false-negative race window; it
does **not** provide a filesystem snapshot, cryptographic signature validation,
malware clearance, or a guarantee against arbitrary concurrent modification.

## Reproduction and new regression coverage

In a Linux CPython local control, read eight bytes of an 8192-byte file,
truncate the file to eight bytes from a separate handle, then seek to offset
4095 and read one byte from the original handle:

- `open(path, "rb")` (buffered control): returned **`b"A"`** (stale).
- `open(path, "rb", buffering=0)` (raw control): returned **`b""`** (EOF).

The committed `test_pe_raw_descriptor_r498.py` adds nine methods:

- Six standalone real-filesystem tests: raw FileIO type, post-truncate EOF,
  multi-position reads after truncation, in-place mutation visibility, pathname
  replacement custody (skipped on Windows where CRT handles may block rename),
  and descriptor cleanup.
- Three parser-binding tests on a trusted checkout: invalid PE still opens
  `buffering=0`; actual inert PE fixture passes the raw FileIO object to
  the integrated certificate guard; all six expected candidate filenames
  pass PE shape plus SHA-256 on inert synthetic images.

**Executed locally:** only the six standalone real-filesystem methods,
**6/6 PASS** on Linux CPython normal and **6/6 PASS** with `-OO`
(12 executions, no skips). Compilation passed. These six tests operate
on the exact Git-blob-matched new regression source. The three parser-binding
methods were added but were **not executed locally**: a trusted full checkout
was unavailable. R497's full parser and six-app release integration suite
also remains unexecuted in this sprint.

Both independent source-evidence and Windows internal-build workflows now
include the nine-method R498 regression module in normal and optimized modes.
CI workflow execution, Windows behavior, all six real EXE builds/smokes, Defender
checks, accessibility and gated premium delivery remain release blockers.

## Reproduce from the feature checkout

```sh
python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_raw_descriptor_r498.py
python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_raw_descriptor_r498.py
python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py
python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py
```

Use the source-evidence workflow on Ubuntu and Windows x64, then the internal
build workflow; do not use a source-only success to authorize publishing.

**Release gates preserved:** private local-first data, exact Decimal monetary
logic, deterministic audit and human review are untouched. Neither the four
free nor two premium products is released. Premium download entitlements,
independent QD review and explicit founder approval are required before any
public distribution. No merge, production site update, or executable release
is part of R498.
