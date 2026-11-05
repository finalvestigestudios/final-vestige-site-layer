# Final Vestige Labs R196 — native policy hunk-key custody

**Issue:** #73 · **Parent:** draft R195 PR #1003, commit `50a0e463f6f8120389fffc5b48558ada40f301e5` · **Release:** HARD HOLD.

## Scope and defect

Policy Delta Desk's direct `render_local_confusable_evidence` helper accepted
an **exact** Python dict with non-native field keys (objects, numbers, bytes,
`str` subclasses). The source-citation helper had hardened row/line values
but called `hunk.get(field)` before validating key types. This could admit
unsupported metadata into a source-owned evidence structure or involve custom
key comparison code during field lookup. The sibling canonical helper already
enforced native string keys.

R196 validates **every** hunk key with `type(key) is str` before looking up
either `removed_sources` or `added_sources`. Native string extras remain
allowed. A malformed hunk still produces no look-alike cue; separate, valid
hunks retain their historical behavior. No source files are modified.

## Reproducible tests (2026-11-04, Linux, Python 3.13.5)

Synthetic data only. New focused regression file:
`products/desktop/tests/test_policy_hunk_key_custody_r196.py`.

- Unmodified parent source Git blob: `4348d9bd59f2e9455fc2505270a71182386068d3`; **15 of 22 focused tests failed**, reproducing the missing key gate.
- Patched source Git blob: `0f89919bd07d48d1694e06f1035f501d1761eb08`.
- Focused test Git blob: `92231cea20a365946e73738abfb7ba7127f0e767`.
- Patched source: **22/22 normal** and **22/22 optimized (-OO)**, total **44/44 PASS**, no skipped cases; Python compilation PASS.
- Fixtures include colliding hostile keys, non-native extra metadata, `str` subclasses, no private-text echo, retained valid accessible Unicode name cues, stable hunk sorting, ambiguous duplicates, and cross-hunk coordinate collisions.
- Validation used an isolated local copy with byte-identical Git blobs; **not** a full repository run, native Windows test, or completed GitHub-hosted CI.

From repository root after checkout:

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_policy_hunk_key_custody_r196.py'
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_policy_hunk_key_custody_r196.py'
```

## Compliance, privacy and release gate

All policy results are textual navigation requiring human review, never legal
or compliance determinations. No telemetry, uploads, financial data mutation,
Decimal money-code changes, executable builds, or live distribution changes.
No premium files made public. Keep PR draft and stacked, not on `main`.
Retain independent QD and founder review and signed-off publishing gate.

**Next highest-impact step:** restore GitHub Actions Windows/Ubuntu runners
(the last inspected R195 run #41931277316 ended with two failed jobs and no
recorded test steps); then execute full inherited suite, finish Policy Delta's
remaining real-file integration matrix, and privately build, checksum, scan,
and smoke-test all six Windows x64 apps before any release.
