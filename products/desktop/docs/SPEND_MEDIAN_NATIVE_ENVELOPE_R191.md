# R191 — SpendMap median direct-API numeric custody (DRAFT / QD HARD HOLD)

Tracking: [six-app issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
Scope: **SpendMap Lite** shared running-median helper only. No production, CMS,
financial input/report schema, signing, paid entitlement, download or EXE change.

## Reproduced against unchanged R190 source

- Original source Git blob: `3eab14a5efd119e905bebb38f0684db4e4c26bb0`.
- A `Decimal` subclass with an overridden `is_finite()` executed caller-owned
  Python code during `RunningDecimalMedian.add()` (observed `RuntimeError:
  private hook fired` in a local reproduction).
- `Decimal('1e81')` was accepted into the original heap even though this
  value is impossible for a bounded 200,000-row SpendMap monthly total.
  Arbitrarily large exponents could later create impractical midpoint
  contexts rather than a bounded review result.
- These are **direct-library-caller** risks; this does not establish that
  imported ordinary CSVs can produce those values.

## Proposed remediation

Reject subclassed `Decimal`, floats, non-Decimal objects, NaN and infinity
**before invoking untrusted value methods or mutating heap state**. Native
finite Decimals must have a coefficient of at most 80 digits and a stored
exponent in [-80, +80]. The envelope is intentionally wider than the
CSV/200k-row monetary domain; it preserves existing 70-digit historical
precision tests, half-cent midpoints, opposite signs and trailing-zero cases.
Original Decimal arithmetic, cent precision, data sources, provenance and
human-review-only anomaly semantics are unchanged.

All rejection messages are generic and do not repeat financial source values.
The median remains exact under hostile caller Decimal precision, exponent
limits and traps. Prior valid observations are not changed by rejection.

## Exact source / test custody and local reproducibility

- Engine: `products/desktop/fvs_suite/spend_median.py` — Git blob
  `6c81f0dd502b45cd31400612c934c28143b4e022`.
- New 25-method module:
  `products/desktop/tests/test_spend_median_native_envelope_r191.py` —
  Git blob `d3f9de2a394db3db0d0ec76e67b79dbd22eb4810`.
- Original and modified source + tests were compared with local Git
  `blob <size>\\0<bytes>` SHA-1 identities; source/test local hashes match
  the GitHub committed blob IDs above.
- Local Linux Python 3.13.5 (isolated exact-file-matched package):
  - `PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_spend_median_native_envelope_r191.py'`: **25/25 PASS**.
  - Same command with `python -OO`: **25/25 PASS**.
  - **50/50 total focused method executions**, 0 skips/errors/failures.
  - Both source and test files compiled successfully.
- Includes hostile subclasses, numeric envelopes, negative zero, 70-digit
  exact historical arithmetic, half-cents under Decimal traps, large
  opposite exponents, 24 permutations of a four-value history and 3,000
  deterministic median insertions.
- CI wiring: independent Ubuntu `source-tests` and Windows
  `windows-build` jobs each require both normal and `-OO` R191
  tests. Windows checks `$LASTEXITCODE` immediately after each invocation.

**Limits:** This is *not* execution of the whole repository's inherited
tests, the 14 outstanding Policy Delta real-file integrations, either
GitHub-hosted runner, a native Windows build, an EXE smoke test, or a physical
Win11 accessibility/Defender/EDR check. Full CI may reveal integration
regressions. Tests use synthetic numbers; no private financial data.

## Release hold / next highest-impact action

The preceding R190 hosted Actions run
[#41883923415](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41883923415)
completed FAILURE with two failed jobs and zero recorded executed
steps/runner IDs. Root cause has not been demonstrated; do not attribute
the failure to test code. Repository owner: inspect the run banner,
billing/usage allowance, enabled Actions permissions and hosted runner
provisioning; restore allocation, rerun unchanged R191 head, then complete
whole-suite/Policy Delta integration and all six private Windows x64 build
artifacts. Checksum, Defender/EDR, native accessibility, signing, protected
premium access, independent QD and founder release authorization all remain
**NOT VERIFIED**. Six products remain **UNRELEASED** and no downloadable
executables or unrestricted premium URLs may be published.
