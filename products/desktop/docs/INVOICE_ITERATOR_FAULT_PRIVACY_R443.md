# R443 — Invoice Twin Scout source iterator privacy custody

Issue: #73. Scope: Invoice Twin Scout direct in-process candidate API, shared source-review contract. **Internal draft only; release_authorized=false**.

## Defect and correction

`candidate_pairs(records)` validates source rows and limits candidate counts, but an arbitrary caller-supplied iterable can fail while constructing its iterator or retrieving any item. The prior `for record in records` propagated arbitrary iterator exceptions. A hostile or faulty adapter could attach confidential transaction values, client names, or filesystem details to an `OSError`, `ValueError`, or `RuntimeError` that appeared in diagnostics; caller source material must not become a report or traceback message.

`fvs_suite.invoice_match._private_source_records` now owns iterator creation and individual `next()` calls. It translates ordinary external iterator faults into fixed-text `ValueError("Invoice source records could not be read")` **after exiting** the private exception handler, so the public exception's `__cause__` and `__context__` do not preserve the raw exception. Normal `StopIteration` remains successful termination; `KeyboardInterrupt` and `SystemExit` retain their interruption semantics. Pre-existing record shape, native Decimal/date/key validators, source-order canonicalization, 200,000-row ceiling, and 100,000-candidate fail-closed limit remain unchanged. No partial report is returned when an iterator fails after yielding valid rows.

This is an exception-boundary guarantee, not a promise that Python traceback frame locals or third-party adapters cannot themselves retain sensitive source data. Do not log source objects or traceback locals in production.

## Verification and limitations

Synthetic **local projection** on Linux CPython 3.13.5, containing the exact R443 helper text and 10 committed pure-helper regression methods, executed with `PYTHONPATH=.`:

- `python -W error -m unittest discover -s tests -p test_invoice_iterable_privacy_r443.py` — **10/10 PASS**
- `python -OO -W error -m unittest discover -s tests -p test_invoice_iterable_privacy_r443.py` — **10/10 PASS**
- `python -m compileall -q .` — PASS
- Controlled pre-fix `for` iteration exposed the synthetic private canary through its exception message on **3/3** error cases. This is a local reproduction of the vulnerable control-flow pattern, not an execution of the full pre-fix repository.

**Not executed locally:** the five committed full-module `test_invoice_iterable_integration_r443.py` methods, complete inherited invoice suites, or any native Windows checks. No complete checkout was available. The source-evidence workflow schedules both new modules plus inherited R67/R93 regressions under normal and `-OO` Python on Ubuntu and Windows; these are **scheduled test commands, not CI passes**.

## Acceptance and release hold

- Synthetic input adapters that raise private exceptions before/after valid records produce a generic error with no private Python exception chain; native record validation remains distinct.
- Valid source generators preserve result orientation, exact/near status, canonical source-row order and Decimal evidence.
- Owner must restore GitHub Actions runner execution, run exact-commit full-module checks, then verify real Windows x64 six-app builds, Defender, high-DPI/keyboard accessibility, release hashes and premium access controls.
- No signing key, premium executable, entitlement, download URL, website content, deployment, or payment/compliance approval is generated here.
- Independent QD review and explicit founder approval remain mandatory before merge or publication.
