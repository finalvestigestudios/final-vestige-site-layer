# Labs R481 — foreign-offset source-row key reuse (internal / release HOLD)

Tracks [six-app issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
This increment is stacked only on draft **R480**. It is **not** a release or
permission to ship ProcureGuard Studio Pro, change live WordPress, or expose
premium binaries.

## Focused behavior

The ProcureGuard review-only foreign-offset resolver added in R479 and
preflighted per reference in R480 still called `_source_row_sort_key` again
for every affected PO/line during final evidence rendering. With one physical
original row linked from thirty foreign purchase orders, preflight performed
one numeric row validation and final rendering repeated that conversion
thirty times: **31 total validations** for one row.

R481 builds a `validated_row_keys` mapping once per distinct original
source-row spelling, shared across both credit and return offset types.
The mapping is populated during the existing global preflight, *before* any
cross-PO evidence is materialized. Final canonical sorting reads the cached
immutable `(int(row), len(row), row)` tuple instead of parsing each copy.
A local 30-target regression changes the expected validation count from
**31 to 1**; a 90-target, three-distinct-row case expects **3**, not 273.

This changes CPU work only. It never changes source rows, review identities,
sorted evidence, two-type isolation, same-PO suppression, budget reservations,
row redaction, source digests, exact Decimal money, payment authorization or
reviewer control. Worst-case expanded citation memory is still governed by
the inherited conservative one-million-citation budget; **no speedup in
wall-clock production workloads has been measured**.

## Proposed source and test gates

- `products/desktop/fvs_suite/procurement_cross_po_r471.py`: memoize validated
  original-row numeric keys across typed references and reuse for output.
- `products/desktop/tests/test_procurement_foreign_offset_fanout_r480.py`:
  update the inherited tracked-call expectation from 31 to 1, retaining all
  R480 functional assertions.
- `products/desktop/tests/test_procurement_foreign_row_key_cache_r481.py`:
  nine new native `unittest` methods for 90-group fanout, distinct-reference
  and cross-type reuse, overlapping target rows, local-original suppression,
  redacted later-type errors, shared budget, unresolved links, and 175 seeded
  independent two-stream oracle scenarios.
- `.github/workflows/desktop-source-evidence-r385.yml`: require R481's native
  tests on both hosted OS matrices under standard and `-OO -W error` Python.

## Executed evidence versus outstanding gates

**Executed offline (Linux):** An isolated manually reconstructed version
of the new foreign-offset resolver, not the byte-identical complete committed
GitHub module, passed **5/5 focused `unittest` methods with `-W error` and
5/5 with `-OO -W error`**. Compilation passed. These include **1,000
independent seeded parity scenarios in each mode** across both credit and
return streams, an exact/over citation-budget boundary, a redacted late-type
invalid row, and 90-group/one-row numeric-key reuse. The reconstruction is
not evidence of full engine, six-app integration, CI or a Windows build.

**Committed, not executed locally:** The nine-method real-module R481
test file, the inherited twelve-method R480 file (whose tracked-call
expectation changed), the sixteen-method R479 helper file, the four CSV
integration methods, the 38 ProcureGuard CSV methods and all six-app suites.
Native Windows x64 packaging, installed GUI/accessibility checks, Defender,
binary SHA256 and protected premium distribution remain unverified.

**Known pre-sprint CI blocker:** R480
[source evidence run #43948492008](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43948492008)
and [Windows internal build #43948492003](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43948492003)
failed with both jobs each reporting `steps=null`. This is not proof of a
code failure; precise account/runner root cause is unconfirmed. Verify R481's
own exact-head workflow runs before treating it as tested.

## Next highest-impact step

GitHub organization/repository administrator must inspect the Actions
failure banners and job annotations and verify billing limits, runner
eligibility, Actions restrictions and permission. Restore **actual job
steps**, then run the R481 standard/optimized source tests and all inherited
ProcureGuard + six-app native integration suites at the exact PR commit.
Only after native Windows x64 packaging/installation, virus scan,
checksums, accessibility, genuine premium gating, independent QD review
and explicit founder approval may any distribution be considered.

No merges, releases, website changes, premium files or public download links
are authorized by this sprint.
