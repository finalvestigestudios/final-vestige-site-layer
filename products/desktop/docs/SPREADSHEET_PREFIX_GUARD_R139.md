# Labs R139 — Shared CSV invisible-prefix formula defense (DRAFT / HARD HOLD)

## Scope and purpose
Five financial applications use a shared local CSV report writer. The writer
already escaped leading equals, plus, at, and nonnumeric minus formulas, but
str.lstrip() does not remove all directional/zero-width Unicode prefixes. Some
spreadsheet importers differ about which invisible characters they ignore.
R139 quotes all report cells whose leading prefix contains a hidden format,
control, variation, unassigned/private-use, non-space whitespace or combining
character, before any formula could be interpreted. A leading ordinary ASCII
space and a true negative fixed-point numeric cell remain unchanged.

## Examples, synthetic only
- =2+2 becomes literal apostrophe then =2+2.
- U+200B followed by =2+2 becomes apostrophe, same U+200B, same text.
- U+202E followed by @x becomes apostrophe, same U+202E, same text.
- A tab followed by ordinary text also gains the conservative quote.
- -0.01 stays -0.01, but -SUM(A1) gains a leading apostrophe.

This only changes rendered report cells. Original source files, snapshot
SHA-256 digests, source physical-row references, exact Decimal arithmetic,
review statuses and premium access controls remain unchanged. The independent
audit-display layer is still responsible for showing interior invisible
characters: this writer does NOT rewrite every Unicode character. It also
preserves existing atomic, no-overwrite publication on Windows and Linux.

## Source, reproducible CI and limitations
- Engine: products/desktop/fvs_suite/engine.py (safe_cell)
- 20 synthetic direct, CSV writer and true LedgerDiff/Invoice Twin/SpendMap tests:
  products/desktop/tests/test_spreadsheet_prefix_guard_r139.py
- Strict method-owned no-skip runner:
  products/desktop/scripts/safe_unittest_r139.py
- From repository root with PYTHONPATH=products/desktop:
  python products/desktop/scripts/safe_unittest_r139.py
  python -OO products/desktop/scripts/safe_unittest_r139.py
- Mandatory both-OS steps: .github/workflows/desktop-build.yml.
  Expected 20 methods x two Python modes x Linux/Windows = 80 named
  executions only when exact-head CI is COMPLETED/SUCCESS on both jobs.

These tests do not execute Excel, prove universal protection across every
spreadsheet importer, replace encrypted premium distribution, or constitute
physical Windows acceptance. For untrusted CSVs, explicitly import columns as
TEXT in the chosen spreadsheet. Original source and SHA-256 are authoritative
if a spreadsheet displays an apostrophe or other encoding differently.

Release remains HOLD until independently authenticated private six-EXE custody,
all 46 real human Windows 11 accessibility observations, actual Defender/EDR,
code signing, gated premium delivery, independent QD and founder authorization.
No EXEs or private customer data may be placed at public download URLs.
