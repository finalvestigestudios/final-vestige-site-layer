# R276 — Six-engine source-smoke receipt custody

**Issue:** #73. **Scope:** private, offline Windows x64 candidate acceptance only. **Status:** DRAFT / independent QD and founder hard hold; no public binaries, site changes, premium URLs or release approval.

## Verified defect in R275 receipt validation

The private candidate runner previously required six source-smoke entries in the correct **application name** order, each with `result == "PASS"`. It did **not** validate the associated `engine`, the claimed `synthetic_output_count`, or unexpected evidence fields. Consequently, a source-smoke receipt could say that LedgerDiff Lite had passed **the procurement engine** with **zero output files**, yet the old app-name/PASS predicate would accept that contradictory evidence. The R276 regression reproduces the original predicate accepting precisely this synthetic counterexample. This finding is about evidence validation, **not** a claim that the actual source tests or packages had failed.

## Change

`products/desktop/scripts/source_smoke_receipt_r276.py` now provides a strict read-only validator called from `offline_windows_candidate_r269._source_receipt_sha256`. Exactly six **native** Python dictionaries in the existing fixed product order are required; each must have exactly `app`, `engine`, `result`, and `synthetic_output_count`. The required app/engine pairs are:

| Product | Engine |
| --- | --- |
| LedgerDiff Lite | `ledger` |
| Invoice Twin Scout | `invoices` |
| SpendMap Lite | `spend` |
| Policy Delta Desk | `policy` |
| GrantAudit Studio Pro | `grants` |
| ProcureGuard Studio Pro | `procurement` |

`result` must be the literal string `PASS`; synthetic output count must be an exact positive integer in `1..10000`. Zero, bool, float, huge counts, missing/extra fields, wrong engines, duplicate products, subclasses or unsafe/private extra data cause the existing fixed `CandidateBuildRejected(ERROR)` without echoing financial paths. The emitted source-smoke producer already supplies the canonical fields. The runner retains R270–R275 source-suite checksums, tested-source binding and all existing build, PE, attestation and final-custody gates.

This validator proves **receipt shape and internal consistency only**. It does not independently prove past execution, authenticate a hostile producer, verify native binaries, license premium use or authorize compliance outcomes.

## Executed local verification

Exact committed content was mirrored in a small local workspace and its **Git blob SHAs were compared** with GitHub after writing: helper `364c35f0d7ede1b16653fe0fb0b565221fb1a09f`; test `bda5f69c259a7ba8182619e377f814d5fe65013a`.

```text
Linux CPython 3.13.5
python -W error -m unittest discover -s products/desktop/tests -p test_source_smoke_receipt_r276.py -q
Ran 26 tests — OK
python -OO -W error -m unittest discover -s products/desktop/tests -p test_source_smoke_receipt_r276.py -q
Ran 26 tests — OK
python -m compileall -q products/desktop
PASS
```

**52/52 focused executions**: canonical evidence, exact boundary, six product/engine mismatches (subtests), duplicate/reordered/missing entries, false PASS labels, absent/extra sensitive fields, bool/float/string/negative/zero/oversized counts and subclass wrappers. These are **synthetic focused validator tests**: the full inherited repository suite, actual Windows runner integration, private Windows x64 binary builds and native EXE smoke tests were **not** executed in this Linux environment.

Both Linux and Windows CI jobs were updated to run this test in normal and `-OO` modes. Their hosted execution status must be checked on the new draft PR; passing local fixtures do not substitute for native acceptance.

## Required next gate

Restore GitHub Actions worker execution, run the full inherited Python test suite, and then run the private R276 candidate builder on a trusted **Windows 11 x64** workstation using an existing access-controlled private workspace outside checkout. Retain real source-suite evidence, six native PE images, SHA-256 checksums, executable smoke reports, attestation and build custody checks. Independently verify Defender results, keyboard/screen-reader/high-DPI accessibility and premium entitlement/download access before QD review and founder approval. Do not merge to `main` or publish a free/premium executable as a side effect of this sprint.
