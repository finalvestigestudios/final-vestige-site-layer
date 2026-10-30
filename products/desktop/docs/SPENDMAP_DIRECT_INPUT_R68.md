# R68 — SpendMap Lite direct-call input integrity (UNRELEASED)

## Defect and boundary

\`fvs_suite.spend_analysis.summarize_spend\` is reusable outside its normal CSV reader. Previously a direct caller could supply duplicate/noncanonical physical CSV rows, floating-point or nonfinite money values returned from a custom parser, a malformed normalized vendor key, or an invalid parsed date. Those could invalidate row-level review evidence, merge unrelated spend or undermine exact anomaly calculations. The CSV reader remains the authoritative source of imported byte identity.

## Implementation

\`fvs_suite.spend_input.validated_spend_rows\` checks that input is a bounded list of at most 200,000 mapping records; each has a unique ASCII canonical physical CSV line >=2 (maximum ten digits), text vendor/date/amount, and optional text category. The existing injected callbacks are invoked once per record; their outputs must be an ASCII uppercase alphanumeric vendor key, an actual \`datetime.date\` rather than \`datetime.datetime\`, and a finite exact \`Decimal\`. Callback failures become fixed, sanitized errors containing only validated physical source rows, not confidential source cells. It rejects invalid input before a report can be returned.

\`summarize_spend\` now consumes those validated tuples without changing report headers, source digests, row order, vendor-collision flags, monthly sums, refund subtraction, deterministic sorting, historical median or spike thresholds. Empty/omitted categories remain \`Uncategorized\`, blank normalized vendors retain the R59 error, and both free and premium products continue to require human review of all compliance-related findings.

This change is source-only and does **not** authenticate caller-provided source digests, prevent malicious Python callbacks, certify financial accuracy, or replace the descriptor-verified CSV intake/atomic report publication. No telemetry, network processing, approvals or new downloads are added.

## Test evidence and release gate

Focused new regression module: \`tests/test_spend_input_r68.py\` (28 \`unittest\` test methods, including parameterized adversarial cases). Prior compatibility: \`test_spend_provenance_r59.py\` (20 methods), \`test_spend_running_median_r60.py\` (13 methods). On Linux Python 3.13.5, 61/61 cases passed normally and 61/61 under \`-OO\`, warnings treated as errors, using exact committed production module dependencies copied to a focused local source tree. \`compileall\` passed. R60 tests were reconstructed from source, not established by matching their exact original Git blob; treat this as focused compatibility evidence, **not the entire authoritative repository suite**.

Commands from \`products/desktop\`:

\`\`\`sh
PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_spend*' -v
PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_spend*' -v
python -m compileall -q fvs_suite/spend_input.py fvs_suite/spend_analysis.py tests/test_spend_input_r68.py
\`\`\`

**Still blocked:** Complete private-repository normal/-OO source gate, native Windows 11 x64 build and actual six-EXE smokes, malicious-input GUI checks, screen reader/keyboard accessibility, malware scan, checksums, premium authenticated distribution and independent QD/founder release approval. Issue #75 tracks GitHub Actions runner-start failures. Do not merge into production or publish binaries before those gates pass.
