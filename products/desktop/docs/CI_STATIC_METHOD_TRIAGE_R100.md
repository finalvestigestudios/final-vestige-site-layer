# R100 — privacy-safe failing test method identifiers

**Issue #73 | Draft HOLD | Based on R99 PR #394, not production main.**

## Why
R99 Actions shows nine assertion failures in six old test modules. Earlier module-only evidence
does not reveal which source-defined methods failed. Printing exception text, traceback,
subtest parameters or CSV values would expose financial/private test data.

## Implemented
- Child extracts *static* test_module.test_method labels via Python AST, only top-level classes and source-defined methods.
- No runtime test.id(), exception messages, subtest parameters or customer-derived labels are emitted.
- Maximum ten sorted labels, <=104 ASCII characters each; extra label count is recorded.
- Parent independently parses the source AST and refuses unallowlisted, malformed, repeated or unsorted methods.
- Legacy R98/R99 diagnostics remain valid; stderr stays discarded and total accepted stdout is bounded to 2,048 bytes.
- All complete-suite source tests, Python -OO parity, six engine smokes and fail-closed Windows packaging gates are unchanged.

## Reproduce from an actual checkout at the PR head

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_static_method_diagnostics_r100.py' -v
    PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_static_method_diagnostics_r100.py' -v
    python products/desktop/scripts/offline_source_gate.py

Ten synthetic-only tests cover source AST allowlisting; subtest privacy; normal and optimized
subprocess behavior; forged/unsourced labels; absent parent allowlist; malformed and private
method text; invalid counts/order; legacy compatibility; and deterministic method caps.

**No tests are claimed passing until runtime evidence is collected.** Keep actual traceback
and client fixture data inside the trusted checkout; never paste them in CI comments.

## Next
Use exact R100 CI method labels to identify and repair the nine real regressions without
deleting tests or loosening review/entitlement rules. Require green Linux/Windows normal
and -OO source tests and six smokes, then native Win11 x64 binary/PE/SHA/AV/accessibility,
premium-controlled distribution, independent QD and explicit founder approval.

**All six apps unreleased; no production/CMS write, public EXE, download URL, entitlement change or merge.**
