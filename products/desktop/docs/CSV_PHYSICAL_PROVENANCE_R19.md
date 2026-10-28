# R19 — Physical CSV source citations and strict record boundaries (pre-release)

## Defect addressed

The shared `engine.table()` formerly labeled records using
`enumerate(csv.DictReader(...), 2)`. That produces **logical** record ordinals,
not the physical line number in the actual source file. A valid quoted
multi-line memo or a blank line ahead of a transaction causes exported
`left_rows`, `right_rows`, `row_a`, `row_b`, `claim_rows`, and
`invoice_rows` references to point at the wrong source lines. Financial
reconciliation and audit review must not cite the wrong evidence.

R19 uses Python's strict `csv.reader` and captures the **first physical
line** of each complete CSV record. It preserves quoted embedded newlines,
UTF-8 BOM files, blank-line skipping, normalized-header ambiguity rejection,
the 200,000-*record* cap, and existing key/money normalization.

The parser now fails closed for a truncated field count, an extra field, or
unclosed/malformed CSV quoting. Previously some truncated rows (including an
optional category) silently became empty values. Reports are not written when
input parsing fails. Input parsing remains local; report references do not
authorize grant eligibility, payment, procurement compliance or fraud findings.

## Exact reproducibility and interpretation

Example physical input:

```csv
id,amount,notes
A,10,"first line
second line"

B,20,ordinary
```

The resulting record `row` references are **2 and 5**, not 2 and 3.
A CSV record's `row` means the physical **start** line, not its final line
and not its ordinal among nonempty CSV records. Source row references remain
file-relative. The original source files are not rewritten.

A missing optional column is still permitted; **if a column is present**, every
nonblank record must contain its field, even if the value is empty. Supply
`,` for an empty trailing cell, not an omitted field. Blank CSV records
between data records remain ignored, as before.

## Verification

Local independent isolated parser harness (Python on Linux, no app bundle):

```text
python -m unittest -v test_table_impl        # 12/12 PASS
python -OO -m unittest -q test_table_impl    # 12/12 PASS
python -m compileall -q table_impl.py test_table_impl.py
```

Those focused tests reproduced the new parser logic and a representative set
of alias mappings, including multiline headers/fields, blank lines, malformed
row widths, broken quotes, duplicate aliases, BOM and optimization mode.
They **do not** establish a full-repository pass.

The 12 new committed **integrated** regression tests live in
`tests/test_csv_physical_provenance_r19.py` and exercise the actual shared
parser plus LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, GrantAudit
Studio Pro and ProcureGuard Studio Pro; Policy Delta Desk reads TXT/MD/CSV as
*text* rather than using this tabular finance parser. Run at the repository root:

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_csv_physical_provenance_r19.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_csv_physical_provenance_r19.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

Run those against the **exact checkout**, then execute Windows build and
smoke verification before release. Existing GitHub Windows jobs continue to
fail *before any runner steps* (`404 BlobNotFound` reported when retrieving
logs). No claim is made that the integrated 12 tests passed, that the Windows
binaries were built, or that QD approval has been granted.

## Boundaries and next step

No payment decisions, human exception states, premium license issuance,
website/QD review flow, binaries, or download permissions changed. This is a
draft stacked development branch. Restore Windows runner execution or use a
trusted Windows x64 workstation to execute the entire suite and six-app
portable build/checksum/smoke workflow, then review any integration failures
before considering gated distribution.
