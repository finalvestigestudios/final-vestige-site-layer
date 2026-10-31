# Labs R76 — Policy Delta Desk control-safe, unambiguous diff display

**Draft engineering change. Not a product release or legal opinion.** Stacked
on R75; independent QD/founder sign-off remains mandatory.

## Defect and customer impact

Policy Delta Desk accepts three common source line endings: LF, CRLF and
CR-only. The R26/R64 reader correctly fingerprints exact original bytes,
but the unified-diff writer previously copied source carriage returns (CR)
and tabs directly into the report. A viewer or terminal can interpret CR
as cursor movement, potentially overwriting the visible start of a before/
after line. Tabs can distort alignment. Simply replacing CR with a printed
backslash-r is ambiguous when a source document literally contains those
two characters.

This is a **report readability and evidence-review hazard**, not an assertion
that previous source SHA-256 fingerprints were wrong.

## Implemented behavior

For every source line of the human-readable diff (removed, added and context),
the renderer escapes in this exact order:

1. Literal source backslashes become doubled visible backslashes.
2. Horizontal source tabs become a visible backslash-t sequence.
3. Source CR becomes a visible backslash-r sequence.

The first two unified-diff headers and all hunk-range metadata remain intact.
CR-only source lines still receive a report line break; missing-final-newline
markers remain intact. SHA-256 source fingerprints, UTF-8/BOM behavior,
physical line counts, validation caps and atomic non-overwriting publication
remain unchanged. Original TXT/MD/CSV inputs are never modified.

Reports explicitly announce this display encoding. Output is a **human-review
display, NOT a machine-applicable patch**: displayed escapes must not be
blindly applied as original policy text. Consult source files and SHA-256
evidence. No legal, compliance, procurement or payment conclusions are made.

## Concrete scope

- fvs_suite/policy_diff.py: display encoding and report disclosure.
- tests/test_policy_display_r76.py: 24 real local-policy-snapshot and atomic
  report tests using synthetic data. Covers LF, CRLF, CR-only, mixed endings,
  escaped-vs-literal ambiguity, tabs, context and hunk positions, exact SHA-256,
  BOM-only review, unchanged originals, prohibited controls and non-overwrite.
- fvs_suite/smoke.py: adds packaged-policy smoke invariants 46, 47 and 48,
  covering raw controls, escaped display strings and original-byte digests.
  The new packaged checks have NOT yet run as an EXE.
- README.md: customer-facing notation disclosure and release hold.

## Local executed evidence (2026-10-31 UTC)

Python 3.13.5, Linux x86_64. Focused harness contains the exact fetched and
Git-blob-verified policy_diff.py, csv_snapshot.py, and atomic_text.py, plus
the new exact test file. Commands:

    PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_*r76.py' -v
    PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_*r76.py' -v
    python -m compileall -q fvs_suite tests

**24/24 PASS** normal, **24/24 PASS** optimized, compileall **PASS**. This is
real source snapshot and report integration for the exact changed policy
module, but NOT a verified full private repository checkout.

## Outstanding release gates

Existing R26/R64 policy suites, full six-app normal and optimized tests,
changed packaged smoke checks, real Windows x64 executable and GUI validation,
malware scan, binary checksums, premium entitlement and purchase/download
access, QD independence and founder approval remain unverified. GitHub Actions
continues to fail before executing jobs; runner blocker: issue #75.

**Next highest-impact action:** Repository owner restores Actions runner
allocation; alternatively, a trusted Windows x64 workstation runs
products/desktop/scripts/verify-windows-candidate.ps1 with -Build after full
source checks. No EXEs are released, no premium assets are made public, and no
WordPress production change is authorized by this sprint.
