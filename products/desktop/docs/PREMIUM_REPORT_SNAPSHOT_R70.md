# R70 — Bind premium review exports and encrypted copies to the opened report

**Status:** source change on an isolated stacked draft PR. All six Windows utilities remain **unreleased**.

## Problem and failure condition

The human-review workbench shows an exception report opened at time T0. A different, well-formed CSV may subsequently replace it on disk. The existing review *append* API checks its expected SHA-256, but the register export and encrypted backup calls previously accepted the current path without the opened report's expected SHA. As a result, a valid later file could be exported or sealed despite the operator still seeing evidence from T0.

## Invariant implemented

* The review window revalidates the selected report and complete review journal before review, register export, and encrypted backup actions. If validation fails or the immutable loaded report batch differs, it clears the actionable queue and visible selection.
* \`export_register\` forwards the expected loaded SHA-256 to the atomic writer. The publisher verifies it before staging and again after consuming all rows, immediately before atomic publication; observed changes fail without a final CSV or leftover partial file.
* \`seal_evidence\` checks the loaded SHA-256 before reading auxiliary evidence and again after its existing complete source/journal consistency checks, before writing an encrypted \`.fvault\`.
* Existing direct API callers may omit \`expected_report_sha256\` for compatibility. They retain the existing source/journal consistency rules but **are not protected against a valid report substitution that happened before their call**. The premium GUI always supplies the verified SHA-256.
* Fingerprints must be lowercase 64-digit ASCII hex. Failure strings are fixed text and never interpolate financial inputs, paths, or fingerprints.
* No cloud processing, automated authorization, new plaintext persistence, or change to the source/journal formats.

## Executed verification (Linux, Python 3.13.5, isolated source harness)

The harness consists of the exact newly committed \`review_identity.py\`, \`review_queue_load.py\`, \`review_register.py\`, existing \`atomic_reports.py\`, and two new regression test files.

\`\`\`text
PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_*r70.py' -q
22 tests PASS
PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_*r70.py' -q
22 tests PASS
python -m compileall -q fvs_suite tests
PASS
\`\`\`

Tests cover invalid/malformed SHA fingerprints, no leaked financial values, stale or missing sources, corrupt journals, re-open recovery, read-only preflight, exact successful atomic register publication, report replacement before and during staging, journal mutation during staging, and backwards-compatible direct API behavior. The atomic register writer used in the harness is the unmodified original module, not a fake implementation.

**Limits:** This was not a complete private-repository checkout, a real Tk Windows GUI, a cryptographic vault roundtrip, or a native Windows 11 x64 EXE test. The \`exception_review.py\`, \`evidence_vault.py\`, and \`review_ui.py\` integration wiring is committed but unverified against the complete suite. GitHub Actions remains blocked before runner steps begin (issue #75). No release approval is implied.

## Windows acceptance pending

After Actions runner startup is restored: full normal/-OO source tests, all six executable source smokes and native Windows builds; then test report substitution between UI load, file-dialog selection, and encryption prompt on both premium SKUs. Confirm the old report is unselected, no CSV or vault is produced for stale evidence, reloading permits a new verified selection, and security/keyboard checks pass. Require independent QD/founder approval before release. Do not upload customer financial CSVs as evidence.
