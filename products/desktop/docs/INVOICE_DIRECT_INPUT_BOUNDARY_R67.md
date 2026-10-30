# R67 — Invoice Twin Scout direct-engine input boundary

**Status: source-only draft; not released or independently QD-approved.** This change applies only to the free Invoice Twin Scout matching engine. No premium files, customer inputs, telemetry, WordPress catalog, or binary distribution change.

## Why this boundary matters

The normal CSV importer validates monetary and date text, but `invoice_match.candidate_pairs` is also a reusable Python function. Previously direct calls could silently accept floating-point amounts, nonfinite Decimals, boolean candidate limits (`True == 1` in Python), malformed physical row citations, or repeated source-row identities. Those values could undermine audit comparability even when the standard GUI had already checked its inputs.

R67 adds a pre-grouping validation pass. For every record the matching engine now requires an exact finite `Decimal`, an actual `datetime.date` (not a `datetime.datetime`), normalized uppercase ASCII alphanumeric vendor/invoice keys, and a unique positive canonical physical CSV row of at most ten digits (line 2 or later). Missing or malformed data fail with **fixed, private-data-free** messages. A direct caller cannot submit more than 200,000 records, mirroring the existing CSV import bound. Boolean or floating-point policy arguments are rejected. No rounding, coercion, automatic compliance conclusions or network calls are added.

The accepted input domain, two matching classifications (`exact_invoice_key` and `review_possible_duplicate`), seven-day inclusive window, first-source-record exact-key anchor, chronological near matches, report schema, candidate IDs, report atomicity, and 100,000-candidate default limit remain unchanged for valid CSV imports. Validation happens before candidate grouping, so no incomplete return value can masquerade as a completed duplicate scan.

## Reproduce and review

From `products/desktop` in a trusted checkout:

```powershell
python -W error -m unittest -v tests.test_invoice_boundary_r67
python -OO -W error -m unittest -v tests.test_invoice_boundary_r67
python -m compileall -q fvs_suite/invoice_match.py tests/test_invoice_boundary_r67.py
```

R67's focused synthetic tests cover Decimal half-cents, malformed and duplicated source-line references, record and candidate limits, nonfinite/float/bool inputs, invalid keys and dates, error redaction, deterministic matching, no input mutation and normal / optimized Python parity. Run the existing R4 scale tests and complete `unittest discover` on a full authoritative checkout; isolated focused test success does **not** establish suite-wide or packaged Windows compatibility.

## Release hold

No Windows executable is authorized by this patch. Runner-allocation failures tracked in issue #75 must be resolved or a trusted Windows 11 x64 test environment must execute the complete release gates, including all six app binaries, AV checks, accessibility, checksums, premium access controls, and independent QD/founder approval. All duplicate findings require human review; no fraud determination is made.
