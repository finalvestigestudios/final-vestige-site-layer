# R400 — Visibly distinguish Unicode combining marks in financial identity evidence

**Scope:** Final Vestige Labs issue #73; shared financial audit-display source labels and premium human-review queue references. **DRAFT — independent QD and founder HARD HOLD.** Stacked on R399 draft PR #2327, not production main. No binaries or premium download links are authorized.

## Reproduction and impact

Prepatch fvs_suite.audit_display.visible_identity_label displayed Café and the canonically equivalent but byte-distinct Cafe\u0301 as visually indistinguishable labels, even though their source spellings and identity bytes differ. An original str subclass with a custom __iter__ also reached the generic source renderer and executed that hook before an audit cell was produced. The latter is a local Python API hardening concern, not evidence of customer exploitation.

The existing ledger/procurement matching rules can require human review of distinct original identities; hiding those differences at the presentation layer makes the review evidence difficult to interpret. The diff-only Policy Delta Desk already has separate combining-mark visibility; this patch does not change it.

## Changes

- fvs_suite/audit_display.py: visible_identity_label now requests combining-mark disclosure for Unicode **Mn/Me** categories. Each raw combining codepoint is rendered as a deterministic \uXXXX/\UXXXXXXXX cue, with literal backslashes escaped first, so a typed escape cannot impersonate a real mark.
- General visible_source_text retains its prior readable multi-language rendering by default; only financial *identity labels* activate extra combining-mark visibility. An exact native str check prevents a subclass from executing an overridden iteration hook at this shared rendering boundary.
- Premium visible_review_row, shared source-label lists, and callers of review.labels_for_report inherit the identity-specific cue without changing original case IDs, flags, monetary values or provenance.
- Added tests/test_review_combining_identity_r400.py with **19** offline synthetic methods including NFC/NFD twins, enclosing marks, multiple marks, literal escape impersonation, semicolon/boundary whitespace, malicious string subclasses, immutable input and compatibility with legacy plain text.
- Extended the independent Ubuntu/Windows source workflow to run those methods in both standard and python -OO -W error modes. This is not a release workflow or publication authorization.

## Measured verification — exact tested source subset, not full repository

On Linux CPython 3.13.5, with unchanged R399 unicode_hazards.py, the **exact committed blob** of audit_display.py and **exact committed blob** of the new R400 test file were run locally:

- Standard: **19/19 PASS**.
- Optimized -OO -W error: **19/19 PASS**.
- Total **38/38 focused test-method executions PASS**.
- py_compile of edited code and tests: PASS.
- Exact Git blob verification: audit_display.py = 3551c838fcc6aed8bdb4d1c5262a485d13a9582a; test_review_combining_identity_r400.py = 7ad21577dc5505542b20a36a6dbaa14e3e94878d; unchanged unicode_hazards.py = 50801b3f168396b0e2c75e95352e435f7c936588.
- Prepatch reproduced both the visually ambiguous NFD identity and unexpected custom str.__iter__ execution; patched tests reject the latter before iterating.

**Not verified:** complete repository integration, inherited R81/R97/R399 full tests, real CSV/report imports, six-app financial/Decimal and crypto suites, native Windows runtime, Windows x64 binary execution, Defender scan, screen-reader acceptance, premium entitlement distribution. Passing these isolated synthetic tests does not establish release readiness.

## CI and release hold

Prior R399 exact-HEAD [source CI](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43408329569) and [desktop build](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43408329620) failed within seconds with **runner_id=0** and **zero recorded job steps**; both consumed **zero billed milliseconds**. Logs returned 404 BlobNotFound. Root cause not established; inspect GitHub Actions check annotations, spending/eligibility and repository-level runner access before claiming a code failure or pass. Inspect R400-specific runs after opening the draft PR.

## Acceptance criteria / next highest-impact action

1. Restore hosted GitHub Actions runner allocation; execute the exact R400 SHA's R400/R399/R81/R97 and all source/integration/financial/crypto suites on Ubuntu and genuine Windows.
2. Confirm that actual six distinct Windows x64 executables launch and exercise offline imports/exports with source hashes preserved; record Defender scans, keyboard/screen-reader manual evidence and signed/unsigned status.
3. Separately verify that both premium binaries can be accessed **only** through an authorized entitlement/payment flow.
4. Obtain independent QD review and explicit founder approval before merge, product availability, WordPress publication or any download distribution.

No customer data, telemetry, automated compliance decisions, source bytes, payment approval, release branch, site or premium package was touched by R400.
