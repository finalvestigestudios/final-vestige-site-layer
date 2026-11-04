# R182 — Policy Delta Desk source-coordinate custody (DRAFT / HARD RELEASE HOLD)

Tracking: [Final Vestige Labs six-app suite #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Base: R181 draft PR #917, exact parent `05db02412e820ee0800bacb086bdbb36d57aa638`. The R182 branch targets **R181**, never `main`.

## Fixed correctness boundary

The local cross-script look-alike **navigation-only** helper formerly accepted any positive integer as a claimed physical policy line, including positions beyond the reader's 50,000-line input limit. A direct caller could also supply two different source texts with the *same* before or after line number, producing contradictory citations. Lists, tuples and dict subclasses with custom iteration/access were not all rejected before processing. The ordinary file comparer already constructs genuine line numbers; this sprint hardens the secondary evidence API against malformed or spoofed records without changing successful normal file comparisons.

`fvs_suite/policy_confusables.py` now enforces native `list` hunk collections, native `dict` hunks, native `list` source sides, native two-item `tuple` entries, native non-subclass `int` line numbers within `1..50000`, native `str` source text, and **unique line identifiers on each side**. If *either* side is malformed or duplicates a physical line, the entire hunk is excluded from supplemental cross-script pairing. Independently valid hunks remain navigable. Source lines longer than 4096 characters are still ignored only as candidates, so they do not suppress other eligible rows in the same otherwise valid hunk. Character cues remain limited to eight glyphs per line and sixteen pairs.

This is **not** an anti-fraud verdict or comprehensive confusables detector. The original byte fingerprints, actual source-owned unified diff, human review, and prior wording remain authoritative. The helper never echoes private policy text, performs network requests, edits originals, or decides compliance.

## Tests and exact evidence

- New synthetic tests: `tests/test_policy_confusable_source_custody_r182.py` — **38** methods. Blob SHA `2b35c4f34e8bd396de6c799682213ec2da7ad4af`.
- Changed helper: `fvs_suite/policy_confusables.py` — blob SHA `211b516d37d900b4682a13a5d4fea1dee6fbe0cc`.
- New strict runner: `scripts/safe_unittest_r182.py` — blob SHA `a28d0f58b0fb90656374b411a2f8338442258011`. Requires the exact named 38-method inventory, zero errors/failures/skips/unexpected successes; failing gate exit code on drift.
- Workflow: `.github/workflows/desktop-build.yml` contains mandatory R182 normal and `-OO` runs in **both** Ubuntu source-tests and Windows x64 build/test jobs.
- **Actually executed** against these exact three Git-blob-matched files in an isolated Linux Python 3.13.5 environment, using `PYTHONPATH=.`: `python scripts/safe_unittest_r182.py` → **PASS 38/38**, and `python -OO scripts/safe_unittest_r182.py` → **PASS 38/38**. Total **76/76** focused method executions, zero errors, failures or skips. Independent `unittest discover` in normal and optimized modes also passed with 38 tests per execution. Python source/test `compileall` passed.
- Local execution scope: **isolated helper**, not a complete repository checkout, not the inherited R180/R181 tests, not R178/R180 real-file integration, not Windows CI, not an executable build, and not real Windows accessibility/Defender evidence. Do not equate local test passes with a release gate.

## Mandatory acceptance before any release

1. Restore GitHub-hosted Actions runner allocation; rerun the unchanged exact R182 SHA on Ubuntu and Windows. Verify both normal and `-OO` R182 gates, all inherited regression/integration gates (including seven R178 and seven R180 real-file tests), six internal portable Windows x64 candidate builds, smoke, and provenance.
2. Obtain independent physical Windows 11 46-observation accessibility acceptance; genuine Defender/EDR evaluation; checksum/version/signing assurance; protected premium downloads/access controls; independent QD review and explicit founder approval.
3. Never merge this branch directly to production, change WordPress, publish untested EXEs, or expose GrantAudit/ProcureGuard premium files without access controls.

Next engineering priority: **unblock GitHub Actions runner allocation** (inspect run's top-level error banner, billing/usage allowance, account/repo Actions permissions and runner provisioning), then run all pending full-repository tests against the unchanged R182 head. Do not interpret pre-runner failures as test failures.
