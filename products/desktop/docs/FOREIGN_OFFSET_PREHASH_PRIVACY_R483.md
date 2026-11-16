# R483 — Validate foreign-PO source citations before hashing (DRAFT / QD HARD HOLD)

Issue: [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73)  
Parent: R482 draft [#2793](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2793) at `43cb91ddd5eb0065ddd01a00e6ea36c871ecae4c`.  
Scope: ProcureGuard Studio Pro, source-only; **never** production `main`. No publish, no payments, no premium exposure.

## Reproduced defect

`cross_po_foreign_offset_source_rows` deduplicated original source-row objects with `frozenset(row for ...)` **before** invoking the privacy-safe `_source_row_sort_key`. A direct helper caller could supply a `str` subclass or object whose `__hash__` raises, leaks data, or runs code, or an unhashable row whose exception bypasses the standardized privacy error. Normal CSV intake supplies native bounded strings; this is defensive direct-helper hardening for review evidence.

## Change and invariants

For references with real foreign target groups, process each original source row in order:
1. Reject non-native `str` values through `_source_row_sort_key` **before dictionary/set membership or hashing**.
2. Validate each distinct accepted row spelling once in the existing immutable numeric key memo.
3. Add only validated native strings to the dedup set, then freeze and reserve `unique rows × foreign groups` against the existing one-million citation budget.
4. Only materialize credit/return evidence after *both* types pass reservation.

The exact private-input error remains `Cross-order review requires numeric source row citations`. Same-PO suppression, leading-zero citation spelling, numeric ordering, source-original immutability, typed references, local-first processing, audit provenance, Decimal money math and **human review** remain unchanged.

## Tests and evidence

- 12 new native `unittest` methods in `tests/test_procurement_foreign_hash_custody_r483.py`, importing the **actual suite module** on a checkout. They cover hostile `__hash__` objects on invoice/receipt, `str` subclasses, unhashable values, private paths and 5,000-digit labels, second-type invalidity, same-PO/unmatched suppression, deterministic valid citations, atomic budget, input immutability and 160 seeded two-type parity cases.
- CI step in `.github/workflows/desktop-source-evidence-r385.yml` runs the native tests under `python -W error` and `python -OO -W error` on both Ubuntu and Windows **when runners execute**.
- **Actually executed locally (Python 3.13.5):** an 8-method focused test suite against an isolated function reconstruction, standard mode **8/8 PASS**, optimized mode **8/8 PASS**; 160 seeded parity scenarios per mode. `py_compile` passed.
- **Baseline negative control:** restored the old pre-validation `frozenset` behavior in that isolated reconstruction; 3 targeted methods produced 3 failures plus 1 error (`exit=1`). Restoring the fix made all 3 pass.
- **Not executed:** the 12 newly committed native methods against the full byte-identical repository module; full ProcureGuard CSV integration suite; six-app matrix; any native Windows EXE/Defender/signed packaging or entitlement checks. Local reconstruction is not a substitute for repository integration.

## Release and unblock

The prior R482 workflows [six-engine source #43966599808](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43966599808) and [Windows build #43966599725](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43966599725) had four failed jobs before steps began (`steps=null`). GitHub check-run metadata indicates one annotation per job, but this connector cannot read the annotation URL. The runner/billing/root cause is **not established**.

**Smallest unblock:** repository administrator opens the GitHub Actions check failure details, inspects the annotation, Actions billing/usage and runner eligibility, and restores job step execution. Then run exact-R483 normal and optimized new tests, inherited 38-method ProcureGuard CSV integration suite and six-product regression, followed by actual Windows x64 binary smoke, Defender, accessibility, SHA256, and guarded premium distribution. QD independent review and explicit founder approval are mandatory before merge or publication.
