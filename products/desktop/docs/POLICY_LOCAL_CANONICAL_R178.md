# R178 — Policy Delta Desk: local NFC-only change navigation (DRAFT / RELEASE HOLD)

## User-visible improvement
A whole-document NFC-equivalence alert misses canonical Unicode edits when another policy sentence changes at the same time. Policy Delta now adds a **bounded, physical-source-line-cited local NFC-only candidate index** derived from the existing unified-diff hunks. It pairs only one-to-one removed/added lines in the *same* hunk with equal NFC normalization but different original codepoints. Ambiguous duplicates are deliberately omitted. At most 16 candidates are displayed with an explicit overflow count; confidential source text is not repeated in the index.

Example with synthetic lines: before Café and Owner Old; after Cafe plus combining acute and Owner New. This now cites the line-level canonical candidate despite the substantive second edit. The existing NFKC-only local warnings remain distinct; true numerical/word edits, line-ending-only edits, and lookalike glyphs are not labeled NFC-only. Original source bytes, hashes, visible escaped diff and originals remain authoritative. **Unicode normalization is not semantic or legal equivalence; all conclusions require human review.**

## Tests / evidence
- PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r178.py and python -OO target exactly **28 pinned synthetic module tests**, fail on missing/skipped/added tests, and redact all test output.
- Seven additional synthetic end-to-end tests exercise real file snapshots, fingerprints, non-overwriting report publication, mixed edits, duplicate ambiguity and unsafe control rejection. These are part of the inherited complete repository suite, **not** counted as locally passed until executed on the full repo.
- Mandatory Ubuntu and Windows CI steps each run 28 cases twice (normal/optimized Python), for **112 targeted method executions** if both runners function, plus seven integration tests from full suite. A runner-allocation failure is not a test result.

## Safety and release
No source bytes or private paths leave the machine, no edit to originals, no automated compliance decisions, no premium entitlement changes. All six apps remain **UNRELEASED**. Before release: full cross-platform CI and six private Windows x64 candidates, independent physical Windows 11 accessibility (46 observations), real Defender/EDR evaluation, signing, protected premium delivery, independent QD and founder authorization. Never publish unrestricted premium binaries.
